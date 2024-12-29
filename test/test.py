#
# Test Program
# MPU: ESP32-C3
#

import time	
from machine import Pin
from machine import I2C
from machine import Timer
from maqueen import Maqueen

MAQUEEN_SERVO_ADDR = 0x10

yellow_LED=Pin(21,Pin.OUT)

blink_timer=None


def callback(timer): 
    yellow_LED.value((yellow_LED.value()+1)%2)

def start_blink(type):
    global blink_timer
    if type == 'STATE_RUN':
       period = 500
    elif type == 'STATE_ERROR':
       period = 100
    elif type == 'STATE_FIN':
       period = 2000
    else:
       period = 2000

    if blink_timer is not None:
        blink_timer.deinit()
        blink_timer = None

    blink_timer = Timer(0) 
    blink_timer.init(period=period, mode=Timer.PERIODIC, callback=callback)

i2c = None

def main():
    global i2c
    if i2c is None:
        i2c = I2C(0, scl=Pin(6), sda=Pin(5), freq=10_000)
        time.sleep(1)

    if MAQUEEN_SERVO_ADDR in i2c.scan():
         start_blink('STATE_RUN')
         maqueen = Maqueen(i2c)
         test(maqueen)
         start_blink('STATE_FIN')
    else:
         print('Error in main')
         print('can no find Maqeen motor driver')
         print(i2c.scan())
         start_blink('STATE_ERROR')

# test program
#
def test(maq):
    maq.go()
    time.sleep(3)
    
    maq.stop()
    time.sleep(1)
    
    maq.rotate('L')
    time.sleep(3)
    
    maq.rotate('R')
    time.sleep(3)
    
    maq.turn('L')
    time.sleep(3)
    
    maq.turn('R')
    time.sleep(3)
    
    maq.stop()
    

#
# call main
#
main()




