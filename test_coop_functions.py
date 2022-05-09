# -*- coding: utf-8 -*-
"""
Created on Tue Nov 23 08:43:37 2021

@author: jmatt
"""

import datetime as dt
from email.message import EmailMessage
import os
import time
import traceback
from twilio.rest import Client 
import settings
import smtplib
from suntime import Sun
import random
import copy as cp

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

def get_datetime_string(dto):
    
    dto = dto.replace(tzinfo=dt.timezone.utc).astimezone(tz=None)
    month = str(dto.month).zfill(2)
    day = str(dto.day).zfill(2)
    hour = str(dto.hour).zfill(2)
    minute = str(dto.minute).zfill(2)
    second = str(dto.second).zfill(2)
    
    string = '{}-{} {}:{}'.format(month,day,hour,minute)
    parts = (month,day,hour,minute,second)
    return string,parts     

def print_sun_times(sunrise,sunset,close_time,label_msg = None):
    #Prints the sunrise/sunset times to the logfile
    sunrise,parts = get_datetime_string(sunrise)
    sunset,parts = get_datetime_string(sunset)
    close_time,parts = get_datetime_string(close_time)
    print('\n')
    print('New Day!\n')
    print('    Sunrise: {}\n'.format(sunrise))
    print('     Sunset: {}\n'.format(sunset))
    print(' Door close: {}\n'.format(close_time))
    
    
def check_sunset_is_current_day(dto):
    dto_orig = cp.deepcopy(dto)
    dto = dto.replace(tzinfo=dt.timezone.utc).astimezone(tz=None)
    day_delta = dto_orig.day-dto.day
    dto_orig = dto_orig + dt.timedelta(days=day_delta)
    return dto_orig
    


cur_time = dt.datetime.now(dt.timezone.utc)
sun = Sun(settings.latitude, settings.longitude)

sunrise = sun.get_sunrise_time(cur_time)
sunset = sun.get_sunset_time(cur_time)
while sunset<sunrise:
    print('incrementing sunrise to next day')
    sunset = sunset + dt.timedelta(days=1)
# sunset_new = check_sunset_is_current_day(sunset)

close_time = sunset + dt.timedelta(minutes=settings.wait_after_sunset)
print_sun_times(sunrise,sunset,close_time)
        


  
    #     self.get_cur_time()
    #     #Calculate the sunrise/sunset times
    #     self.get_sunrise_sunset()
    #     #Initialize the GPIO pins
    #     # self.init_pins()
    #     #INit the program control flags, constants, and variables.
    #     self.init_flags()
    #     #Initialize the butten menu dictionary
    #     # self.init_button_menu()
    #     #Initialize the display
    #     # self.init_display()
                       
        
    # def clear_old_logs(self):
    #     #List all the foles in the log directory, sort, and keep only the 30
    #     #newest logs
    #     files = [os.path.join(self.log_dir,file) for file in os.listdir(self.log_dir)]
    #     files = [file for file in files if os.path.isfile(file)]
    #     files.sort()
    #     if len(files)>30:
    #         files_to_delete = files[:(len(files)-30)]
    #         for file in files_to_delete:
    #             os.remove(file)
        
            
    
            

   
      
        
    # def disp_current_time(self):
    #     string,parts = self.get_datetime_string(self.cur_time)
    #     msg = 'Current Time:\n{}'.format(string)
    #     return msg
        
    # def disp_door_times(self):
    #     string,parts = self.get_datetime_string(self.sunrise)
    #     month,day,hour,minute,second = parts
    #     l1 = 'Door=>Open {}:{}'.format(hour,minute)
    #     string,parts = self.get_datetime_string(self.close_time)
    #     month,day,hour,minute,second = parts
    #     l2 = '     Close {}:{}'.format(hour,minute)
    #     msg = '{}\n{}'.format(l1,l2)
    #     return msg
        
    # def disp_light_times(self):
    #     string,parts = self.get_datetime_string(self.sunrise)
    #     month,day,hour,minute,second = parts
    #     l1 = 'Light=>On {}:{}'.format(hour,minute)
    #     string,parts = self.get_datetime_string(self.sunset)
    #     month,day,hour,minute,second = parts
    #     l2 = '      Off {}:{}'.format(hour,minute)
    #     msg = '{}\n{}'.format(l1,l2)
    #     return msg
        
      
            
    # def check_times(self):
    #     self.door_open_time = (self.cur_time>self.sunrise) & (self.cur_time<self.close_time)
        
    #     self.light_on_time = (self.cur_time>self.sunrise) & (self.cur_time<self.sunset)
        
        
    #     self.check_send_notification_time()
        
    #     self.check_display_time()
        
    #     self.check_for_new_day()
        
    #     self.check_door_move_time()
        
    #     if settings.VERBOSE:
    #         string,parts = self.get_datetime_string(self.cur_time)
    #         with open(self.logfile_name,'a') as f:
    #             print('\n\n******************')
    #             print(string)
    #             print('        raw: {}\n'.format(self.cur_time))
    #             string,parts = self.get_datetime_string(self.sunrise)
    #             print('    sunrise: {}\n'.format(string))
    #             print('        raw: {}\n'.format(self.sunrise))
    #             string,parts = self.get_datetime_string(self.sunset)
    #             print('        raw: {}\n'.format(self.sunset))
    #             print('    sunset: {}\n'.format(string))
    #             string,parts = self.get_datetime_string(self.close_time)
    #             print('    close_time: {}\n'.format(string))
    #             print('    Door should be open: {}\n'.format(self.door_open_time))
    #             print('    Light should be on: {}\n'.format(self.light_on_time))
    #             print('        After sunrise: {}\n'.format(self.cur_time>self.sunrise))
    #             print('        Before sunset: {}\n'.format(self.cur_time<self.sunset))
    #             print('        Before door close time: {}\n'.format(self.cur_time<self.close_time))
    #             print('******************\n\n')
            
            
            
    # def check_send_notification_time(self):
    #     if (self.cur_time > self.send_next_message_time) and (len(self.notification_list)>0):
    #         self.send_next_message_time = self.cur_time + dt.timedelta(seconds=1.5)
    #         self.send_next_notification()
            
    # def check_display_time(self):
    #     self.display_time_exceeded = self.cur_time>self.display_off_time
        
    # def check_for_new_day(self):
    #     string,parts = self.get_datetime_string(self.cur_time)
    #     month,day,hour,minute,second = parts
    #     if self.cur_day != day:
    #         if settings.restart_daily:
    #             restart()
    #         else:
    #             self.cur_day = day
    #             self.get_sunrise_sunset()
            
    # def check_door_move_time(self):
    #     if self.cur_time > self.door_move_end_time:
    #         string,parts = self.get_datetime_string(self.cur_time)
    #         if self.door_is_closing:
    #             msg = 'DOOR MALFUNCTION:\n  Door Didn\'t close \n  time: {}'.format(string)
    #             self.error_msg = 'ERR: clse failed\nSelect ==> clear'
    #         elif self.door_is_opening:
    #             msg = 'DOOR MALFUNCTION:\n  Door Didn\'t open \n  time: {}'.format(string)
    #             self.error_msg = 'ERR: open failed\nSelect ==> clear'
    #         else:
    #             msg = 'DOOR MALFUNCTION:\n  Not sure what the problem is \n  time: {}'.format(string)
    #             self.error_msg = 'ERR: unk failure\nSelect ==> clear'
              
                
    #         self.error_state = True
    #         self.cur_menu = -3
    #         self.in_sub_menu = False
            
    #         self.door_stop()
    #         self.queue_notification(msg)
            
            
    # def check_display_status(self):
    #     if self.display_is_on:
    #         if self.display_time_exceeded:
    #             if self.door_state_override or self.light_state_override:
    #                 self.cur_menu = -2
    #                 self.display_message = self.disp_override()
    #                 self.in_sub_menu = False
    #                 self.update_display()
    #             else:
    #                 self.display_off()
    #         else:
    #             self.update_display()
            
        
        
    # # def init_display(self):
        
    # #     lcd_columns = 16
    # #     lcd_rows = 2
    # #     i2c = busio.I2C(board.SCL, board.SDA)
    # #     self.lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
    # #     self.display_on()
    # #     self.display_off_time = self.cur_time + dt.timedelta(seconds=10)
    # #     # self.display_message = 'Welcome to the\nJungle!'
    # #     self.display_message = 'HI! Starting the\nstream'
    # #     self.prev_display_message = 'none'
        
    
    # def display_on(self):
    #     self.display_is_on = True
    #     self.lcd.color = [100, 0, 0]
        
    # def display_off(self):
    #     self.display_is_on = False
    #     self.cur_menu = -1
    #     self.lcd.clear()
    #     self.display_message = 'None'
    #     self.msg = 'None'
    #     self.in_sub_menu = False
    #     self.lcd.color = [0, 0, 0]
    
    
    # def init_flags(self):
    #     self.long_time = dt.timedelta(days=365*100)
    #     string,parts = self.get_datetime_string(self.cur_time)
    #     month,day,hour,minute,second = parts
    #     self.cur_day = day
    #     self.light_is_on = None
    #     self.door_closing_complete = False
    #     self.door_opening_complete = False
    #     self.door_is_opening = False
    #     self.door_is_closing = False
    #     self.door_travel_stop_time = self.cur_time+self.long_time
    #     self.door_state_override = False
    #     self.light_state_override = False
    #     self.new_day = False
    #     self.door_move_end_time = self.cur_time+self.long_time
    #     self.cur_menu = -1
    #     self.in_sub_menu = False
    #     self.door_travel_time = dt.timedelta(seconds = settings.expected_door_travel_time)
    #     self.notification_list = []
    #     self.send_next_message_time = self.cur_time
    #     self.error_state = False
    #     self.msg = 'None'
        
        
    # def queue_notification(self,message):
        
    #     for name in settings.phone_numbers.keys():
    #         address = settings.phone_numbers[name]
            
    #         # if (name == 'Monica') & (random.uniform(0,1)>.85):
    #         #     message = random_case(message)
            
    #         if (name == 'Jeremy') & (random.uniform(0,1)>.85):
    #             message = random_case(message)
                
    #         self.notification_list.append((message,address))
            
    #     # for address in settings.phone_numbers:
    #     #     self.notification_list.append((message,address))
        
        
    # def send_next_notification(self):
    #     message,address = self.notification_list.pop(0)
        
    #     try:
    #         send_message_twilio(address,message)
    #     except Exception as e:
    #         with open(self.logfile_name, 'a') as file:
    #             file.write('\nFAILED TO SEND TEXT NOTIFICATION. \nADDRESS:\n{}\nMESSAGE:\n{}\n\nTRACEBACK:\n'.format(address,message))
    #             traceback.print_exc(limit=None, file=file, chain=True)
        
        
        
    #     # msg= EmailMessage()
    #     # my_address = settings.email
    #     # app_generated_password = settings.password    # gmail generated password
    #     # msg["From"]= 'coop controller'      #sender address
        
    #     # msg["To"] = address     #reciver address
        
    #     # msg.set_content(message)   #message body
        
    #     # with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            
    #     #     smtp.login(my_address,app_generated_password)    #login gmail account
            
    #     #     print("sending mail")
    #     #     smtp.send_message(msg)   #send message 
    #     #     print("mail has sent")