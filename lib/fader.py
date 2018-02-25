import utime
from machine import Pin, PWM
from hls import rgb_to_hls, hls_to_rgb
import pycom
import _thread

class Fader:
    def __init__(self, *args):
        self.pwm_r = args[0]
        self.pwm_g = args[1]
        self.pwm_b = args[2]
        self.lightness = 0
        self._running = False
        self.fading_lock = _thread.allocate_lock()
        self.running_lock = _thread.allocate_lock()


    @property
    def running(self):
        value = None
        self.running_lock.acquire()
        value = self._running
        self.running_lock.release()
        return value


    @running.setter
    def running(self, value):
        self.running_lock.acquire()
        self._running = value
        self.running_lock.release()


    def fade_in(self, red, green, blue):
        if self.running is True:
            print('fading in progress, interrupting...')
            self.running = False
        _thread.start_new_thread(self._fade_in, (red, green, blue))

    def _fade_in(self, red, green, blue):
        self.fading_lock.acquire()
        self.running = True
        steps = 40

        (r, g, b) = (red, green, blue)
        (h, l, s) = rgb_to_hls(r/255, g/255, b/255)

        lstep = l/steps

        while True:
            (r, g, b) = hls_to_rgb(h, self.lightness, s)
            self.pwm_r.duty_cycle(r)
            self.pwm_g.duty_cycle(g)
            self.pwm_b.duty_cycle(b)
            # print((int(r*255), int(g*255), int(b*255)))
            # rgbled = (int(r*255)<<16) + (int(g*255)<<8) + int(b*255)
            # pycom.rgbled(rgbled)
            if self.lightness > l:
                print('fade in complete')
                break
            self.lightness = self.lightness + lstep
            utime.sleep_ms(25)
            if self.running is False:
                print('stopping fade in at lightness {}'.format(self.lightness))
                break

        self.running = False
        self.fading_lock.release()


    def fade_out(self, red, green, blue):
        if self.running is True:
            print('fading in progress, interrupting...')
            self.running = False
        _thread.start_new_thread(self._fade_out, (red, green, blue))

    def _fade_out(self, red, green, blue):
        self.fading_lock.acquire()
        self.running = True
        steps = 200

        (r, g, b) = (red, green, blue)
        (h, self.lightness, s) = rgb_to_hls(red/255, green/255, blue/255)

        lstep = self.lightness/steps

        while True:
            (r, g, b) = hls_to_rgb(h, self.lightness, s)
            self.pwm_r.duty_cycle(r)
            self.pwm_g.duty_cycle(g)
            self.pwm_b.duty_cycle(b)
            # print((int(r*255), int(g*255), int(b*255)))
            # rgbled = (int(r*255)<<16) + (int(g*255)<<8) + int(b*255)
            # pycom.rgbled(rgbled)
            if self.lightness < 0:
                print('fade out complete')
                break
            self.lightness = self.lightness - lstep
            utime.sleep_ms(25)
            if self.running is False:
                print('stopping fade out at lightness {}'.format(self.lightness))
                break

        self.running = False
        self.fading_lock.release()
