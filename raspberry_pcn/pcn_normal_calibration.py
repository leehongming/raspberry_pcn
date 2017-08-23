#!/usr/bin/python3
import sys
import time
import wrn 
import tdc
import numpy
import configparser

class pcn_normal_calibration(object):
    """
    PCN normal calibration mode.
    """
    def __init__(self,wrn_role="slave"):
        super(pcn_normal_calibration, self).__init__()
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

    def tdc_reset(self):
        return (self.tdc.restart())

    def pre_calibration(self):
        """
        Calibration preparation.

        Determine several key parameters used in normal calibration mode.
        """
        input("""
    Now you are in calibration preparation phase. 
    Connect PCN master port and PCN slave port with fibre L1.
    L1 should be fibre of several meters.
    Wait for several seconds and type in Enter to continue.""")
        # Todo
        # Modify the PCN to get the delayMM, delay_ms, delay_sm.
        rt_delay_l1 = 0
        rt_delay_l1_sm = 200
        rt_delay_l1_ms = 200

        input("""
    Connect PCN master port and PCN slave port with fibre L2. 
    L2 should be fibre whose length is above 1km.
    Wait for several seconds and type in Enter to continue.""")
        rt_delay_l2 = 0
        rt_delay_l2_sm = 900
        rt_delay_l2_ms = 900

        input("""
    Connect PCN master port and PCN slave port with fibre L1+L2. 
    Wait for several seconds and type in Enter to continue.""")
        rt_delay_l1_l2 = 1
        rt_delay_l1_l2_sm = 1000
        rt_delay_l1_l2_ms = 1000

        # Todo
        # Get the exact L1 fibre delay.
        fibre_delay_rt = rt_delay_l1_l2 - rt_delay_l2
        # Get fixed delay summary
        fixed_delay_sum = rt_delay_l1 + rt_delay_l2 - rt_delay_l1_l2
        # Get fixed delay asymmetry between master&slave port of PCN
        fixed_delay_asym= (rt_delay_l1_ms + rt_delay_l2_ms - rt_delay_l1_l2_ms) - \
                          (rt_delay_l1_sm + rt_delay_l2_sm - rt_delay_l1_l2_sm)
        try:
            config.read('config/pcn_normal_calibration.ini')
            sfp0_pn = config.get('WR','sfp0_pn')
            sfp1_pn = config.get('WR','sfp1_pn')
            fixed_delay_asym_master = int(config.get('WR','fixed_delay_asym_master'))
        except:
            sfp0_pn = "AXGE-1254-0531"
            sfp1_pn = "AXGE-3454-0531"
            fixed_delay_asym_master = 0

        fixed_delay_asym_slave = fixed_delay_asym_master - fixed_delay_asym
        sfp0_tx = fixed_delay_sum//2 + fixed_delay_asym_master
        sfp0_rx = fixed_delay_sum//2 - fixed_delay_asym_master
        sfp1_tx = fixed_delay_sum//2 + fixed_delay_asym_slave
        sfp1_rx = fixed_delay_sum//2 - fixed_delay_asym_slave

        # Get alpha
        fibre_alpha = (float(rt_delay_l1_l2_ms - rt_delay_l1_ms) / float(rt_delay_l1_l2_sm - rt_delay_l1_sm)) - 1
        fibre_alpha_int = int(fibre_alpha * (2**40))
        sfp0_alpha = fibre_alpha_int
        sfp1_alpha = -fibre_alpha_int
        self.pcn.sfp0_pn    = sfp0_pn
        self.pcn.sfp0_tx    = sfp0_tx
        self.pcn.sfp0_rx    = sfp0_rx
        self.pcn.sfp0_alpha = sfp0_alpha
        self.pcn.sfp1_pn    = sfp1_pn
        self.pcn.sfp1_tx    = sfp1_tx
        self.pcn.sfp1_rx    = sfp1_rx
        self.pcn.sfp1_alpha = sfp1_alpha
        
        self.pcn.set_sfp_info(0)
        self.pcn.set_sfp_info(1)
        print("Update PCN sfp database.")

        input("""
    L1 is chosen as the reference fibre in following calibration process.
    Now disconnect the PCN ports. Plug two mPPS signals of PCN into two TDC inputs.
    Wait for several seconds and type in Enter to continue.""")
        # Todo
        # start the TDC.

        # Todo
        # Measure the PPS skew
        ch1_input_delay = 0
        ch1_ch2_diff_1 = 0

        input("""
    Now exchange the two mPPS input signals.
    Wait for several seconds and type in Enter to continue.""")

        # Todo
        # Measure the PPS skew again
        ch1_ch2_diff_2 = 0        

        ch2_input_delay = ch1_input_delay - (ch1_ch2_diff_1+ch1_ch2_diff_2)//2

        config = configparser.ConfigParser()
        config['DEFAULT'] = {'loop_num':'2',
                             'calib_threshold':self.calib_threshold}
        config['WR'] = {'fibre_delay_rt' : fibre_delay_rt,
                        'fixed_delay_asym_master': fixed_delay_asym_master,
                        'fixed_delay_asym_slave' : fixed_delay_asym_slave,
                        'sfp0_pn': sfp0_pn,
                        'sfp1_pn': sfp1_pn,
                        'sfp0_tx': sfp0_tx,
                        'sfp0_rx': sfp0_rx,
                        'sfp1_tx': sfp1_tx,
                        'sfp1_rx': sfp1_rx,
                        'sfp0_alpha'  : sfp0_alpha,
                        "sfp1_alpha"  : sfp1_alpha
                        }
        config['TDC'] = {'ch1_input_delay':ch1_input_delay,
                         'ch2_input_delay':ch2_input_delay}
        with open('config/pcn_normal_calibration.ini','w') as configfile:
            config.write(configfile)

        print("""
    The calibration prepration has finished.""")

    def do_calibration(self):
        
        ## WR information part
        self.wrn.get_sfp_info()
        if (self.wrn_role == "slave"):
            delay_mm, delay_ms, delay_sm = self.wrn.get_link_delay()
            self.wrn.sfp0_tx = (delay_mm - self.pcn.sfp1_tx - self.pcn.sfp1_rx - self.fibre_delay_rt) / 2
            self.wrn.sfp0_rx = (delay_mm - self.pcn.sfp1_tx - self.pcn.sfp1_rx - self.fibre_delay_rt) / 2
            # Reset the sfp database of wrn and restart wrn
            self.wrn.erase_sfp_info()
            self.wrn.set_sfp_info(0)
            self.wrn.set_sfp_info(1) # Avoid losing the SFP1 info
            if(self.wrn.restart(True)):
                return 1
        elif (self.wrn_role == "master"):
            # Todo
            # Should get the sync status through pcn
            delay_mm, delay_ms, delay_sm = self.wrn.get_link_delay()
            self.wrn.sfp1_tx = (delay_mm - self.pcn.sfp0_tx - self.pcn.sfp0_rx - self.fibre_delay_rt) / 2
            self.wrn.sfp1_rx = (delay_mm - self.pcn.sfp0_tx - self.pcn.sfp0_rx - self.fibre_delay_rt) / 2
            # Reset the sfp database of wrn and restart wrn
            self.wrn.erase_sfp_info()
            self.wrn.set_sfp_info(0) # Avoid losing the SFP0 info
            self.wrn.set_sfp_info(1) 
            if(self.pcn.restart(True)):
                return 1
        else:
            print("The wrn role is not valid.")
            return 1

        ## TDC measurement part
        # restart the TDC
        self.tdc_reset(self)
        time.sleep(1)
        timeout = 0
        while(abs(do_verification(self))>self.calib_threshold):
            if self.wrn_role=="slave":
                self.wrn.restart(True)
            else:
                self.pcn.restart(True)
            time.sleep(1)
            if timeout<5:
                timeout += 1
            else:
                return 1
        print("Calibration has finished!")
        return 0

    def do_verification(self):
        calc_rise_diff = 0
        calc_fall_diff = 0

        for i in range(self.loop_num):
            self.tdc.meas_start()
            time.sleep(1)
            calc_rise_list = self.tdc.calc_rise_diff()
            calc_fall_list = self.tdc.calc_fall_diff()
            
            if len(calc_rise_list)>10:
                if (numpy.std(calc_rise_list)<50):
                    calc_rise_diff += numpy.mean(calc_rise_list)
                else:
                    print("The std %d of TDC rise measurement is too large!"%(numpy.std(calc_rise_list)))
                    return 0
            else:
                print("There are no enough TDC rise measurement results")
                return 0
                
            if len(calc_fall_list)>10:
                if (numpy.std(calc_fall_list)<50):
                    calc_fall_diff += numpy.mean(calc_fall_list)
                else:
                    print("The std %d of TDC fall measurement is too large!"%(numpy.std(calc_fall_list)))
                    return 0
            else:
                print("There are no enough TDC fall measurement results!")
                return 0
        
        calc_rise_diff = calc_rise_diff // self.loop_num
        calc_fall_diff = calc_fall_diff // self.loop_num

        print("The PPS skew between master and slave is %d"%(calc_rise_diff))

        # Todo
        # Temporarily, only use rise diff
        if (self.wrn.get_sfp_info()):
            print("wrn sfp info readout error!")
            return 99999

        if abs(calc_rise_diff)>self.calib_threshold:
            if (self.wrn_role=="slave"):
                self.wrn.sfp0_tx    = self.wrn.sfp0_tx + calc_rise_diff
                self.wrn.sfp0_rx    = self.wrn.sfp0_rx - calc_rise_diff
                self.wrn.sfp0_alpha = self.wrn.sfp0_alpha
                self.wrn.erase_sfp_info()
                self.wrn.set_sfp_info(0)
                self.wrn.set_sfp_info(1)
            else:
                self.wrn.sfp1_tx    = self.wrn.sfp1_tx - calc_rise_diff
                self.wrn.sfp1_rx    = self.wrn.sfp1_rx + calc_rise_diff
                self.wrn.sfp1_alpha = self.wrn.sfp1_alpha
                self.wrn.erase_sfp_info()
                self.wrn.set_sfp_info(0)
                self.wrn.set_sfp_info(1)
        return calc_rise_diff

def main():
    calib = pcn_normal_calibration("slave")
    # calib.pre_calibration()
    # calib.do_calibration()
    # calib.tdc_reset()
    calib.do_verification()

if __name__ == '__main__':
    main()

