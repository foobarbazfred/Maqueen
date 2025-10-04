#
# Maqueen Driver
#
#

DEFAULT_SPEED = 30
CTLR_ADDR = 0x10
MOTOR_L = 0
MOTOR_R = 2

FORWARD = 0
BACK = 1

class Maqueen:

    def __init__(self, i2c):
        self.i2c = i2c

    def go(self, speed = DEFAULT_SPEED):
        self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_L, FORWARD, speed)))
        self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_R, FORWARD, speed)))
    
    def back(self, speed = DEFAULT_SPEED):
        self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_L, BACK, speed)))
        self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_R, BACK, speed)))
    
    def stop(self):
        self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_L, FORWARD, 00)))
        self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_R, FORWARD, 00)))
    
    def rotate(self, direction, speed = DEFAULT_SPEED):
        if direction == 'L':
            self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_L, BACK, speed)))
            self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_R, FORWARD, speed)))
        elif direction == 'R':
            self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_L, FORWARD, speed)))
            self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_R, BACK, speed)))
    
    def turn(self, direction, speed = DEFAULT_SPEED):
        slow_speed = int(speed * 0.5)
        if direction == 'L':
            self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_L, FORWARD, slow_speed)))
            self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_R, FORWARD, speed)))
        elif direction == 'R':
            self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_L, FORWARD, speed)))
            self.i2c.writeto(CTLR_ADDR, bytes((MOTOR_R, FORWARD, slow_speed)))
    
    

#
#
#