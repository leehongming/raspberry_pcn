#!/usr/bin/python3
# -*- coding: utf-8 -*-
import serial
import sys,getopt
import time

def SerialTx(device,cmd,timeout=0,read_buf=1000):
    """
    Send command to WR node.

    :param device: device should be like /dev/ttyUSB0
    :returns:
        "null" : error happens
        others : read from WR node
    """
    try:
        ser = serial.Serial(device,115200,timeout=0.5)
        if ser.isOpen():
            mes = cmd+"\r"
            i = 0
            while mes[i]!="\r":
                ser.write(mes[i].encode('utf-8'))
                time.sleep(0.05)
                i+=1
            ser.write("\r".encode('utf-8'))
            time.sleep(timeout)
            temp=ser.read(read_buf)
            return(temp.decode('utf-8'))
        else:
            print("Serial Open Error")
            return ("null")
    except Exception as e:
        print e
        return temp
    
def SerialTxEsc(device):
    """
    Send the "ESC" to WR node.

    :param device: device should be like /dev/ttyUSB0
    :returns:
        0 : succeed to send out "ESC"
        1 : error happens
    """
    ser = serial.Serial(device,115200,timeout=0.5)
    ESC = b"\x1b"
    if ser.isOpen():
        ser.write(ESC)
        # print("Send out the ESC command")
        time.sleep(0.1)
        ser.write("\r".encode('utf-8'))
        time.sleep(0.5)
        return 0
    else:
        print("Serial Open Error")
        return 1

def main():
    """
    Send the command to WRPC through UART.
    Usage:
        send out normal command:
            sudo ./SerialTx.py -c "cmd"
        send out "ESC"
        sudo ./SerialTx.py -e
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:e")
    except getopt.GetoptError:
        sys.exit()
    if len(opts) == 0:
        sys.exit()
    operation=opts[0]
    cmd = operation[0]
    value = operation[1]
    if cmd in ("-c","c","--c"):
        # print(SerialTx("/dev/ttyUSB0",value,1))
        print(SerialTx("/dev/ttyAMA0",value,1.1,1000))
    else:
        #SerialTxEsc("/dev/ttyUSB0")
        SerialTxEsc("/dev/ttyAMA0")
        
if __name__ == "__main__":
    main()
