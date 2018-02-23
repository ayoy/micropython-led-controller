from helpers import *
import pycom
from network import WLAN
from machine import Pin, Timer
from _thread import start_new_thread
from fade import Fader
import utime
from ledstrip import LEDStrip

pycom.heartbeat(False)


import usocket as socket

ledstrip = LEDStrip()
fader = Fader(Pin('P22'), Pin('P21'), Pin('P23'))
fader.set_color(ledstrip.r, ledstrip.g, ledstrip.b)
pir = Pin('P18', mode=Pin.IN, pull=None)
fadeout_timer = None

# Commands:
#
# WAT - get color + fader status
# DIS - set color
# FAD - enable/disable Fader


def leds(port):
    global ledstrip
    global fader

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
            status = bytes([ledstrip.r, ledstrip.g, ledstrip.b])
            status += chr(ledstrip.fading)
            status += ledstrip.schedule_start.to_bytes(2, 'little')
            status += ledstrip.schedule_stop.to_bytes(2, 'little')
            conn.send(status)
        elif command == "DIS":
            color = conn.recv(3)
            if len(color) == 3:
                r = color[0]
                g = color[1]
                b = color[2]
                color = (r<<16) + (g<<8) + b
                print('({},{},{})'.format(r, g, b))
                ledstrip.r = r
                ledstrip.g = g
                ledstrip.b = b
                fader.set_color(ledstrip.r, ledstrip.g, ledstrip.b)
                # pycom.rgbled(color)
        elif command == "FAD":
            status = conn.recv(5)
            if len(status) == 5:
                fader_enabled = status[0] > 0
                fader_changed = fader_enabled != ledstrip.fading
                ledstrip.fading = fader_enabled
                ledstrip.schedule_start = int.from_bytes(status[1:3], 'little')
                ledstrip.schedule_end = int.from_bytes(status[3:5], 'little')

                if ledstrip.schedule_start < 1440 and ledstrip.schedule_end < 1440:
                    start_hour = int(ledstrip.schedule_start/60)
                    start_min = (ledstrip.schedule_start - 60*start_hour)
                    end_hour = int(ledstrip.schedule_end/60)
                    end_min = (ledstrip.schedule_end - 60*end_hour)
                    print('fader enabled: {}, start: {}:{}, end: {}:{}'
                        .format(ledstrip.fading, start_hour, start_min, end_hour, end_min))
                else:
                    print('fader enabled: {}'.format(ledstrip.fading))

                if fader_changed:
                    if ledstrip.fading:
                        motion_stopped(fader)
                        start_pir()
                    else:
                        stop_pir()

        conn.close()


start_new_thread(leds, (4000,))


# =======================================


def motion_started(fader):
    global ledstrip
    if ledstrip.fading and ledstrip.enabled:
        print('fading in')
        fader.fade_in(ledstrip.r, ledstrip.g, ledstrip.b)


def fadeout_timer_handler(args):
    fader = args[1]
    motion_stopped(fader)
    start_pir()


def motion_stopped(fader):
    global ledstrip
    if ledstrip.enabled:
        print('fading out')
        fader.fade_out(ledstrip.r, ledstrip.g, ledstrip.b)


def pir_handler(args):
    global fadeout_timer
    pir = args[0]
    fader = args[1]

    stop_pir()

    pir_value = pir()
    utime.sleep_ms(200)
    if pir_value == pir() and pir_value is 0:
        print('motion detected')
        motion_started(fader)
        fadeout_timer = Timer.Alarm(fadeout_timer_handler, 10, arg=args)
    else:
        print('false positive - motion not detected')
        start_pir()


def start_pir():
    global pir
    print('starting PIR')
    pir.callback(Pin.IRQ_FALLING, pir_handler, (pir, fader))

def stop_pir():
    global pir
    global fadeout_timer
    if fadeout_timer is not None:
        fadeout_timer.cancel()
        fadeout_timer = None
    print('stopping PIR')
    pir.callback(Pin.IRQ_FALLING, None)

if ledstrip.fading:
    motion_stopped(fader)
    start_pir()
