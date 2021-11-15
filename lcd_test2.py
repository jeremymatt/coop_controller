import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
import time
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)

lcd.color = [100, 0, 0]
#lcd.color = [0,0,0]
lcd.message = "How're you doing\nkiddo?"
time.sleep(1)
for i in range(15,-1,-1):
    lcd.message = "How're you doing\nkiddo? Bye in {}sec".format(i)
    time.sleep(1)
lcd.color = [0,0,0]
