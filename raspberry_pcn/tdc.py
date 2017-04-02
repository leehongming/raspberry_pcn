#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import lib.spi_controller as spi
import lib.gpio_controller as gpio
import lib.SerialTx as uart
import time
import numpy

class tdc(object):
    """
    TDC abstract. 
    The PCN contains two TDC channels.
    """
    def __init__(self):
        super(tdc, self).__init__()
        self.device = "/dev/ttyAMA0"
        gpio.gpio_init()
        self.spi = spi.spi_controller()

    def restart(self):
        """
        restart the TDC in WR node, including the LUT

        :param null
        :returns:
            0 : everything is ok
            1 : error happens
        """
        if (uart.SerialTxEsc(self.device)):
            return 1
        uart.SerialTx(self.device,"tdc reset")
        time.sleep(0.1)
        print(uart.SerialTx(self.device,"tdc dnl",1))
        print(uart.SerialTx(self.device,"tdc inl",0.1))
        return 0

    def meas_start(self):
        """
        start TDC measurement.
        
        :param null
        :returns: null
        """
        tdc_cnt = 0
        while gpio.tdc_meas_start() == 1 :
            print ("TDC data is not enough")
            read_channel(0)
            read_channel(1)
            read_channel(2)
            read_channel(3)
            if tdc_cnt == 5:
                print "quit"
                sys.exit()
            tdc_cnt += 1 
            print ("Restart the tdc measure procedure d% times",tdc_cnt)    
        

    def debug_output(self):
        pass

    def read_channel(self,channel):
        """
        read the TDC measurement results through the SPI.

        :param channel: channel num 0~3
        :returns:
            TDC data list.
        """
        self.spi.set_channel(channel)
        return (self.spi.read_channel(channel))

    def calc_rise_diff(self):
        """
        calculate the PPS skew rise difference.

        :param null
        :returns:
            rise difference list
        """
        ch1_rise = self.read_channel(0)
        
        ch2_rise = self.read_channel(1)
        
        if (len(ch1_rise)==0) or (len(ch2_rise))==0:
            print("TDC readout error")
            return 0

        try:
            ch1_i=0
            ch2_i=0
            rise_diff_list=[]
            while True:
                rise_diff = ch1_rise[ch1_i] - ch2_rise[ch2_i]
                if abs(rise_diff)<50000000000: # 50ms
                    rise_diff_list.append(rise_diff)
                    ch1_i = ch1_i + 1
                    ch2_i = ch2_i + 1
                elif rise_diff>0:
                    if rise_diff>500000000000: # 0.5s
                        ch1_i = ch1_i + 1
                    else:
                        ch2_i = ch2_i + 1
                else:
                    if rise_diff<-500000000000:
                        ch2_i = ch2_i + 1
                    else:
                        ch1_i = ch1_i + 1
        except Exception as e:
            pass
        return rise_diff_list

    def calc_fall_diff(self):
        """
        calculate the PPS skew fall difference.

        :param null
        :returns:
            fall difference list
        """
        ch1_fall = self.read_channel(2)
        ch2_fall = self.read_channel(3)
        if (len(ch1_fall)==0) or (len(ch2_fall)==0):
            print("TDC readout error")
            return 

        try:
            ch1_i=0
            ch2_i=0
            fall_diff_list=[]
            while True:
                fall_diff = ch1_fall[ch1_i] - ch2_fall[ch2_i]
                if abs(fall_diff)<50000000000: # 50ms
                    fall_diff_list.append(fall_diff)
                    ch1_i = ch1_i + 1
                    ch2_i = ch2_i + 1
                elif fall_diff>0:
                    if fall_diff>500000000000: # 0.5s
                        ch1_i = ch1_i + 1
                    else:
                        ch2_i = ch2_i + 1
                else:
                    if fall_diff<-500000000000:
                        ch2_i = ch2_i + 1
                    else:
                        ch1_i = ch1_i + 1
        except Exception as e:
            pass
        return fall_diff_list

    
def main():
    test_tdc = tdc()
    test_tdc.meas_start()
    time.sleep(1)
    # print(test_tdc.read_channel(0))
    # print(test_tdc.read_channel(1))
    # print(test_tdc.read_channel(2))
    # print(test_tdc.read_channel(3))
    calc_rise_diff = test_tdc.calc_rise_diff()
    calc_fall_diff = test_tdc.calc_fall_diff()
    print(numpy.mean(calc_rise_diff),numpy.std(calc_rise_diff))
    #print(numpy.mean(calc_fall_diff),numpy.std(calc_fall_diff))

if __name__ == "__main__":
    main()
