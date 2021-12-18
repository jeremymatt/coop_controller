# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 08:43:37 2021

@author: jmatt
"""

import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
import board
import busio
import datetime as dt
from email.message import EmailMessage
import os
import RPi.GPIO as GPIO
import time
import traceback
from twilio.rest import Client 
import settings
import smtplib
from suntime import Sun

GPIO.setmode(GPIO.BCM)

def restart():
    os.system('sudo reboot')
    
    
    """
    #https://www.ridgesolutions.ie/index.php/2013/02/22/raspberry-pi-restart-shutdown-your-pi-from-python-code/
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)
    """

def get_datetime_parts():
    #Get the year, month, day, hour, minute, and second of the current local time
    ct = dt.datetime.now()
    y = ct.year
    mo = str(ct.month).zfill(2)
    d = str(ct.day).zfill(2)
    h = str(ct.hour).zfill(2)
    m = str(ct.minute).zfill(2)
    s = str(ct.second).zfill(2)
    
    return y,mo,d,h,m,s
    

def send_crash_notification(logfile_name):
    #SEnd a text message crash notification.  If that fails, write the failure 
    #to the logfile
    y,mo,d,h,m,s = get_datetime_parts()
    message = '*** ERROR ***\n    COOP CONTROLLER HAS CRASHED\n    {}-{}-{} {}:{}'.format(y,mo,d,h,m)
    for address in settings.phone_numbers:
        
        try:
            send_message_twilio(address,message)
        except Exception as e:
            with open(logfile_name, 'a') as file:
                file.write('\nFAILED TO SEND CRASH TEXT NOTIFICATION. \nADDRESS:\n{}\nMESSAGE:\n{}\n\nTRACEBACK:\n'.format(address,message))
                traceback.print_exc(limit=None, file=file, chain=True)
                
        
def send_message_twilio(address,message):
    #Send a message using the twilio text service
    client = Client(settings.account_sid, settings.auth_token) 
     
    message = client.messages.create(  
                                  messaging_service_sid='MG3cef878fb0107a7b2c4412cc890ba226', 
                                  body=message,      
                                  to=address 
                              ) 
         

class coop_controller:
    
    def __init__(self):
        #Get the current date & time and generate a logfile name
        y,mo,d,h,m,s = get_datetime_parts()
        self.logfile_name = 'LOGFILE_{}-{}-{}_{}:{}:{}.txt'.format(y,mo,d,h,m,s)
        #Get the current directory, generate the log directory path, and make
        #the directory if it doesn't exist
        cd = os.getcwd()
        self.log_dir = os.path.join(cd,'logs')
        if not os.path.isdir(self.log_dir):
            os.makedirs(self.log_dir)
            
        #Clear old logs
        self.clear_old_logs()
            
        #Generate the logfile name
        self.logfile_name = os.path.join(self.log_dir,self.logfile_name) 
        
        
        with open(self.logfile_name,'w') as f:
            f.write('\n')
            f.write('Welcome to the Jungle!!!\n')
        
        #Run the function to get the current time in UTC
        self.get_cur_time()
        #Calculate the sunrise/sunset times
        self.get_sunrise_sunset()
        #Initialize the GPIO pins
        self.init_pins()
        #INit the program control flags, constants, and variables.
        self.init_flags()
        #Initialize the butten menu dictionary
        self.init_button_menu()
        #Initialize the display
        self.init_display()
                       
        
    def clear_old_logs(self):
        #List all the foles in the log directory, sort, and keep only the 30
        #newest logs
        files = [os.path.join(self.log_dir,file) for file in os.listdir(self.log_dir)]
        files = [file for file in files if os.path.isfile(file)]
        files.sort()
        if len(files)>30:
            files_to_delete = files[:(len(files)-30)]
            for file in files_to_delete:
                os.remove(file)
        
        
    def run(self):
        #The main loop
        #Init a trigger to print the current state to the console for debugging
        #purposes
        self.print_state_trigger = self.cur_time
        while True:
            #Get the current times
            self.get_cur_time()
            #Generate boolean control variables based on the current time relative
            #to the door&light control times
            self.check_times()
            #Check if the program is in an error state (IE the door didn't 
            #open or close properly)
            self.check_error_state()
            #Check if there was a button press and handle
            self.check_buttons()
            #Check the status of the inputs (the switches testing if the door
            #is open or closed)
            self.check_inputs()
            #Check the door status and open/close if necessary
            self.check_door()
            
            if self.cur_time > self.print_state_trigger:
                self.print_state_trigger = self.cur_time + self.long_time
                self.print_state()
            
            self.check_display_status()
            
            
    def print_sun_times(self,label_msg = None):
        #Prints the sunrise/sunset times to the logfile
        sunrise,parts = self.get_datetime_string(self.sunrise)
        sunset,parts = self.get_datetime_string(self.sunset)
        close_time,parts = self.get_datetime_string(self.close_time)
        with open(self.logfile_name,'a') as f:
            f.write('\n')
            f.write('New Day!\n')
            f.write('    Sunrise: {}\n'.format(sunrise))
            f.write('     Sunset: {}\n'.format(sunset))
            f.write(' Door close: {}\n'.format(close_time))
            
    def print_state(self,label_msg = None):
        #Prints the state of control variables to the logfile and to the console
        with open(self.logfile_name,'a') as f:
            f.write('\n')
            if label_msg != None:
                f.write(label_msg)
                
            string,parts = self.get_datetime_string(self.cur_time)
            f.write('{}\n'.format(string))
            f.write('Door is opening: {}\n'.format(self.door_is_opening))
            f.write('Door is fully open: {}\n'.format(self.door_is_open))
            f.write('Door is closing: {}\n'.format(self.door_is_closing))
            f.write('Door is closed: {}\n'.format(self.door_is_closed))
            f.write('Door override: {}\n'.format(self.door_state_override))
            f.write('Light is on: {}\n'.format(self.light_is_on))
            f.write('Light override: {}\n'.format(self.light_state_override))
            f.write('IN ERROR STATE: {}\n'.format(self.error_state))
            f.write('current menu: {}\n'.format(self.cur_menu))
            f.write('In submenu: {}\n'.format(self.in_sub_menu))
            f.write('Items in message send queue: {}\n'.format(len(self.notification_list)))
            f.write('Menu Message: {}\n'.format(self.msg))
        
        
        print('\n')
        # print('\nDoor is open: {}'.format(self.door_is_open))
        if label_msg != None:
            print(label_msg)
        print(self.cur_time)
        print('Door is opening: {}'.format(self.door_is_opening))
        print('Door is fully open: {}'.format(self.door_is_open))
        # print('Door is closed: {}'.format(self.door_is_closed))
        print('Door is closing: {}'.format(self.door_is_closing))
        print('Door is closed: {}'.format(self.door_is_closed))
        print('Door override: {}'.format(self.door_state_override))
        print('Light is on: {}'.format(self.light_is_on))
        print('Light override: {}'.format(self.light_state_override))
        print('IN ERROR STATE: {}'.format(self.error_state))
        print('current menu: {}'.format(self.cur_menu))
        print('In submenu: {}'.format(self.in_sub_menu))
        print('Items in message send queue: {}'.format(len(self.notification_list)))
        print('Menu Message: {}'.format(self.msg))
        
            
    def check_error_state(self):
        display_state = True
        
        in_err_state = False
        
        disp_blink_time = self.cur_time + dt.timedelta(seconds=0.5)
        
        while self.error_state:
            if not in_err_state:
                self.print_state('IN ERROR STATE\n')
                self.lcd.color = [100, 0, 0]
                self.lcd.message = self.error_msg
                in_err_state = True
                
            self.get_cur_time()
            self.check_send_notification_time()
            self.check_buttons()
            if self.cur_time>disp_blink_time:
                if display_state:
                    self.lcd.color = [0,0,0]
                    disp_blink_time = self.cur_time + dt.timedelta(seconds=.5)
                    display_state = False
                else:
                    self.lcd.color = [100,0,0]
                    disp_blink_time = self.cur_time + dt.timedelta(seconds=.75)
                    display_state = True
                    
        if in_err_state:
            self.display_on()
            self.cur_menu = 0
            self.in_sub_menu = False
            self.update_display()
            
            
            
            
    def check_door(self):
        
        if self.door_is_closed and self.door_is_open:
            string,parts = self.get_datetime_string(self.cur_time)
            msg = 'DOOR MALFUNCTION:\n  Both switches closed \n  time: {}'.format(string)
            self.error_msg = 'ERR:bth swch cls\nSelect ==> clear'
          
            
            self.error_state = True
            self.cur_menu = -3
            self.in_sub_menu = False
            
            self.door_stop()
            self.queue_notification(msg)
            
        
        if self.door_is_closed and self.door_is_closing:
            print('triggered close stop at: {}'.format(self.cur_time))
            self.door_is_closing = False
            self.door_is_opening = False
            self.door_move_end_time = self.cur_time + self.long_time
            self.print_state_trigger = self.cur_time - dt.timedelta(seconds=1)
            self.door_travel_stop_time = self.cur_time + dt.timedelta(seconds=(settings.extra_door_travel+settings.door_lock_travel))
            with open(self.logfile_name,'a') as f:
                f.write('\n')
                f.write('Stop closing:\n')
                f.write('     Triggered at: {}'.format(self.get_datetime_string(self.cur_time)[0]))
                f.write('   Stop moving at: {}'.format(self.get_datetime_string(self.door_travel_stop_time)[0]))
            
        if self.cur_time>self.door_travel_stop_time:
            print('Stopped move at: {}'.format(self.cur_time))
            self.door_travel_stop_time = self.cur_time + self.long_time
            self.print_state_trigger = self.cur_time - dt.timedelta(seconds=1)
            self.door_stop()
           
        if self.door_is_open and self.door_is_opening:
            print('triggered open stop at: {}'.format(self.cur_time))
            self.door_is_closing = False
            self.door_is_opening = False
            self.door_move_end_time = self.cur_time + self.long_time
            self.print_state_trigger = self.cur_time - dt.timedelta(seconds=1)
            self.door_travel_stop_time = self.cur_time + dt.timedelta(seconds=settings.extra_door_travel)
            with open(self.logfile_name,'a') as f:
                f.write('\n')
                f.write('Stop opening:\n')
                f.write('     Triggered at: {}'.format(self.get_datetime_string(self.cur_time)[0]))
                f.write('   Stop moving at: {}'.format(self.get_datetime_string(self.door_travel_stop_time)[0]))
            
            
        if self.door_open_time and not (self.door_is_open or self.door_is_opening) and not self.door_state_override:
            string,parts = self.get_datetime_string(self.cur_time)
            self.print_state_trigger = self.cur_time - dt.timedelta(seconds=1)
            msg = 'Chicken door opening:\n  time: {}'.format(string)
            # msg = 'CHiCKeN DooR OpEnIng:\n  time: {}'.format(string)
            self.queue_notification(msg)
            self.door_raise()
            
        if not self.door_open_time and not (self.door_is_closed or self.door_is_closing) and not self.door_state_override:
            string,parts = self.get_datetime_string(self.cur_time)
            self.print_state_trigger = self.cur_time - dt.timedelta(seconds=1)
            msg = 'Chicken door closing:\n  time: {}'.format(string)
            # msg = 'cHicKen DOOr ClOsiNG:\n  time: {}'.format(string)
            self.queue_notification(msg)
            self.door_lower()
            
        if self.light_on_time and not self.light_is_on and not self.light_state_override:
            string,parts = self.get_datetime_string(self.cur_time)
            self.print_state_trigger = self.cur_time - dt.timedelta(seconds=1)
            msg = 'Chicken light turning on:\n  time: {}'.format(string)
            # msg = 'ChiCKen liGhT tUrNiNG on:\n  time: {}'.format(string)
            if settings.notify_lights:
                self.queue_notification(msg)
            self.light_on()
            
        if not self.light_on_time and self.light_is_on and not self.light_state_override:
            string,parts = self.get_datetime_string(self.cur_time)
            self.print_state_trigger = self.cur_time - dt.timedelta(seconds=1)
            msg = 'Chicken light turning off:\n  time: {}'.format(string)
            # msg = 'ChIcKeN lIgHt TuRnInG oFf:\n  time: {}'.format(string)
            if settings.notify_lights:
                self.queue_notification(msg)
            self.light_off()
            
            
    def check_inputs(self):
        self.door_is_closed = GPIO.input(self.pins['door_closed'])==GPIO.LOW
        self.door_is_open = GPIO.input(self.pins['door_open'])==GPIO.LOW
        
    
    def init_button_menu(self):
        self.button_menu = {}
        menu = -3
        sub_menu = False
        self.button_menu[menu] = {}
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = self.disp_error_msg
        self.button_menu[menu][sub_menu]['select'] = self.cancel_error
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = None
        self.button_menu[menu][sub_menu]['down'] = None
        
        menu = -2
        sub_menu = False
        self.button_menu[menu] = {}
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = self.disp_override
        self.button_menu[menu][sub_menu]['select'] = None
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = self.next_menu
        self.button_menu[menu][sub_menu]['down'] = self.prev_menu
        
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
        self.button_menu[menu][sub_menu]['msg'] = self.disp_door_override
        self.button_menu[menu][sub_menu]['select'] = self.enter_submenu
        self.button_menu[menu][sub_menu]['left'] = self.cancel_door_override
        self.button_menu[menu][sub_menu]['right'] = self.cancel_door_override
        self.button_menu[menu][sub_menu]['up'] = self.next_menu
        self.button_menu[menu][sub_menu]['down'] = self.prev_menu
        
        menu = 2
        sub_menu = True
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = 'Override door\nUD:op/cls,LR:stp'
        self.button_menu[menu][sub_menu]['select'] = self.exit_submenu
        self.button_menu[menu][sub_menu]['left'] = self.door_stop
        self.button_menu[menu][sub_menu]['right'] = self.door_stop
        self.button_menu[menu][sub_menu]['up'] = self.override_door_raise
        self.button_menu[menu][sub_menu]['down'] = self.override_door_lower
        
        menu = 3
        sub_menu = False
        self.button_menu[menu] = {}
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = self.disp_light_override
        self.button_menu[menu][sub_menu]['select'] = self.enter_submenu
        self.button_menu[menu][sub_menu]['left'] = self.cancel_light_override
        self.button_menu[menu][sub_menu]['right'] = self.cancel_light_override
        self.button_menu[menu][sub_menu]['up'] = self.next_menu
        self.button_menu[menu][sub_menu]['down'] = self.prev_menu
        
        menu = 3
        sub_menu = True
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = 'Override light\nUD:on/off'
        self.button_menu[menu][sub_menu]['select'] = self.exit_submenu
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = self.override_light_on
        self.button_menu[menu][sub_menu]['down'] = self.override_light_off
        
        menu = 4
        sub_menu = False
        self.button_menu[menu] = {}
        self.button_menu[menu][sub_menu] = {}
        self.button_menu[menu][sub_menu]['msg'] = self.disp_sensor_state
        self.button_menu[menu][sub_menu]['select'] = None
        self.button_menu[menu][sub_menu]['left'] = None
        self.button_menu[menu][sub_menu]['right'] = None
        self.button_menu[menu][sub_menu]['up'] = self.next_menu
        self.button_menu[menu][sub_menu]['down'] = self.prev_menu
            
    def check_buttons(self):
        
        if self.lcd.left_button:
            self.do_button('left')
        
        elif self.lcd.up_button:
            self.do_button('up')

        elif self.lcd.down_button:
            self.do_button('down')

        elif self.lcd.right_button:
            self.do_button('right')

        elif self.lcd.select_button:
            self.do_button('select')
            
        
    def enter_submenu(self):
        self.in_sub_menu = True
        
    def exit_submenu(self):
        self.in_sub_menu = False
        
    def do_button(self,button):
        time.sleep(0.1)
        if self.button_menu[self.cur_menu][self.in_sub_menu][button] != None:
            self.display_off_time = self.cur_time + dt.timedelta(seconds=settings.screen_on_time)
            if not self.display_is_on:
                self.display_on()
            
            self.button_menu[self.cur_menu][self.in_sub_menu][button]()
            
            self.display_message = self.button_menu[self.cur_menu][self.in_sub_menu]['msg']
            
    def cancel_error(self):
        self.in_sub_menu = False
        self.cur_menu = 1
        self.error_state = False
            
    def update_display(self):
        if self.display_is_on:    
            if type(self.display_message) == str:
                self.msg = self.display_message
            else:
                self.msg = self.display_message()
                
            if self.prev_display_message != self.msg:
                self.lcd.clear()
                self.lcd.message = self.msg
                self.prev_display_message = self.msg
        
    def override_door_raise(self):
        self.print_state_trigger = self.cur_time - dt.timedelta(seconds=1)
        self.door_state_override = True
        self.door_raise()
    
    def override_door_lower(self):
        self.print_state_trigger = self.cur_time - dt.timedelta(seconds=1)
        self.door_state_override = True
        self.door_lower()
        
    def cancel_door_override(self):
        self.print_state_trigger = self.cur_time - dt.timedelta(seconds=1)
        self.door_state_override = False
        
            
    def door_stop(self):
        GPIO.output(self.pins['door_raise'], GPIO.LOW)
        GPIO.output(self.pins['door_lower'], GPIO.LOW)
        self.door_is_opening = False
        self.door_is_closing = False
        self.door_move_end_time = self.cur_time+self.long_time
        
    def door_raise(self):
        GPIO.output(self.pins['door_lower'], GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(self.pins['door_raise'], GPIO.HIGH)
        self.door_is_opening = True
        self.door_is_closing = False
        self.door_move_end_time = self.cur_time+self.door_travel_time
        
    def door_lower(self):
        GPIO.output(self.pins['door_raise'], GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(self.pins['door_lower'], GPIO.HIGH)
        self.door_is_opening = False
        self.door_is_closing = True
        self.door_move_end_time = self.cur_time+self.door_travel_time
        
    def override_light_on(self):
        self.light_state_override = True
        self.light_on()
        
        
    def override_light_off(self):
        self.light_state_override = True
        self.light_off()
        
    def cancel_light_override(self):
        self.light_state_override = False
        
    def light_on(self):
        GPIO.output(self.pins['light'], GPIO.HIGH)
        self.light_is_on = True
        
    def light_off(self):
        GPIO.output(self.pins['light'], GPIO.LOW)
        self.light_is_on = False
        
            
    def next_menu(self):
        self.in_sub_menu = False
        self.cur_menu = max(0,(self.cur_menu+1))
        self.cur_menu %= (max(self.button_menu.keys())+1)
        
    def prev_menu(self):
        self.in_sub_menu = False
        self.cur_menu -= 1
        if self.cur_menu < 0:
            self.cur_menu = max(self.button_menu.keys())
            
    def disp_error_msg(self):
        return self.error_msg
    
    def disp_door_override(self):
        if self.door_state_override:
            msg = 'DOOR OVERRIDDEN\nL/R to cancel'
        else:
            msg = 'Door Override\nSel => manual'
        return msg
        
    def disp_light_override(self):
        if self.light_state_override:
            msg = 'LIGHT OVERRIDDEN\nL/R to cancel'
        else:
            msg = 'Light Override\nSel => manual'
        return msg
            
    def disp_override(self):
        if self.door_state_override:
            door_state = 'T'
        else:
            door_state = 'F'
            
        if self.light_state_override:
            light_state = 'T'
        else:
            light_state = 'F'
            
        msg = 'Override Door: {}\n        Light: {}'.format(door_state,light_state)
        return msg
            
            
    def disp_sensor_state(self):
        if self.door_is_closed:
            DC = 'cl'
        else:
            DC = 'op'
            
        if self.door_is_open:
            DO = 'cl'
        else:
            DO = 'op'
            
        msg = 'Sensor state\nDC:{} DO:{}'.format(DC,DO)
        return msg
            
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
        
        string = '{}-{} {}:{}'.format(month,day,hour,minute)
        parts = (month,day,hour,minute,second)
        return string,parts       
            
    def check_times(self):
        self.door_open_time = (self.cur_time>self.sunrise) & (self.cur_time<self.close_time)
        
        self.light_on_time = (self.cur_time>self.sunrise) & (self.cur_time<self.sunset)
        
        
        self.check_send_notification_time()
        
        self.check_display_time()
        
        self.check_for_new_day()
        
        self.check_door_move_time()
            
            
            
    def check_send_notification_time(self):
        if (self.cur_time > self.send_next_message_time) and (len(self.notification_list)>0):
            self.send_next_message_time = self.cur_time + dt.timedelta(seconds=1.5)
            self.send_next_notification()
            
    def check_display_time(self):
        self.display_time_exceeded = self.cur_time>self.display_off_time
        
    def check_for_new_day(self):
        string,parts = self.get_datetime_string(self.cur_time)
        month,day,hour,minute,second = parts
        if self.cur_day != day:
            if settings.restart_daily:
                restart()
            else:
                self.cur_day = day
                self.get_sunrise_sunset()
            
    def check_door_move_time(self):
        if self.cur_time > self.door_move_end_time:
            string,parts = self.get_datetime_string(self.cur_time)
            if self.door_is_closing:
                msg = 'DOOR MALFUNCTION:\n  Door Didn\'t close \n  time: {}'.format(string)
                self.error_msg = 'ERR: clse failed\nSelect ==> clear'
            elif self.door_is_opening:
                msg = 'DOOR MALFUNCTION:\n  Door Didn\'t open \n  time: {}'.format(string)
                self.error_msg = 'ERR: open failed\nSelect ==> clear'
            else:
                msg = 'DOOR MALFUNCTION:\n  Not sure what the problem is \n  time: {}'.format(string)
                self.error_msg = 'ERR: unk failure\nSelect ==> clear'
              
                
            self.error_state = True
            self.cur_menu = -3
            self.in_sub_menu = False
            
            self.door_stop()
            self.queue_notification(msg)
            
            
    def check_display_status(self):
        if self.display_is_on:
            if self.display_time_exceeded:
                if self.door_state_override or self.light_state_override:
                    self.cur_menu = -2
                    self.display_message = self.disp_override()
                    self.in_sub_menu = False
                    self.update_display()
                else:
                    self.display_off()
            else:
                self.update_display()
            
        
        
    def init_display(self):
        
        lcd_columns = 16
        lcd_rows = 2
        i2c = busio.I2C(board.SCL, board.SDA)
        self.lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
        self.display_on()
        self.display_off_time = self.cur_time + dt.timedelta(seconds=10)
        # self.display_message = 'Welcome to the\nJungle!'
        self.display_message = 'HI! Starting the\nstream'
        self.prev_display_message = 'none'
        
    
    def display_on(self):
        self.display_is_on = True
        self.lcd.color = [100, 0, 0]
        
    def display_off(self):
        self.display_is_on = False
        self.cur_menu = -1
        self.lcd.clear()
        self.display_message = 'None'
        self.msg = 'None'
        self.in_sub_menu = False
        self.lcd.color = [0, 0, 0]
    
    
    def init_flags(self):
        self.long_time = dt.timedelta(days=365*100)
        string,parts = self.get_datetime_string(self.cur_time)
        month,day,hour,minute,second = parts
        self.cur_day = day
        self.light_is_on = None
        # self.door_is_open = False
        # self.door_is_closed = False
        self.door_is_opening = False
        self.door_is_closing = False
        self.door_travel_stop_time = self.cur_time+self.long_time
        self.door_state_override = False
        self.light_state_override = False
        self.new_day = False
        self.door_move_end_time = self.cur_time+self.long_time
        self.cur_menu = -1
        self.in_sub_menu = False
        self.door_travel_time = dt.timedelta(seconds = settings.expected_door_travel_time)
        self.notification_list = []
        self.send_next_message_time = self.cur_time
        self.error_state = False
        self.msg = 'None'
        
       
    def init_pins(self):
        
        outputs = [13,20,21]
        for output in outputs:
            GPIO.setup(output,GPIO.OUT)
            GPIO.output(output, GPIO.LOW)        
        
        inputs = [16,19]
        for inpt in inputs:
            GPIO.setup(inpt,GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
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
        self.print_sun_times()
        
        
    def queue_notification(self,message):
        for address in settings.phone_numbers:
            self.notification_list.append((message,address))
        
        
    def send_next_notification(self):
        message,address = self.notification_list.pop(0)
        
        try:
            send_message_twilio(address,message)
        except Exception as e:
            with open(self.logfile_name, 'a') as file:
                file.write('\nFAILED TO SEND TEXT NOTIFICATION. \nADDRESS:\n{}\nMESSAGE:\n{}\n\nTRACEBACK:\n'.format(address,message))
                traceback.print_exc(limit=None, file=file, chain=True)
        
        
        
        # msg= EmailMessage()
        # my_address = settings.email
        # app_generated_password = settings.password    # gmail generated password
        # msg["From"]= 'coop controller'      #sender address
        
        # msg["To"] = address     #reciver address
        
        # msg.set_content(message)   #message body
        
        # with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            
        #     smtp.login(my_address,app_generated_password)    #login gmail account
            
        #     print("sending mail")
        #     smtp.send_message(msg)   #send message 
        #     print("mail has sent")