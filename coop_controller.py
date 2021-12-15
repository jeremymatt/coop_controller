# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 11:34:53 2021

@author: jmatt
"""

import datetime as dt
import coop_functions as CF
import sys


dt = dt.datetime.now()
y = dt.year
m = str(dt.month).zfill(2)
d = str(dt.day).zfill(2)
h = str(dt.hour).zfill(2)
m = str(dt.minute).zfill(2)
s = str(dt.second).zfill(2)
# sys.stdout = open('{}-{}-{}_{}-{}-{}_log.txt'.format(y,m,d,h,m,s), 'w')

controller = CF.coop_controller()
# controller.run()
try:
    controller.run()
except Exception as e:
    CF.send_crash_notification()
    try:
        controller.print_state('CONTROLLER CRASHED WITH ERROR MESSAGE\n{}\nState:\n'.format(str(e)))
    except:
        donothing = 1
        
    
