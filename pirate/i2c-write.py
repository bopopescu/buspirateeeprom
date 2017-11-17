#!/usr/bin/env python
# encoding: utf-8
"""
Adapted from i2c-test.py from Peter Huewe
"""
import sys
from pyBusPirateLite.I2C import *
import argparse
import time

def i2c_write_byte(address, data):
    haddress = address >> 8;
    laddress = address&0xff
    i2c.send_start_bit()
    i2c.bulk_trans(1, [0xa0])
    i2c.bulk_trans(1, [haddress])
    i2c.bulk_trans(1, [laddress])
    i2c.bulk_trans(1, [ord(data)])
#    print "data: %s" % hex(ord(data))
#    print "address: %s" % hex(address)
#    print "haddress: %s" % hex(haddress)
#    print "lhaddress: %s" % hex(laddress)
    i2c.send_stop_bit()


def i2c_read_bytes(address, numbytes, ret=False):
    data_out=[]
    i2c.send_start_bit()
    i2c.bulk_trans(len(address),address)
    while numbytes > 0:
        if not ret:
            print ord(i2c.read_byte())
        else:
            data_out.append(ord(i2c.read_byte()))
        if numbytes > 1:
            i2c.send_ack()
        numbytes-=1
    i2c.send_nack()
    i2c.send_stop_bit()
    if ret:
        return data_out

if __name__ == '__main__':
    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument("-i", "--input", dest="inputfile", metavar="INPUTFILE", type=argparse.FileType('rb'),
            required=True)
    parser.add_argument("-p", "--serial-port", dest="bp", default="/dev/ttyUSB0")
    parser.add_argument("-s", "--size", dest="size", type=int, required=True)
    parser.add_argument("-S", "--serial-speed", dest="speed", default=115200, type=int)
    parser.add_argument("-b", "--block-size", dest="bsize", default=256, type=int)

    args = parser.parse_args(sys.argv[1:])

    i2c = I2C(args.bp, args.speed)
    print "Entering binmode: ",
    if i2c.BBmode():
        print "OK."
    else:
        print "failed."
        sys.exit()

    print "Entering raw I2C mode: ",
    if i2c.enter_I2C():
        print "OK."
    else:
        print "failed."
        sys.exit()
        
    print "Configuring I2C."
    if not i2c.cfg_pins(I2CPins.POWER | I2CPins.PULLUPS):
        print "Failed to set I2C peripherals."
        sys.exit()
    if not i2c.set_speed(I2CSpeed._400KHZ):
        print "Failed to set I2C Speed."
        sys.exit()
    i2c.timeout(1)
    
    print "Writing %d bytes out of the EEPROM." % args.size

   
    # Start dumping
#    for block in range(0, args.size, args.bsize):
    i = 0
    for i in range(0, args.size):
        print i
        i2c_write_byte(i, args.inputfile.read(1))
    args.inputfile.close()

    print "Reset Bus Pirate to user terminal: "
    if i2c.resetBP():
        print "OK."
    else:
        print "failed."
        sys.exit()

