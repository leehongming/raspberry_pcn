#!/usr/bin/python3
import sys
import spidev
sys.path.append("..")
import lib.gpio_controller as gpio
import time

class spi_controller(object):
    """
    spi controller for raspberry spi bus to 
    control the CUTEWR-DP PCN board.
    """
    def __init__(self):
        super(spi_controller, self).__init__()
        ## TDC channel information
        self.tdc_max_channel = 4

        ## Timestamp information
        self.timestamp_len = 5 # bytes
        self.timestamp_fine_len = 12
        self.timestamp_coarse_len = 27
        self.timestamp_polarity_loc = 40
        self.timestamp_coarse_period = 8000 #ps

        ## SPI device setting
        spi_bus=0
        spi_device=0
        self.spi_controller = spidev.SpiDev(spi_bus,spi_device)
        self.spi_controller.mode = 3

    def set_channel(self,channel):
        """
        Set which channel fifo to be read.

        :param channel: channel num 0~3
        :returns : current channel fifo status
            1: fifo is empty
            0: fifo has some data to be read 
        """
        spi_tx_data = (1<<channel)+(1<<(self.tdc_max_channel))
        self.spi_controller.writebytes([spi_tx_data])
        time.sleep(0.1)
        return(gpio.tdc_meas_finish())

    def read_channel(self,channel):
        """
        Read the channel fifo until it's empty.

        :param channel: channel num 0~3
        :returns: data list of current channel fifo.
        """
        channel_result_list=[]
        while (not gpio.tdc_meas_finish()):
            timestamp = self.spi_controller.readbytes(self.timestamp_len)
            
            timestamp_fine = 0
            timestamp_coarse = 0
            timestamp_tmp = 0
            for i in range(len(timestamp)):
                timestamp_tmp += timestamp[-i-1] << (8*i)
            timestamp_fine = timestamp_tmp & (2**self.timestamp_fine_len-1)
            timestamp_polarity = (timestamp_tmp & (1<<(self.timestamp_polarity_loc-1)))>>(self.timestamp_polarity_loc-1)
            timestamp_coarse =  (timestamp_tmp & ((1<<(self.timestamp_polarity_loc))-(1<<self.timestamp_fine_len)))>>self.timestamp_fine_len
            timestamp_full = \
                timestamp_coarse * self.timestamp_coarse_period + \
                ((timestamp_fine*self.timestamp_coarse_period)>>(self.timestamp_fine_len))
            # print(timestamp_full)
            channel_result_list.append(timestamp_full)
        return (channel_result_list)

def main():
    gpio.gpio_init()
    gpio.tdc_meas_start()
    spi_test = spi_controller()
    time.sleep(1)
    spi_test.set_channel(0)
    print(spi_test.read_channel(0))
    spi_test.set_channel(1)
    print(spi_test.read_channel(1))
    spi_test.set_channel(2)
    print(spi_test.read_channel(2))
    spi_test.set_channel(3)
    print(spi_test.read_channel(3))

if __name__ == '__main__':
    main()

