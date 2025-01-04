#!/bin/bash
sudo apt-get install virtualenv -y
virtualenv -q -p /usr/bin/python $HOME/.venv
source $HOME/.venv/bin/activate
pip install -r requirements.txt