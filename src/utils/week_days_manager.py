#!/usr/bin/python

_NUM_TO_DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def compute_run_day(game_day: str) -> str:
    game_day = game_day.lower()
    if game_day not in _NUM_TO_DAYS:
        raise Exception("ERROR: Invalid game_day")

    game_day_int = _NUM_TO_DAYS.index(game_day)
    run_day_int = (game_day_int + 1) % 7
    return _NUM_TO_DAYS[run_day_int]
