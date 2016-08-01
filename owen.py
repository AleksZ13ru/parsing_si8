#!/usr/bin/python

import convert
import sys
import serial
import ctypes
from ctypes import *

# raspberrypi
# lib = ctypes.CDLL('./ownpi.so')
# x86
lib = ctypes.CDLL('./own.dll')

debug = 0
maxFrameSize = c_size_t(21)
maxAsciiFrameSize = c_size_t(45)


def ReadSI(adr, adrLen, datasize, name, port):
    maxdata = 15
    DATA = (c_ubyte * maxdata)()
    address = c_ushort(adr)
    addrLen = c_ushort(adrLen)
    req = 1
    request = c_int(req)
    dataSize = c_size_t(datasize)
    data = DATA
    crc = c_ushort(0)
    crc_ok = c_int(0)
    id = '0x00'
    # name = 'DCNT'
    lib.name2id(name, len(name), id)
    hash = lib.id2hash(id)
    frame = (c_ubyte * 21)()
    frameSize = c_size_t(0)

    '''
    print address
    print addrLen
    print request
    print hash
    print dataSize
    print data
    print crc
    print crc_ok
    print frame
    print maxFrameSize
    '''
    frameSize = lib.packFrame(address, addrLen, request, hash, dataSize, data, crc, crc_ok, frame, maxFrameSize)

    tempframeAscii = (c_ubyte * 45)()

    lib.packFrameToAscii(frame, frameSize, tempframeAscii, maxAsciiFrameSize)
    framenotzero = 0
    incr = 0
    for i in tempframeAscii:

        if i == 0:
            framenotzero = incr
            break
        incr = incr + 1

    frameAscii = (c_ubyte * framenotzero)()
    for i in range(0, framenotzero):
        frameAscii[i] = tempframeAscii[i]

    lenascii = len(frameAscii)

    if not port.isOpen: port.open()

    if port.isOpen:

        reading = ''
        port.write("".join(chr(h) for h in frameAscii))
        for j in range(0, 21):
            read1 = port.read(1)
            if read1 != 13:
                reading = reading + read1
            else:
                reading = reading + read1
                break

    print(reading)
    response = reading
    frameAsciiRecv = reading,

    ll = len(response) + 2
    AsciiRecv = (c_char * ll)()

    for i in range(0, ll - 2):
        AsciiRecv[i] = response[i]

    recvsize = c_size_t(0)
    xx = lib.frameAsciiRS(AsciiRecv, recvsize)
    for i in AsciiRecv:
        # print(i)
        pass

    xyz = (c_ubyte * (xx + 8))()

    x1 = len(AsciiRecv) - 2

    lib.unpackAsciiFrame(AsciiRecv, x1, xyz, maxFrameSize)

    x2 = (x1 - 2) / 2
    lib.unpackFrame(xyz, x2, address, adrLen, request, hash, dataSize, data, crc, crc_ok)
    for i in AsciiRecv:
        # print(i)
        pass
    Count = convert.BCD(data)

    if debug: print("Value counter = " + str(Count))
    return Count


def ReadSI8(adr, len, size, name):
    try:
        port = serial.Serial(
            port='COM4',
            baudrate=4800,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2

        )

        R = ReadSI(adr, len, size, name, port)
        port.close()
        return R
    except:
        pass
