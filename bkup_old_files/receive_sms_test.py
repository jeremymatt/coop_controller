# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 19:21:06 2021

@author: jmatt
"""

from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    
    # Use this data in your application logic
    from_number = request.form['From']
    to_number = request.form['To']
    body = request.form['Body']

    # Start our TwiML response
    resp = MessagingResponse()

    # Add a message
    resp.message("Hey {}, you said: {}\nThe Robots are coming! Head for the hills!".format(from_number,body))

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)