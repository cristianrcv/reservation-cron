#!/usr/bin/python

import schedule

from crons.reservation import do_reservation
from utils.week_days_manager import compute_run_day


class CronInteractions:
    DAYS_TO_JOB = {
        "monday": schedule.every().monday,
        "tuesday": schedule.every().tuesday,
        "wednesday": schedule.every().wednesday,
        "thursday": schedule.every().thursday,
        "friday": schedule.every().friday,
        "saturday": schedule.every().saturday,
        "sunday": schedule.every().sunday
    }

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
        for job_id in range(self.get_num_active_crons()):
            schedule.cancel_job(self._active_crons[job_id][4])
        self._active_crons.clear()

    def cron_create(self, game_day: str, game_start_time: str, game_duration: str) -> None:
        run_day = compute_run_day(game_day)

        job = CronInteractions.DAYS_TO_JOB[run_day].at("00:01").do(
            do_reservation,
            game_day=game_day,
            game_start_time=game_start_time,
            game_duration=game_duration
        )

        job_info = (run_day, game_day, game_start_time, game_duration, job)
        self._active_crons.append(job_info)

    def cron_delete(self, job_id: int) -> None:
        if job_id < 0 or job_id >= len(self._active_crons):
            raise Exception("ERROR: Invalid cron id to delete")

        schedule.cancel_job(self._active_crons[job_id][4])
        self._active_crons.pop(job_id)
