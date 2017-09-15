#!/usr/bin/python3
import sys,getopt
import time
import wrn 
import tdc
import numpy
import configparser

def usage():
    """
    Usage of PCN Verification
    """
    print(" ")
    print("PCN verification mode.")
    print(" ")
    print("-h, --help")
    print("      Print out usage of this program.")
    print(" ")
    print("default")
    print("      Enter the verification mode")
    print(" ")
    
class pcn_verification(object):
    def __init__(self):
        super(pcn_verification, self).__init__()
        config = configparser.ConfigParser()
        try:
            config.read('config/pcn_normal_calibration.ini')
            self.loop_num = int(config.get('DEFAULT','loop_num'))
            self.calib_threshold = int(config.get('DEFAULT','calib_threshold'))
            self.ch1_input_delay = round(float(config.get('TDC','ch1_input_delay')))
            self.ch2_input_delay = round(float(config.get('TDC','ch2_input_delay')))
        except:
            print("Read configuration file error, use default values.")
            self.loop_num = 1
            self.calib_threshold = 150
            self.ch1_input_delay = 0
            self.ch2_input_delay = 0
        self.pcn = wrn.wrn("pcn")
        self.tdc = tdc.tdc()
        


    def tdc_reset(self):
        return (self.tdc.restart())

    
    def do_verification(self):
    	"""
		Verification mode.

		Check the mPPS skew between the clock of WR node and master clock of WR network.
    	"""
        try:
            input("""
        Now you are in verification mode . 
	First of all, connect the PCN slave port to the top node of WR network.
	And then plug the mPPS signal of WRN and PCN to the TDC input ports.
	Wait for several seconds and type in "1" and Enter to continue.""")
        except Exception as e:
            pass

        calc_rise_diff = 0

        for i in range(self.loop_num):
            self.tdc.meas_start()
            time.sleep(1)
            calc_rise_list = self.tdc.calc_rise_diff()
            calc_fall_diff = self.tdc.calc_fall_diff()
            if len(calc_rise_list)>10:
                if (numpy.std(calc_rise_list)<50):
                    calc_rise_diff += numpy.mean(calc_rise_list)
                else:
                    print("The std %d of TDC rise measurement is too large!"%(numpy.std(calc_rise_list)))
                    return 0
            else:
                print("There are no enough TDC rise measurement results")
                return 0
                        
        calc_rise_diff = (calc_rise_diff // self.loop_num) + self.ch1_input_delay - self.ch2_input_delay

        print("The PPS skew between master and slave is %d"%(calc_rise_diff))
        if((abs(calc_rise_diff)<self.calib_threshold)):
            print("The wrn is synchronous to the master clock")
        else:
            print("THe wrn is not synchronous to the master clock")

        return 0

def main():
    """
    NAME:
        Portable calibration node verification mode.

    SYNOPSIS:
        ./pcn_verification.py [] [-h]  
    
    DESCRIPTION:
        This script is used for portable calibration node. After connecting 
        the pcn to the top wr node in wr network, this script can can measure 
        the skew between wrn and pcn. And we can judge if the wr node work 
        correctly.  

    OPTIONS: 
        -h, --help
              print out usage of this program.
         
        default
              Enter the verification mode, measure the skew between wrn and pcn.
    """
    
    try:
        opts,args = getopt.getopt(sys.argv[1:],"h",["help"])
    except Exception as e:
        print e
        usage()
        sys.exit()
    else:
        for opt,value in opts:
            if opt in ('-h','--help'):
                usage()
                sys.exit()
            else:
                print "Wrong Parameter!"
                usage()
                sys.exit()
    
    verif = pcn_verification()
    verif.do_verification()
if __name__ == '__main__':
    main()

