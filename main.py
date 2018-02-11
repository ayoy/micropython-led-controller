from helpers import *
import pycom
from network import WLAN
from machine import Pin
from _thread import start_new_thread
from fade import Fader
import utime

pycom.heartbeat(False)

import usocket as socket

(r, g, b) = (0, 0, 20)
fader = Fader(Pin('P22'), Pin('P21'), Pin('P23'))
pir = Pin('P18', mode=Pin.IN, pull=None)

request_motion_stopped = False

# Commands:
#
# WAT - get color + fader status
# DIS - set color
# FAD - enable/disable Fader


def leds(port):
    global r, g, b, fader

    s = socket.socket()
    ip_addr = WLAN().ifconfig()[0]
    s.bind((ip_addr, port))
    s.listen()

    while True:
        machine.idle()
        (conn, address) = s.accept()
        data = conn.recv(3)
        command = data.decode('utf8')
        print(command)
        if command == "WAT":
            print('({},{},{}) {}'.format(r, g, b, fader.enabled))
            conn.send(bytes([r, g, b, fader.enabled]))
        elif command == "DIS":
            color = conn.recv(3)
            if len(color) == 3:
                r = color[0]
                g = color[1]
                b = color[2]
                color = (r<<16) + (g<<8) + b
                print('({},{},{})'.format(r, g, b))
                fader.set_color(r, g, b)
                # pycom.rgbled(color)
        elif command == "FAD":
            status = conn.recv(1)
            if len(status) == 1:
                fader.enabled = status[0] > 0
                print('fader enabled: {}'.format(fader.enabled))
                request_motion_stopped = True

        conn.close()


start_new_thread(leds, (4000,))


def motion_started(fader):
    global r, g, b
    if fader.enabled is True and r > 0 and g > 0 and b > 0:
        print('fading in')
        fader.fade_in(r, g, b)

def motion_stopped(fader):
    global r, g, b
    if r > 0 and g > 0 and b > 0:
        print('fading out')
        fader.fade_out(r, g, b)


def pir_handler(pir, fader):
    wait_for_rising = False

    while True:
        if request_motion_stopped is True:
            request_motion_stopped = False
            utime.sleep_ms(5000)
            motion_stopped(fader)
        else:
            # print(pir())
            if pir() is 0 and not wait_for_rising:
                print('pir 0 #1')
                utime.sleep_ms(500)
                if pir() is 0:
                    print('pir 0 #2')
                    motion_started(fader)
                    wait_for_rising = True
            elif wait_for_rising and pir() is 1:
                print('pir 1 #1')
                utime.sleep_ms(500)
                if pir() is 1:
                    print('pir 1 #2')
                    wait_for_rising = False
                    motion_stopped(fader)

        machine.idle()
        utime.sleep_ms(100)

pir_handler(pir, fader)
