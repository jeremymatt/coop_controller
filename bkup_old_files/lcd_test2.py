import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
import time
import RPi.GPIO as GPIO

import subprocess

outputs = [13,20,21]
for output in outputs:
    GPIO.setup(output,GPIO.OUT)
    GPIO.output(output, GPIO.LOW)
#GPIO.setup(13, GPIO.OUT)
#GPIO.setup(20, GPIO.OUT)
#GPIO.setup(21, GPIO.OUT)


lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)

lcd.color = [100, 0, 0]
#lcd.color = [0,0,0]
lcd.message = "How're you doing\nkiddo?"
#time.sleep(1)
for i in range(0,-1,-1):
    lcd.message = "How're you doing\nkiddo? Bye in {}sec".format(i)
    time.sleep(1)
lcd.color = [0,0,0]
lcd.clear()   


with open('/home/pi/github/coop_controller/beans.txt', 'a') as file:
    file.write('Aobut to call coop controller\n')
    
#subprocess.call(['python','/home/pi/github/coop_controller/coop_controller.py'])
    
"""

while True:
    if lcd.left_button:
        print("Left!")
        lcd.message = "Left!"
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW)

    elif lcd.up_button:
        print("Up!")
        lcd.message = "Up!"
        GPIO.output(21, GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(20, GPIO.HIGH)

    elif lcd.down_button:
        print("Down!")
        lcd.message = "Down!"
        GPIO.output(20, GPIO.LOW)
        time.sleep(0.25)
        GPIO.output(21, GPIO.HIGH)

    elif lcd.right_button:
        print("Right!")
        lcd.message = "Right!"
        GPIO.output(13, GPIO.LOW)

    elif lcd.select_button:
        print("Select!")
        lcd.message = "Select!"
        GPIO.output(13, GPIO.HIGH)

    else:
        time.sleep(0.1)
        lcd.clear()    
"""