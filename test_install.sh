#!/bin/bash
sudo apt-get install virtualenv
virtualenv -q -p /usr/bin/python3.5 ~/.venv
source ~/.venv/bin/activate
pip install -r requirements.txt