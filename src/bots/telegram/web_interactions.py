#!/usr/bin/python

import logging

from bs4 import BeautifulSoup
from selenium import webdriver

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


#
# HELPER METHODS
#

def _navigate_intranet(browser_session_manager: BrowserSessionManager) -> None:
    browser_session_manager.navigate(
        "ctl00_ctl00_LinkButtonAcessoIntranet"
    )


def _navigate_balance_control(browser_session_manager: BrowserSessionManager) -> None:
    browser_session_manager.navigate(
        "ctl00_ctl00_ContentPlaceHolderContenido_WUCMenuLateralIzquierdaIntranet_LabelMenuControlSaldo"
    )


def _navigate_reservations(browser_session_manager: BrowserSessionManager) -> None:
    browser_session_manager.navigate(
        "ctl00_ctl00_ContentPlaceHolderContenido_WUCMenuLateralIzquierdaIntranet_LabelMenuReservas"
    )


def _get_reservations(browser: webdriver.Chrome) -> list:  # (day, start_time, end_time, field)
    cell = browser.find_element_by_id(
        "ctl00_ctl00_ContentPlaceHolderContenido_ContentPlaceHolderContenido_GridView1"
    )
    reservations_html_table = cell.get_attribute("innerHTML")
    soup = BeautifulSoup(reservations_html_table)
    reservations = []
    for row in soup.find_all("tr")[1:]:
        td_entries = row.find_all("td")
        game_day = _format_game_day(td_entries[1].renderContents())
        game_start_time, game_end_time = _format_times_values(td_entries[2].renderContents())
        game_field = _format_field_value(td_entries[3].renderContents())
        reservations.append((game_day, game_start_time, game_end_time, game_field))

    return reservations


def _format_game_day(raw_input: bytes) -> str:
    game_day = str(raw_input)
    game_day = game_day[2:-1]  # erase b' and '
    game_day = game_day.strip()
    return game_day


def _format_times_values(raw_input: bytes) -> (str, str):
    times = str(raw_input)
    times = times[2:-1]  # erase b' and '
    times = times.strip()
    game_start_time, game_end_time = times.split("-")
    game_start_time = str(game_start_time).strip()
    game_end_time = str(game_end_time).strip()
    return game_start_time, game_end_time


def _format_field_value(raw_input: bytes) -> str:
    field = str(raw_input)
    field = field[2:-1]  # erase b' and '
    field = field.replace("Videopista", "")
    field = field.replace("- UnoPadel", "")
    field = field.strip()
    return field


def _get_balance(browser: webdriver.Chrome) -> float:
    cell = browser.find_element_by_id(
        "ctl00_ctl00_ContentPlaceHolderContenido_ContentPlaceHolderContenido_GridViewListado_ctl02_LabelSaldoPosterior"
    )
    balance = cell.get_attribute("innerHTML")
    balance = balance.strip().replace(",", ".")
    balance = float(balance)

    return balance


#
# PUBLIC METHODS
#
def get_all_reservations() -> list:  # (day, start_time, end_time, field)
    _LOGGER.debug("Retrieving reservations")

    browser_session_manager = BrowserSessionManager()
    reservations = []
    try:
        browser_session_manager.login()

        _navigate_intranet(browser_session_manager)
        _navigate_reservations(browser_session_manager)
        reservations = _get_reservations(browser_session_manager.get_browser())
    except Exception as e:
        _LOGGER.error("ERROR: Cannot retrieve reservations")
        _LOGGER.error(e)
    finally:
        browser_session_manager.quit()
        _LOGGER.debug("Retrieving reservation DONE")

    return reservations


def get_balance() -> float:
    _LOGGER.debug("Retrieving balance")

    browser_session_manager = BrowserSessionManager()
    balance = None
    try:
        browser_session_manager.login()

        _navigate_intranet(browser_session_manager)
        _navigate_balance_control(browser_session_manager)
        balance = _get_balance(browser_session_manager.get_browser())
    except Exception as e:
        _LOGGER.error("ERROR: Cannot retrieve reservations")
        _LOGGER.error(e)
    finally:
        browser_session_manager.quit()
        _LOGGER.debug("Retrieving balance DONE")

    return balance
