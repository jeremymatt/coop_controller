# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 08:43:37 2021

@author: jmatt
"""

import datetime as dt
t = dt.datetime.utcnow()


import smtplib
import settings
from email.message import EmailMessage


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