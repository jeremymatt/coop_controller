# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 12:14:26 2021

@author: jmatt
"""

import os
path_to_repo = os.path.join(os.path.expanduser('~'),'coop_controller')

VERBOSE = False

phone_numbers = {
    'name_1':'+99999999999', # for US numbers: +1{area_code}{7-digit number}
    'name_2':'+99999999999'}


ngrok_static_url = 'knowing-zebra-namely.ngrok-free.app' # your static NGROK URL
port = 8000

email = 'from_email@provider.com'
to_email = 'to_email@provider.com'
password = 'email_provider_password'

account_sid = '' #Twilio account SID
auth_token = '' #Twilio auth token

wait_after_sunset = 45 #minutes
expected_door_travel_time = 40 #seconds
extra_door_travel = 0.5 #seconds
door_lock_travel = 0 #seconds
screen_on_time = 30 #seconds
restart_daily = True #flag to reset pi at midnight every day
notify_lights = True #true = send notifications when lights turn on/off

#Location for determining sunrise/sunset times
lat_degrees =       #integer value
lat_mins =          #integer value
lat_seconds =       #Float value
lat_dir = ""        #N or S

lon_degrees =       #integer value
lon_mins =          #integer value
lon_seconds =       #Float value
lon_dir = ""        #E or W

latitude = (lat_degrees,lat_mins,lat_seconds,lat_dir)
mult = 1
if latitude[3] =='S':
    mult = -1
latitude = mult*(latitude[0]+latitude[1]/60+latitude[2]/3600)
    
longitude = (lon_degrees,lon_mins,lon_seconds,lon_dir) 
mult = 1
if longitude[3] =='W':
    mult = -1
longitude = mult*(longitude[0]+longitude[1]/60+longitude[2]/3600)
