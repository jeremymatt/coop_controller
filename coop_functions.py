# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 08:43:37 2021

@author: jmatt
"""

import datetime as dt
from suntime import Sun, SunTimeException


import smtplib
import settings
from email.message import EmailMessage



class coop_controller:
    
    def __init__(self):
        self.get_cur_time
        self.cur_day = self.cur_day.day
            
        
        
    def init_pins(self):
        
        
    def get_cur_time(self):
        self.cur_time = dt.datetime.now(dt.timezone.utc)
    
    def get_sunrise_sunset(self):
        sun = Sun(settings.latitude, settings.longitude)
        self.today_sr = sun.get_sunrise_time(self.cur_time)
        self.today_ss = sun.get_sunset_time(self.cur_time)
        
        self.close_time = self.today_ss + dt.timedelta(minutes=settings.wait_after_sunset)
        
        
    
    
    def send_notification(message):
        
        msg= EmailMessage()
        
        app_generated_password = settings.password    # gmail generated password
        msg["From"]= 'coop controller'      #sender address
        
        msg["To"] = settings.phone_number     #reciver address
        
        msg.set_content(message)   #message body
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            
            smtp.login(my_address,app_generated_password)    #login gmail account
            
            print("sending mail")
            smtp.send_message(msg)   #send message 
            print("mail has sent")