Imports:
sudo pip3 install adafruit-circuitpython-charlcd
pip install suntime
pip install twilio

Enable VNC - in raspi-config
Enable I2C ports - in raspi-config


Instructions to get code to Run at boot:
crontab -e
select nano as editor
add the following at the end of the file:
@reboot python /home/<user>/github/coop_controller/coop_controller.py > /home/<user>/github/coop_controller/cron.log 2>&1
@reboot $HOME/.venv/bin/python $HOME/coop_controller/coop_controller.py > $HOME/coop_controller/cron.log 2>&1



