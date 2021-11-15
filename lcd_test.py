# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 16:59:45 2021

@author: jmatt
"""
# test cod

# import board
# import busio
# import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
# lcd_columns = 16
# lcd_rows = 2
# i2c = busio.I2C(board.SCL, board.SDA)
# lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)

import board
import digitalio
import busio

print("Hello blinka!")

# Try to great a Digital input
pin = digitalio.DigitalInOut(board.D4)
print("Digital IO ok!")

# Try to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print("I2C ok!")

# Try to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("SPI ok!")

print("done!")
