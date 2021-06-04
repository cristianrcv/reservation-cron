# !/usr/bin/python

import logging
import time
from typing import Optional

from utils.browser_session_manager import BrowserSessionManager

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
_SLOW_TYPE_SLEEP_TIME = 1
_HOUR_TO_INDEX = {
    "8": 1,
    "9": 2,
    "10": 3,
    "11": 4,
    "12": 5,
    "13": 6,
    "14": 7,
    "15": 8,
    "16": 9,
    "17": 10,
    "18": 11,
    "19": 12,
    "20": 13,
    "21": 14,
    "22": 15
}
_MINUTE_TO_INDEX = {
    "00": 2,
    "30": 3
}
_COURT_PRIORITY = [2, 4, 1, 3, 6, 8, 10, 5, 7, 9]
_DURATION_TO_CODE = {
    "60m": 1,
    "90m": 2,
    "120m": 3
}
_CSS_DURATION_TO_CODE = {
    "60' Minutos": 1,
    "90' Minutos": 2,
}


#
# HELPER METHODS
#
def _book(browser_session_manager: BrowserSessionManager,
          game_day: str,
          game_start_time: str,
          game_duration: str,
          disabled_for_testing: bool) -> None:
    # Move to reservations tab
    browser_session_manager.navigate(
        "ctl00_ctl00_ContentPlaceHolderContenido_WUCMenuLateralIzquierdaIntranet_LiBuscadorReservas"
    )

    # Move to game_day (no need to check since cron is being executed 6 days before)
    browser = browser_session_manager.get_browser()
    next_button = browser.find_element_by_xpath("//*[@id='tablaReserva']/div[2]/div[2]/div[1]/div[3]/input[3]")
    for _ in range(6):
        next_button.click()
        time.sleep(_SLOW_TYPE_SLEEP_TIME)

    # Select game_start_time
    game_hour, game_minute = game_start_time.split(":")
    game_hour_index = _HOUR_TO_INDEX[game_hour]
    game_minute_index = _MINUTE_TO_INDEX[game_minute]

    i = 0
    reservation_done = False
    court = None
    while i < len(_COURT_PRIORITY) and not reservation_done:
        court = _COURT_PRIORITY[i]
        game_day_css_id = "#CuerpoTabla>g:nth-child({})>g:nth-child({})>rect:nth-child({})".format(
            game_hour_index,
            court,
            game_minute_index
        )
        try:
            slot_button = browser.find_element_by_css_selector(game_day_css_id)
            slot_button.click()
            time.sleep(_SLOW_TYPE_SLEEP_TIME)
            reservation_done = True
        except Exception:
            _LOGGER.debug("WARN: Cannot make reservation at " + str(court) + ". Retrying...")
            i += 1
            reservation_done = False

    if not reservation_done:
        raise Exception("ERROR: There is not any timeslot available for your reservation")

    # Select game_duration
    duration_code = _DURATION_TO_CODE[game_duration]
    available_time_buttons = browser.find_elements_by_xpath("//*[@id='groupButtons']/*[name()='g']")
    available_duration_codes = [_CSS_DURATION_TO_CODE[b.text.strip()] for b in available_time_buttons]
    duration_button = available_time_buttons[available_duration_codes.index(duration_code)]
    duration_button.click()
    time.sleep(_SLOW_TYPE_SLEEP_TIME)

    # Make reservation
    browser_session_manager.navigate(
        "ctl00_ContentPlaceHolderContenido_ButtonPagoSaldo"
    )
    if not disabled_for_testing:
        browser_session_manager.navigate(
            "ctl00_ContentPlaceHolderContenido_ButtonConfirmar"
        )

    # Log success
    _LOGGER.info(
        "Reservation: GameDay = %s, GameStartTime = %s, GameDuration = %s, Court = %s",
        game_day,
        game_start_time,
        game_duration,
        court
    )


#
# MAIN METHOD
#
def do_reservation(
        game_day: str,
        game_start_time: str,
        game_duration: str,
        disabled_for_testing: Optional[bool] = False) -> None:
    _LOGGER.info(
        "Making reservation for game_day=%s, game_start_time=%s, game_duration=%s",
        game_day,
        game_start_time,
        game_duration
    )

    try:
        browser_session_manager = BrowserSessionManager()
        try:
            browser_session_manager.login()
            _book(browser_session_manager, game_day, game_start_time, game_duration, disabled_for_testing)
        except Exception as e:
            _LOGGER.error("ERROR: Internal error while performing reservation")
            _LOGGER.error(e)
            raise e
        finally:
            browser_session_manager.quit()
        _LOGGER.info("Reservation DONE")
    except Exception:
        _LOGGER.error("ERROR: Reservation failed")
