#!/bin/bash
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
	| sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
	&& echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
	| sudo tee /etc/apt/sources.list.d/ngrok.list \
	&& sudo apt update \
	&& sudo apt install ngrok

sudo apt-get install virtualenv -y
virtualenv -q -p /usr/bin/python $HOME/.venv
source $HOME/.venv/bin/activate
pip install -r requirements.txt
sudo sudo raspi-config nonint do_i2c 0