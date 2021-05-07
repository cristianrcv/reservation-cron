# !/usr/bin/python

import time

from selenium import webdriver

from utils.secret_loader import load_from_secret_file


class BrowserSessionManager:
    _WEB_ENDPOINT = load_from_secret_file("web_endpoint.txt")

    def __init__(self):
        self._browser = webdriver.Chrome()
        time.sleep(1.0)
        self._browser.get(BrowserSessionManager._WEB_ENDPOINT)
        time.sleep(2.0)

    def get_browser(self) -> webdriver.Chrome:
        return self._browser

    def navigate(self, element_id: str) -> None:
        button = self._browser.find_element_by_id(element_id)
        button.click()
        time.sleep(1.0)

    def login(self) -> None:
        username_key = load_from_secret_file("web_username.txt")
        username = self._browser.find_element_by_id("ctl00_ContentPlaceHolderContenido_Login1_UserName")
        username.send_keys(username_key)

        password_key = load_from_secret_file("web_password.txt")
        password = self._browser.find_element_by_id("ctl00_ContentPlaceHolderContenido_Login1_Password")
        password.send_keys(password_key)

        time.sleep(1.0)

        login_button = self._browser.find_element_by_id("ctl00_ContentPlaceHolderContenido_Login1_LoginButton")
        login_button.click()

        time.sleep(3.0)

    def quit(self) -> None:
        self._browser.quit()
