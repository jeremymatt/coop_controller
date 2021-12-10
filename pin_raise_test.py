# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 18:49:16 2021

@author: jmatt
"""

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIOs = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
         12, 13, 16, 17, 18, 19, 20, 21,
         22, 23, 24, 25, 26, 27]
#GPIOs = [5,6,12,13,16,19,20,21,26]
# Setup all GPIOs to input
for gpio in GPIOs:
    GPIO.setup(gpio, GPIO.OUT)
    
# Read state for each GPIO
for gpio in GPIOs:
    print("GPIO no " + str(gpio) + ": " + str(GPIO.input(gpio)))
    
# Cleanup all GPIOs - state will be different after that!
# GPIO.cleanup()