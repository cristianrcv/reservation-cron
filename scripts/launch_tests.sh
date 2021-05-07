#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export PYTHONPATH="${PYTHONPATH}:${SCRIPT_DIR}/../src/"
export PATH="${PATH}:${SCRIPT_DIR}/../chromedriver/"

python "${SCRIPT_DIR}/../src/tests/web_interactions_test.py"
