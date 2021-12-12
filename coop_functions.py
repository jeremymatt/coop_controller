# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 08:43:37 2021

@author: jmatt
"""

import datetime as dt
import time
from suntime import Sun, SunTimeException


import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd


import smtplib
import settings
from email.message import EmailMessage



class coop_controller:
    
    def __init__(self):
        self.get_cur_time()
        self.get_sunrise_sunset()
        self.init_pins()
        self.init_flags()
        self.init_button_menu()
        self.init_display()
        
        
        
    def run(self):
        while True:
            self.get_cur_time()
            self.check_times()
            self.check_buttons()
            
            
            
            
            self.check_display_status()
     
    def init_button_menu(self):
        self.button_menu = {}
        menu = -1
        sub_menu = False
        self.button_menu[menu] = {}
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = None
        self.button_menu[menu][sub_menu]['select'] = None
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = self.next_menu
        self.button_menu[menu][sub_menu]['down'] = self.prev_menu
        
        menu = 0
        sub_menu = False
        self.button_menu[menu] = {}
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = self.disp_current_time
        self.button_menu[menu][sub_menu]['select'] = None
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = self.next_menu
        self.button_menu[menu][sub_menu]['down'] = self.prev_menu
        
        menu = 1
        sub_menu = False
        self.button_menu[menu] = {}
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = self.disp_door_times
        self.button_menu[menu][sub_menu]['select'] = self.enter_submenu
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = self.next_menu
        self.button_menu[menu][sub_menu]['down'] = self.prev_menu
        
        menu = 1
        sub_menu = True
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = self.disp_light_times
        self.button_menu[menu][sub_menu]['select'] = self.exit_submenu
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = self.next_menu
        self.button_menu[menu][sub_menu]['down'] = self.prev_menu
        
        menu = 2
        sub_menu = False
        self.button_menu[menu] = {}
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = 'Override door'
        self.button_menu[menu][sub_menu]['select'] = self.enter_submenu
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = self.next_menu
        self.button_menu[menu][sub_menu]['down'] = self.prev_menu
        
        menu = 2
        sub_menu = True
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = 'Override door\nUD:op/cls,LR:stp'
        self.button_menu[menu][sub_menu]['select'] = self.exit_submenu
        self.button_menu[menu][sub_menu]['left'] = self.door_stop
        self.button_menu[menu][sub_menu]['right'] = self.door_stop
        self.button_menu[menu][sub_menu]['up'] = self.door_raise
        self.button_menu[menu][sub_menu]['down'] = self.door_lower
        
        menu = 3
        sub_menu = False
        self.button_menu[menu] = {}
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = 'Override light'
        self.button_menu[menu][sub_menu]['select'] = self.enter_submenu
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = self.next_menu
        self.button_menu[menu][sub_menu]['down'] = self.prev_menu
        
        menu = 3
        sub_menu = True
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = 'Override light\nUD:on/off'
        self.button_menu[menu][sub_menu]['select'] = self.enter_submenu
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = self.light_on
        self.button_menu[menu][sub_menu]['down'] = self.light_off
            
    def check_buttons(self):
        
        if self.lcd.left_button:
            print('left')
            print('cur_menu: {}, submenu: {}'.format(self.cur_menu,self.in_sub_menu))
            self.do_button('left')
        
        elif self.lcd.up_button:
            print('up')
            print('cur_menu: {}, submenu: {}'.format(self.cur_menu,self.in_sub_menu))
            self.do_button('up')

        elif self.lcd.down_button:
            print('down')
            print('cur_menu: {}, submenu: {}'.format(self.cur_menu,self.in_sub_menu))
            self.do_button('down')

        elif self.lcd.right_button:
            print('right')
            print('cur_menu: {}, submenu: {}'.format(self.cur_menu,self.in_sub_menu))
            self.do_button('right')

        elif self.lcd.select_button:
            print('select')
            print('cur_menu: {}, submenu: {}'.format(self.cur_menu,self.in_sub_menu))
            self.do_button('select')
            
        
    def enter_submenu(self):
        self.in_sub_menu = True
        
    def exit_submenu(self):
        self.in_sub_menu = False
        
    def do_button(self,button):
        if self.button_menu[self.cur_menu][self.in_sub_menu][button] != None:
            self.display_off_time = self.cur_time + dt.timedelta(seconds=settings.screen_on_time)
            if not self.display_is_on:
                self.display_on()
            
            self.button_menu[self.cur_menu][self.in_sub_menu][button]()
            
            self.display_message = self.button_menu[self.cur_menu][self.in_sub_menu]['msg']
            print('processed button {}'.format(button))
            print('cur_menu: {}, submenu: {}'.format(self.cur_menu,self.in_sub_menu))
        else:
            print('inactive button')
            
    def update_display(self):
        if self.display_is_on:    
            if type(self.display_message) == str:
                msg = self.display_message
            else:
                msg = self.display_message()
            self.lcd.clear()
            self.lcd.message = msg
        
            
    def door_stop(self):
        GPIO.output(self.pins['door_raise'], GPIO.LOW)
        GPIO.output(self.pins['door_lower'], GPIO.LOW)
        self.door_is_opening = False
        self.door_is_closing = False
        
    def door_raise(self):
        GPIO.output(self.pins['door_lower'], GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(self.pins['door_raise'], GPIO.HIGH)
        self.door_is_opening = True
        self.door_is_closing = False
        
    def door_lower(self):
        GPIO.output(self.pins['door_raise'], GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(self.pins['door_lower'], GPIO.HIGH)
        self.door_is_opening = False
        self.door_is_closing = True
        
        
    def light_on(self):
        GPIO.output(self.pins['light'], GPIO.HIGH)
        self.light_is_on = True
        
    def light_off(self):
        GPIO.output(self.pins['light'], GPIO.LOW)
        self.light_is_on = True
        
            
    def next_menu(self):
        self.cur_menu +=1
        self.cur_menu %=max(self.button_menu.keys())
        
    def prev_menu(self):
        self.cur_menu -= 1
        if self.cur_menu < 0:
            self.cur_menu = max(self.button_menu.keys())
            
    def disp_current_time(self):
        string,parts = self.get_datetime_string(self.cur_time)
        msg = 'Current Time:\n{}'.format(string)
        return msg
        
    def disp_door_times(self):
        string,parts = self.get_datetime_string(self.sunrise)
        month,day,hour,minute,second = parts
        l1 = 'Door=>Open {}:{}'.format(hour,minute)
        string,parts = self.get_datetime_string(self.close_time)
        month,day,hour,minute,second = parts
        l2 = '     Close {}:{}'.format(hour,minute)
        msg = '{}\n{}'.format(l1,l2)
        return msg
        
    def disp_light_times(self):
        string,parts = self.get_datetime_string(self.sunrise)
        month,day,hour,minute,second = parts
        l1 = 'Light=>On {}:{}'.format(hour,minute)
        string,parts = self.get_datetime_string(self.sunset)
        month,day,hour,minute,second = parts
        l2 = '      Off {}:{}'.format(hour,minute)
        msg = '{}\n{}'.format(l1,l2)
        return msg
        
    def get_datetime_string(self,dto):
        
        dto = dto.replace(tzinfo=dt.timezone.utc).astimezone(tz=None)
        month = str(dto.month).zfill(2)
        day = str(dto.day).zfill(2)
        hour = str(dto.hour).zfill(2)
        minute = str(dto.minute).zfill(2)
        second = str(dto.second).zfill(2)
        
        string = '{}-{} {}:{}:{}'.format(month,day,hour,minute,second)
        parts = (month,day,hour,minute,second)
        return string,parts       
            
    def check_times(self):
        self.daytime = (self.cur_time>self.sunrise) & (self.cur_time<self.close_time)
        self.display_time_exceeded = self.cur_time>self.display_off_time
        
            
    def check_display_status(self):
        if self.display_time_exceeded & self.display_is_on:
            self.display_off()
        
        
    def init_display(self):
        
        lcd_columns = 16
        lcd_rows = 2
        i2c = busio.I2C(board.SCL, board.SDA)
        self.lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
        self.display_on()
        self.display_off_time = self.cur_time + dt.timedelta(seconds=10)
        self.display_message = 'Welcome to the\nJungle!'
        
    
    def display_on(self):
        self.display_is_on = True
        self.lcd.color = [100, 0, 0]
        
    def display_off(self):
        self.display_is_on = False
        self.cur_menu = -1
        self.lcd.clear()
        self.display_message = 'None'
        self.lcd.color = [0, 0, 0]
    
    
    def init_flags(self):
        self.cur_day = self.cur_time.day
        self.light_is_on = None
        self.door_is_open = None
        self.door_is_opening = False
        self.door_is_closing = False
        self.door_state_override = None #none, open, close
        self.light_state_override = None #none, on, off
        self.new_day = False
        self.door_move_start_time = None
        self.cur_menu = -1
        self.in_sub_menu = False
        self.door_travel_time = dt.timedelta(seconds = settings.expected_door_travel_time)
        
       
    def init_pins(self):
        
        outputs = [13,20,21]
        for output in outputs:
            GPIO.setup(output,GPIO.OUT)
            GPIO.output(output, GPIO.LOW)        
        
        inputs = [16,19]
        for inpt in inputs:
            GPIO.setup(inpt,GPIO.IN)
            
        self.pins = {
            'light':13,
            'door_raise':20,
            'door_lower':21,
            'door_closed':16,
            'door_open':19}
        
    def get_cur_time(self):
        self.cur_time = dt.datetime.now(dt.timezone.utc)
    
    def get_sunrise_sunset(self):
        sun = Sun(settings.latitude, settings.longitude)
        self.sunrise = sun.get_sunrise_time(self.cur_time)
        self.sunset = sun.get_sunset_time(self.cur_time)
        
        self.close_time = self.sunset + dt.timedelta(minutes=settings.wait_after_sunset)
        
        
    def send_notification(self,message):
        
        msg= EmailMessage()
        my_address = settings.email
        app_generated_password = settings.password    # gmail generated password
        msg["From"]= 'coop controller'      #sender address
        
        msg["To"] = settings.phone_number     #reciver address
        
        msg.set_content(message)   #message body
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            
            smtp.login(my_address,app_generated_password)    #login gmail account
            
            print("sending mail")
            smtp.send_message(msg)   #send message 
            print("mail has sent")