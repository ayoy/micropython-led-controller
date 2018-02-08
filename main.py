from helpers import *
import pycom
from network import WLAN
from machine import Pin
from _thread import start_new_thread
from fade import Fader
import utime

pycom.heartbeat(False)

import usocket as socket

def leds(port):
    s = socket.socket()
    ip_addr = WLAN().ifconfig()[0]
    s.bind((ip_addr, port))
    s.listen()

    while True:
        machine.idle()
        (conn, address) = s.accept()
        data = conn.recv(3)
        r = data[0]
        g = data[1]
        b = data[2]
        color = (r<<16) + (g<<8) + b
        print('({},{},{})'.format(r, g, b))
        pycom.rgbled(color)
        conn.close()


start_new_thread(leds, (4000,))

def button_callback(fader):
    print('fade in')
    fader.fade_in(82,111,2)
    utime.sleep_ms(2000)
    print('fade out')
    fader.fade_out(82,111,2)

def fade():
    button = Pin('P10', mode=Pin.IN, pull=Pin.PULL_UP)
    fader = Fader(Pin('P9'), Pin('P11'), Pin('P12'))
    button.callback(Pin.IRQ_FALLING, button_callback, fader)

start_new_thread(fade, ())
