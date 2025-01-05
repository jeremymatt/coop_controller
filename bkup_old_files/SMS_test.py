# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 12:16:55 2021

@author: jmatt
"""

import smtplib
import settings
carriers = {
	'att':    '@mms.att.net',
	'tmobile':' @tmomail.net',
	'verizon':  '@vtext.com',
	'sprint':   '@page.nextel.com'
}

def send(message):
        # Replace the number with your own, or consider using an argument\dict for multiple people.
	to_number = '{}{}'.format(settings.phone_number,carriers['att'])
	auth = (settings.email, settings.password)

	# Establish a secure session with gmail's outgoing SMTP server using your gmail account
	server = smtplib.SMTP( "smtp.gmail.com", 587 )
	server.starttls()
	server.login(auth[0], auth[1])

	# Send text message through SMS gateway of destination number
	server.sendmail( auth[0], to_number, message)
    
    
send('test message')


import smtplib
import settings
from email.message import EmailMessage

msg= EmailMessage()

my_address =settings.email    #sender address

app_generated_password = settings.password    # gmail generated password

# msg["Subject"] ="The Email Subject"   #email subject 

# msg["From"]= my_address      #sender address
msg["From"]= 'coop controller'      #sender address

msg["To"] = settings.phone_number     #reciver address

msg.set_content("This is the body of the email")   #message body

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    
    smtp.login(my_address,app_generated_password)    #login gmail account
    
    print("sending mail")
    smtp.send_message(msg)   #send message 
    print("mail has sent")