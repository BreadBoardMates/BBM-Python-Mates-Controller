import time
import sys
import psutil
import socket
# import fcntl
import struct
import uptime
# from gpiozero import CPUTemperature
from mates.controller import MatesController
# import mates_data
from mates.constants import MatesWidget


def up():
    t = uptime.uptime()
    days = 0
    hours = 0
    min = 0
    out = ''
    while t > 86400:
        t -= 86400
        days += 1
    while t > 3600:
        t -= 3600
        hours += 1
    while t > 60:
        t -= 60
        min += 1
    out += str(days) + 'd '
    out += str(hours) + 'h '
    out += str(min) + 'm'
    return out


def get_interface_ipaddress(network):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915,
                                struct.pack('256s',
                                network[:15].encode('utf-8')))[20:24])  # SIOCGIFADDR
    except:
        return '0.0.0.0'


if __name__ == '__main__':

    mates = MatesController('COM10')

    mates.begin(9600)

    global gtime
    gtime = up()
    global lastCpuUse
    lastCpuUse = 0
    global lastTemp
    lastTemp = 0
    global lastlTemp
    lastlTemp = 0
    global lastRamUse
    lastRamUse = 0
    global lastWIPaddr
    lastWIPaddr = '0.0.0.0'
    global lastEIPaddr
    lastEIPaddr = '0.0.0.0'

    mates.updateTextArea(5, gtime, True)
    # cpu = CPUTemperature()
    # lastlTemp = int(cpu.temperature * 10)

    IPinterval = 0

    while True:
        # cpu = CPUTemperature()
        # gcpu = int(cpu.temperature)
        # lcpu = int(cpu.temperature * 10)
        cpuuse = int(psutil.cpu_percent())
        ramuse = int(psutil.virtual_memory().percent)

        if cpuuse < lastCpuUse:
            lastCpuUse = lastCpuUse - (1 + (lastCpuUse - cpuuse > 9))
        if cpuuse > lastCpuUse:
            lastCpuUse = lastCpuUse + 1 + (cpuuse - lastCpuUse > 9)
        # if gcpu < lastTemp:
        #     lastTemp = lastTemp - (1 + (lastTemp - gcpu > 9))
        # if gcpu > lastTemp:
        #     lastTemp = lastTemp + 1 + (gcpu - lastTemp > 9)
        # if lcpu < lastlTemp:
        #     lastlTemp = lastlTemp - 1
        # if lcpu > lastlTemp:
        #     lastlTemp = lastlTemp + 1
        if ramuse < lastRamUse:
            lastRamUse = lastRamUse - (1 + (lastRamUse - ramuse > 9))
        if ramuse > lastRamUse:
            lastRamUse = lastRamUse + 1 + (ramuse - lastRamUse > 9)

        # if gcpu != lastTemp:
        #     mates.setWidgetValueByIndex(MatesWidget.MATES_MEDIA_GAUGE_B,
        #             0, lastTemp)
        # if lcpu != lastlTemp:
        #     mates.setLedDigitsValueInt16(0, lastlTemp)
        if cpuuse != lastCpuUse:
            mates.setWidgetValueByIndex(MatesWidget.MATES_MEDIA_GAUGE_B,
                    1, lastCpuUse)
            mates.setLedDigitsValueInt16(1, lastCpuUse)
        if ramuse != lastRamUse:
            mates.setWidgetValueByIndex(MatesWidget.MATES_MEDIA_GAUGE_B,
                    2, lastRamUse)
            mates.setLedDigitsValueInt16(2, lastRamUse)

        if IPinterval > 20:
            tempIPaddr = get_interface_ipaddress('eth0')
            if tempIPaddr != lastEIPaddr:
                mates.updateTextArea(1, tempIPaddr, True)
                lastEIPaddr = tempIPaddr

            tempIPaddr = get_interface_ipaddress('wlan0')
            if tempIPaddr != lastWIPaddr:
                mates.updateTextArea(3, tempIPaddr, True)
                lastWIPaddr = tempIPaddr
            IPinterval = 0

        IPinterval = IPinterval + 1
        time.sleep(0.060)

        tempTime = up()
        if tempTime != gtime:
            mates.updateTextArea(5, tempTime, True)
            gtime = tempTime
        time.sleep(0.040)
