from helpers import *
import pycom
from network import WLAN
from machine import Pin
from _thread import start_new_thread
from fade import Fader
import utime
from ledstrip import LEDStrip

pycom.heartbeat(False)


import usocket as socket

ledstrip = LEDStrip()
fader = Fader(Pin('P22'), Pin('P21'), Pin('P23'))
pir = Pin('P18', mode=Pin.IN, pull=None)

request_motion_stopped = False

# Commands:
#
# WAT - get color + fader status
# DIS - set color
# FAD - enable/disable Fader


def leds(port):
    global ledstrip

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
            print('({},{},{}) {}'.format(ledstrip.r, ledstrip.g, ledstrip.b, ledstrip.fading))
            conn.send(bytes([ledstrip.r, ledstrip.g, ledstrip.b, ledstrip.fading]))
        elif command == "DIS":
            color = conn.recv(3)
            if len(color) == 3:
                r = color[0]
                g = color[1]
                b = color[2]
                color = (r<<16) + (g<<8) + b
                print('({},{},{})'.format(ledstrip.r, ledstrip.g, ledstrip.b))
                fader.set_color(ledstrip.r, ledstrip.g, ledstrip.b)
                # pycom.rgbled(color)
        elif command == "FAD":
            status = conn.recv(1)
            if len(status) == 1:
                ledstrip.fading = status[0] > 0
                print('fader enabled: {}'.format(ledstrip.fading))
                request_motion_stopped = True

        conn.close()


start_new_thread(leds, (4000,))


def motion_started(fader):
    global ledstrip
    if ledstrip.fading is True and ledstrip.enabled:
        print('fading in')
        fader.fade_in(ledstrip.r, ledstrip.g, ledstrip.b)


def motion_stopped(fader):
    global ledstrip
    if ledstrip.enabled:
        print('fading out')
        fader.fade_out(ledstrip.r, ledstrip.g, ledstrip.b)


def pir_handler(pir, fader):
    global request_motion_stopped
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
