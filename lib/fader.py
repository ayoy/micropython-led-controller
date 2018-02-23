import utime
from machine import Pin, PWM
from hls import rgb_to_hls, hls_to_rgb
import pycom

class Fader:
    def __init__(self, *args):
        self.pwm_r = args[0]
        self.pwm_g = args[1]
        self.pwm_b = args[2]

    def fade_in(self, red, green, blue):
        steps = 40

        (h, l, s) = rgb_to_hls(red/255, green/255, blue/255)

        lightness = 0
        lstep = l/steps

        while True:
            (r, g, b) = hls_to_rgb(h, lightness, s)
            self.pwm_r.duty_cycle(r)
            self.pwm_g.duty_cycle(g)
            self.pwm_b.duty_cycle(b)
            # print((int(r*255), int(g*255), int(b*255)))
            # rgbled = (int(r*255)<<16) + (int(g*255)<<8) + int(b*255)
            # pycom.rgbled(rgbled)
            if lightness > l:
                break
            lightness = lightness + lstep
            utime.sleep_ms(25)


    def fade_out(self, red, green, blue):
        steps = 200

        (h, l, s) = rgb_to_hls(red/255, green/255, blue/255)

        lstep = l/steps

        while True:
            (r, g, b) = hls_to_rgb(h, l, s)
            self.pwm_r.duty_cycle(r)
            self.pwm_g.duty_cycle(g)
            self.pwm_b.duty_cycle(b)
            # print((int(r*255), int(g*255), int(b*255)))
            # rgbled = (int(r*255)<<16) + (int(g*255)<<8) + int(b*255)
            # pycom.rgbled(rgbled)
            if l < 0:
                break
            l = l - lstep
            utime.sleep_ms(25)
