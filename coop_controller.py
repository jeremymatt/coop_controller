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


controller = CF.coop_controller()
# controller.run()
try:
    controller.run()
except Exception as e:
    err_msg = str(e)
    CF.send_crash_notification()
    
    '''
    y,mo,d,h,m,s = CF.get_datetime_parts()
    cd = os.getcwd()
    crash_report_dir = os.path.join(cd,'CRASH_REPORT')
    if not os.path.isdir(crash_report_dir):
        os.makedirs(crash_report_dir)
    crash_report_fn = os.path.join(crash_report_dir,'Exec-traceback_{}-{}-{}_{}:{}:{}.txt'.format(y,mo,d,h,m,s))
    with open(crash_report_fn,'w') as file:
        traceback.print_exc(limit=None, file=file, chain=True)
        '''
        
    
    try:
        controller.print_state('CONTROLLER CRASHED WITH:\n  ERROR MESSAGE ==> {}\n\nState:\n'.format(err_msg))
    except:
        donothing = 1
        
    with open(controller.logfile_name, 'a') as file:
        file.write('\n')
        traceback.print_exc(limit=None, file=file, chain=True)
        
        
    
