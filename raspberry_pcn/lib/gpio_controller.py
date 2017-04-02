#!/usr/bin/python3
import RPi.GPIO as gpio
import time

##  GPIO parameters
MEAS_START_PIN  = 15
MEAS_EMPTY_PIN = 13
MEAS_FULL_PIN = 10

def gpio_init():
    """ 
    GPIO init. Set the direction of each pin.
    
    :param Null
    :returns: Null 
    """
    gpio.setwarnings(False)
    gpio.setmode(gpio.BOARD)
    gpio.setup(MEAS_START_PIN,gpio.OUT)
    gpio.setup(MEAS_EMPTY_PIN,gpio.IN)
    gpio.setup(MEAS_FULL_PIN,gpio.IN)

def tdc_meas_start():
    """
    start the TDC measurement.
    
    ;param Null
    :returns: 
        0: Data is enough
        1: Data is not enough
    """
    gpio.output(MEAS_START_PIN,gpio.HIGH)
    time.sleep(2)
    gpio.output(MEAS_START_PIN,gpio.LOW)
    if (gpio.input(MEAS_FULL_PIN) == 1):
        return 0
    else 
        return 1

def tdc_meas_finish():
    """ 
    The status of selected TDC channel fifo.
    
    :param Null
    :returns:
        1 : fifo is empty
        0 : fifo has some data to be read 
    """
    return(gpio.input(MEAS_EMPTY_PIN))

def main():
    gpio_init()
    tdc_meas_start()
    print(tdc_meas_finish())

if __name__ == '__main__':
    main()


