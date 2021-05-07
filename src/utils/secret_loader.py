#!/usr/bin/python

import logging
import os

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
_CWD = os.path.dirname(os.path.realpath(__file__))


def load_from_secret_file(file_name: str) -> str:
    file_path = str(_CWD) + "/../../secrets/" + file_name
    _LOGGER.info("Loading secret from " + str(file_path))
    with open(file_path, mode='r') as f:
        return f.read()
