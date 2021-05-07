#!/usr/bin/python

from bots.telegram.web_interactions import get_all_reservations
from bots.telegram.web_interactions import get_balance


def test_get_balance():
    balance = get_balance()
    print("CURRENT BALANCE: " + str(balance))


def test_get_reservations():
    reservations = get_all_reservations()
    print("RESERVATIONS: " + str(reservations))


if __name__ == "__main__":
    test_get_balance()
    test_get_reservations()
