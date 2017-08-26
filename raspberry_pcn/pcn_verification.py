#!/usr/bin/python3
import sys
import time

class pcn_verification(object):
    """
    PCN verification mode.
    """
    def __init__(self):
        super(pcn_verification, self).__init__()
        config = configparser.ConfigParser()
      	try:
            config.read('config/pcn_normal_calibration.ini')
            self.loop_num = int(config.get('DEFAULT','loop_num'))
            self.calib_threshold = int(config.get('DEFAULT','calib_threshold'))
            self.fibre_delay_rt = int(config.get('WR','fibre_delay_rt'))
            self.sfp0_pn = config.get('WR','sfp0_pn')
            self.sfp1_pn = config.get('WR','sfp1_pn')
            self.sfp0_tx = int(config.get('WR','sfp0_tx'))
            self.sfp0_rx = int(config.get('WR','sfp0_rx'))
            self.sfp0_alpha   = int(config.get('WR','sfp0_alpha'))
            self.sfp1_tx = int(config.get('WR','sfp1_tx'))
            self.sfp1_rx = int(config.get('WR','sfp1_rx'))
            self.sfp1_alpha   = int(config.get('WR','sfp1_alpha'))
            self.ch1_input_delay = int(config.get('TDC','ch1_input_delay'))
            self.ch2_input_delay = int(config.get('TDC','ch2_input_delay'))
        except:
            print("Read configuration file error, use default values.")
            self.loop_num = 1
            self.calib_threshold = 150
            self.fibre_delay_rt = 15000
            self.sfp0_pn = "SFP-GE-BX"
            self.sfp1_pn = "SFP-GE-BX"
            self.sfp0_tx = 232232
            self.sfp0_rx = 167768
            self.sfp1_tx = 175501
            self.sfp1_rx = 224399
            self.sfp0_alpha = 64398396
            self.sfp1_alpha = -64398396
            self.ch1_input_delay = 0
            self.ch2_input_delay = 0
        self.pcn = wrn.wrn("pcn")
        self.wrn_role = wrn_role
        self.wrn = wrn.wrn(wrn_role)
        self.tdc = tdc.tdc()

    def do_verification(self):
    	"""
		Verification mode.

		Check the mPPS skew between the clock of WR node and master clock of WR network.
    	"""


    	input("""
    Now you are in verification mode . 
	First of all, connect the PCN slave port to the top node of WR network.
	And then plug the mPPS signal of WRN and PCN to the TDC input port.
	Wait for several seconds and type in Enter to continue.""")

        calc_rise_diff = 0

        for i in range(self.loop_num):
            self.tdc.meas_start()
            time.sleep(1)
            calc_rise_list = self.tdc.calc_rise_diff()
            
            if len(calc_rise_list)>10:
                if (numpy.std(calc_rise_list)<50):
                    calc_rise_diff += numpy.mean(calc_rise_list)
                else:
                    print("The std %d of TDC rise measurement is too large!"%(numpy.std(calc_rise_list)))
                    return 0
            else:
                print("There are no enough TDC rise measurement results")
                return 0
                
        
        calc_rise_diff = (calc_rise_diff // self.loop_nu) + ch1_input_delay - ch2_input_delay

        print("The PPS skew between master and slave is %d"%(calc_rise_diff))

        verification_result = (abs(calc_rise_diff)>self.calib_threshold)
        
        if(verification_result):
        	print("The wrn is synchronous to the master clock")
        else:
        	print("THe wrn is not synchronous to the master clock")

        return verification_result

def main():

if __name__ == '__main__':
    main()

