#!/usr/bin/python3
import RPi.GPIO as gpio

##  GPIO parameters
MEAS_START_PIN  = 36
MEAS_FINISH_PIN = 37

def gpio_init():
    """ 
    GPIO init. Set the direction of each pin.
    
    :param Null
    :returns: Null 
    """
    gpio.setwarnings(False)
    gpio.setmode(gpio.BOARD)
    gpio.setup(MEAS_START_PIN,gpio.OUT)
    gpio.setup(MEAS_FINISH_PIN,gpio.IN)

def tdc_meas_start():
    """
    start the TDC measurement.
    
    ;param Null
    :returns: Null 
    """
    gpio.output(MEAS_START_PIN,gpio.HIGH)
    gpio.output(MEAS_START_PIN,gpio.LOW)

def tdc_meas_finish():
    """ 
    The status of selected TDC channel fifo.
    
    :param Null
    :returns:
        1 : fifo is empty
        0 : fifo has some data to be read 
    """
    return(gpio.input(MEAS_FINISH_PIN))

def main():
    gpio_init()
    tdc_meas_start()
    print(tdc_meas_finish())

if __name__ == '__main__':
    main()


