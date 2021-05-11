#!/usr/bin/python

import logging

import schedule

from crons.reservation import do_reservation
from utils.week_days_manager import compute_run_day

#
# Enable logging
#
logging.basicConfig(
    format="[%(levelname)s][%(asctime)s - %(name)s] %(message)s",
    level=logging.DEBUG
)

#
# STATIC ATTRIBUTES
#
_LOGGER = logging.getLogger(__name__)
_DAYS_TO_JOB = {
    "monday": schedule.every().monday,
    "tuesday": schedule.every().tuesday,
    "wednesday": schedule.every().wednesday,
    "thursday": schedule.every().thursday,
    "friday": schedule.every().friday,
    "saturday": schedule.every().saturday,
    "sunday": schedule.every().sunday
}


class CronInteractions:

    def __init__(self):
        self._active_crons = []

    def get_active_crons(self) -> []:
        res = []
        for job_info in self._active_crons:
            exportable_job_info = (job_info[0], job_info[2], job_info[3])
            res.append(exportable_job_info)
        return res

    def get_num_active_crons(self) -> int:
        return len(self._active_crons)

    def clear(self) -> None:
        try:
            for job_id in range(self.get_num_active_crons()):
                schedule.cancel_job(self._active_crons[job_id][4])
            self._active_crons.clear()
            _LOGGER.debug("All reservation crons erased")
        except Exception as e:
            _LOGGER.error("Internal error while clearing all reservation crons")
            _LOGGER.error(e)

    def cron_create(self, game_day: str, game_start_time: str, game_duration: str) -> None:
        try:
            run_day = compute_run_day(game_day)

            job = _DAYS_TO_JOB[run_day].at("00:01").do(
                do_reservation,
                game_day=game_day,
                game_start_time=game_start_time,
                game_duration=game_duration
            )

            job_info = (run_day, game_day, game_start_time, game_duration, job)
            self._active_crons.append(job_info)

            _LOGGER.debug(
                "Reservation Cron created: GameDay = %s, GameStartTime = %s, GameDuration = %s",
                game_day,
                game_start_time,
                game_duration
            )
        except Exception as e:
            _LOGGER.error("Internal error while creating reservation cron")
            _LOGGER.error(e)
            raise e

    def cron_delete(self, job_id: int) -> None:
        try:
            if job_id < 0 or job_id >= len(self._active_crons):
                raise Exception("ERROR: Invalid cron id to delete")

            schedule.cancel_job(self._active_crons[job_id][4])
            self._active_crons.pop(job_id)

            _LOGGER.debug(
                "Reservation Cron with id = %s erased",
                job_id
            )
        except Exception as e:
            _LOGGER.error("Internal error while deleting reservation cron")
            _LOGGER.error(e)
            raise e
