#!/usr/bin/python

from crons.reservation import do_reservation


def test_reservation():
    game_day = "MONDAY"
    game_start_time = "21:30"
    game_duration = "90m"
    do_reservation(
        game_day=game_day,
        game_start_time=game_start_time,
        game_duration=game_duration
    )


if __name__ == "__main__":
    test_reservation()
