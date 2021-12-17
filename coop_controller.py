# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 11:34:53 2021

@author: jmatt
"""

import datetime as dt
import coop_functions as CF
import sys
import traceback
import os
import time

# time.sleep(120)


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
        
        
        
    
