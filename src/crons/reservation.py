# !/usr/bin/python

import logging
import time

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
LOGGER = logging.getLogger(__name__)
SLOW_TYPE_SLEEP_TIME = 0.2


#
# HELPER METHODS
#
def _book(browser_session_manager: BrowserSessionManager, game_day: str, game_start_time: str,
          game_duration: str) -> None:
    # Move to reservations tab
    browser_session_manager.navigate(
        "ctl00_ctl00_ContentPlaceHolderContenido_WUCMenuLateralIzquierdaIntranet_LiBuscadorReservas"
    )

    # Move to game_day (no need to check since cron is being executed 6 days before)
    browser = browser_session_manager.get_browser()
    next_button = browser.find_element_by_xpath("//*[@id='tablaReserva']/div[2]/div[1]/div[3]/input[3]")
    for _ in range(6):
        next_button.click()
        time.sleep(SLOW_TYPE_SLEEP_TIME)

    # Select game_start_time
    # TODO: Select game start time

    # Select game_duration
    # TODO: Select game duration

    # Make reservation
    browser_session_manager.navigate(
        "ctl00_ContentPlaceHolderContenido_ButtonPagoSaldo"
    )


#
# MAIN METHOD
#
def do_reservation(game_day: str, game_start_time: str, game_duration: str) -> None:
    LOGGER.info(
        "Making reservation for game_day=%s, game_start_time=%s, game_duration=%s",
        game_day,
        game_start_time,
        game_duration
    )

    browser_session_manager = BrowserSessionManager()
    _book(browser_session_manager, game_day, game_start_time, game_duration)
    browser_session_manager.quit()

    LOGGER.info("Reservation DONE")
