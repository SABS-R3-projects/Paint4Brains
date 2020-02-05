#!/bin/bash

python3 -m venv env
source env/bin/activate
pip install -e .
pip install -q -r requirements.txt