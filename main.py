from helpers import *
import pycom
from network import WLAN
from _thread import start_new_thread

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
        # print('({},{},{})'.format(r, g, b))
        pycom.rgbled(color)
        conn.close()


start_new_thread(leds, (4000,))
