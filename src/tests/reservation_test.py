#!/usr/bin/python

from crons.reservation import do_reservation


def test_reservation():
    game_day = "THURSDAY"
    game_start_time = "13:00"
    game_duration = "60m"
    do_reservation(
        game_day=game_day,
        game_start_time=game_start_time,
        game_duration=game_duration,
        disabled_for_testing=True
    )


if __name__ == "__main__":
    test_reservation()
