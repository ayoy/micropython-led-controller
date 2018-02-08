import utime
from machine import Pin, PWM
import pycom

class Fader:
    def __init__(self, *args):
        self.pin_r = args[0]
        self.pin_g = args[1]
        self.pin_b = args[2]

        self.pin_r.mode(Pin.OUT)
        self.pin_g.mode(Pin.OUT)
        self.pin_b.mode(Pin.OUT)

        self.pwm = PWM(0, frequency=5000)

        self.pwm_r = self.pwm.channel(0, pin=self.pin_r, duty_cycle=1)
        self.pwm_g = self.pwm.channel(1, pin=self.pin_g, duty_cycle=1)
        self.pwm_b = self.pwm.channel(2, pin=self.pin_b, duty_cycle=1)


    def fade_in(self, red, green, blue):
        cb = 0
        step = 0.025

        while True:
            (r, g, b) = (
                min(255,int(cb * red)),
                min(255,int(cb * green)),
                min(255,int(cb * blue))
            )
            self.pwm_r.duty_cycle(1-r/255)
            self.pwm_g.duty_cycle(g/255)
            self.pwm_b.duty_cycle(b/255)
            print((r, g, b))
            rgbled = (r<<16) + (g<<8) + b
            pycom.rgbled(rgbled)
            if cb > 1:
                break
            cb = cb + step
            utime.sleep_ms(25)


    def fade_out(self, red, green, blue):
        cb = 1
        step = 0.005

        while True:
            (r, g, b) = (
                max(0, int(cb * red)),
                max(0, int(cb * green)),
                max(0, int(cb * blue))
            )
            self.pwm_r.duty_cycle(1-r/255)
            self.pwm_g.duty_cycle(g/255)
            self.pwm_b.duty_cycle(b/255)
            print((r, g, b))
            rgbled = (r<<16) + (g<<8) + b
            pycom.rgbled(rgbled)
            if cb < 0:
                break
            cb = cb - step
            utime.sleep_ms(25)
