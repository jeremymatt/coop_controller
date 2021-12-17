#!/user/bin/env python

"""
Created on Fri Dec 10 11:34:53 2021

@author: jmatt
"""


with open('/home/pi/github/coop_controller/beans.txt', 'a') as file:
    file.write('Start of coop controller\n')

import datetime as dt
with open('/home/pi/github/coop_controller/beans.txt', 'a') as file:
    file.write('datetime imported\n')

import coop_functions as CF
with open('/home/pi/github/coop_controller/beans.txt', 'a') as file:
    file.write('coop functions imported\n')
    
import sys
with open('/home/pi/github/coop_controller/beans.txt', 'a') as file:
    file.write('sys imported\n')
    
import traceback
with open('/home/pi/github/coop_controller/beans.txt', 'a') as file:
    file.write('traceback imported\n')
    
    
import os
with open('/home/pi/github/coop_controller/beans.txt', 'a') as file:
    file.write('os imported\n')
    
import time
with open('/home/pi/github/coop_controller/beans.txt', 'a') as file:
    file.write('time imported\n')

# time.sleep(120)


with open('/home/pi/github/coop_controller/beans.txt', 'a') as file:
    file.write('Done inports\n')
    
    
controller = CF.coop_controller()
# controller.run()
try:
    controller.run()
except Exception as e:
    err_msg = str(e)
    
    with open(controller.logfile_name, 'a') as file:
        file.write('\nCONTROLLER CRASH TRACEBACK\n')
        traceback.print_exc(limit=None, file=file, chain=True)
    
    CF.send_crash_notification(controller.logfile_name)
    
        
    
    try:
        controller.print_state('CONTROLLER CRASHED WITH:\n  ERROR MESSAGE ==> {}\n\nState:\n'.format(err_msg))
    except:
        donothing = 1
        
    CF.restart()
        
        
        
    
