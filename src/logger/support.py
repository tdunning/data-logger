import webrepl
import network
import machine
import socket
import json

import time
import onewire, ds18x20

import wlan


def wakeWifi:
    wlan = network.WLAN(network.STA_IF) # create station interface
    wlan.active(True)       # activate the interface

def getConfig:
    machine = hexify(machine.unique_id())
    return ujson.loads(http_get("http://%s/%s" % (host, machine)))

def readTemps():
    # the device is on GPIO12
    dat = machine.Pin(12)

    # create the onewire object
    ds = ds18x20.DS18X20(onewire.OneWire(dat))

    ds.convert_temp()
    time.sleep_ms(750)
    for t in ds.scan():
        yield (t,ds.read_temp(t))

def reportTemps(temps):
    machine = hexify(machine.unique_id())
    for t,v in temps:
        sensor = hexify(t)
        http_get("http://%s/data/%s/%s/%s" % (host, machine, sensor, v))

def http_get(host, path):
    addr = socket.getaddrinfo(host, 80)[0][-1]
    s = socket.socket()
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
    data = s.recv(10000)
    s.close()
    return data

def hexify(b):
    "".join("%02x" % x for x in b)



def deepSleep(ms):
    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, ms)
    # put the device to sleep
    machine.deepsleep()

### go to  http://micropython.org/webrepl/ and enter IP to access REPL
def repl():
    wlan = network.WLAN(network.STA_IF)
    webrepl.start()
