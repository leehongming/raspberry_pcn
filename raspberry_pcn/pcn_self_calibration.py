#!/usr/bin/python3
import sys,getopt
import time
import wrn 
import tdc
import numpy
import configparser

def usage():
    """
    Usage of PCN Self Calibration
    """
    print(" ")
    print("PCN self calibration mode.")
    print(" ")
    print("-h, --help")
    print("      Print out usage of this program.")
    print(" ")
    print("-t")
    print("      Calibrate the TDC delay parameter.")
    print("")
    print("-w")
    print("      Calibrate the WR sfp delay parameter and fibre delay.")
    print("")
    print("-a")
    print("      Calibrate the WR and TDC parameter.")
    print("")

class pcn_self_calibration(object):
    """
    PCN self calibration mode.
    """
    def __init__(self):
        super(pcn_self_calibration, self).__init__()
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
            self.ch1_input_delay = round(float(config.get('TDC','ch1_input_delay')))
            self.ch2_input_delay = round(float(config.get('TDC','ch2_input_delay')))
            self.wrn_ip = int(config.get('LOG','wrn_ip'))%256
 
        except Exception as e:
            print e
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
            self.wrn_ip = 0
        self.pcn = wrn.wrn("pcn")
        self.tdc = tdc.tdc()

    def tdc_reset(self):
        return (self.tdc.restart())

    def save_data(self):
        """
            save pcn parameter to pcn_normal_calibration.ini
            
            save calibration log to calibration_log.ini
            
        """
        config = configparser.ConfigParser()
        config['LOG'] = {'wrn_ip' : (self.wrn_ip)+1}
        
        config['WR'] = {'fibre_delay_rt' : self.fibre_delay_rt,
                        'sfp0_pn': self.sfp0_pn,
                        'sfp1_pn': self.sfp1_pn,
                        'sfp0_tx': self.sfp0_tx,
                        'sfp0_rx': self.sfp0_rx,
                        'sfp1_tx': self.sfp1_tx,
                        'sfp1_rx': self.sfp1_rx,
                        'sfp0_alpha'  : self.sfp0_alpha,
                        "sfp1_alpha"  : self.sfp1_alpha
                        }
        
        config['TDC'] = {'ch1_input_delay' : self.ch1_input_delay,
                         'ch2_input_delay ': self.ch2_input_delay
                         }
        
        config['DEFAULT'] = {'calib_threshold' : self.calib_threshold,
                             'loop_num ': self.loop_num
                         }
        with open('config/pcn_normal_calibration.ini','w') as configfile:
            config.write(configfile)        

            
    def tdc_self_calibration(self):
        """
        The tdc_self_calibration is used to measure the delays of two TDC inputs, including 
        the fibre delay and circuit delay.
        """
        try:
            input("""
    L1 is chosen as the reference fibre in following calibration process.
    Now disconnect the PCN ports. Plug two mPPS signals of PCN into two TDC inputs.
    Wait for several seconds and type in Enter to continue.""")
        except Exception as e:
            pass
        
        # Todo
        # start the TDC.
        
        self.tdc.meas_start()
        # Todo
        # Measure the PPS skew
        tdc_rise_diff_list_1 = self.tdc.calc_rise_diff()
        ch1_input_delay = 0 
        ch1_ch2_diff_1 = numpy.mean(tdc_rise_diff_list_1)

        try:
            input("""
    Now exchange the two mPPS input signals.
    Wait for several seconds and type in Enter to continue.""")
        except Exception as e:
            pass

        # Todo
        # Measure the PPS skew again
        self.tdc.meas_start()
        tdc_rise_diff_list_2 = self.tdc.calc_rise_diff()
        ch1_ch2_diff_2 = numpy.mean(tdc_rise_diff_list_2)
        
        ch2_input_delay = ch1_input_delay - (ch1_ch2_diff_1+ch1_ch2_diff_2)//2
        self.ch1_input_delay=ch1_input_delay
        self.ch2_input_delay=ch2_input_delay
        print ch1_input_delay,ch2_input_delay
        self.save_data()
        
        print("""
    The TDC calibration has finished.""")

    def wr_self_calibration(self):
        """
        Calibration preparation.

        Determine several key parameters used in normal calibration mode.
        """
        try:
            input("""
    Now you are in calibration preparation phase. 
    Connect PCN master port and PCN slave port with fibre L1.
    L1 should be fibre of several meters.
    Wait for several seconds and type in Enter to continue.""")
        except:
            pass
    
        # Todo
        # Modify the PCN to get the delayMM, delay_ms, delay_sm.
        delay_info = self.pcn.get_link_delay()
        rt_delay_l1 = delay_info[0]
        rt_delay_l1_ms = delay_info[1]
        rt_delay_l1_sm = delay_info[2]

        try:
            input("""
    Connect PCN master port and PCN slave port with fibre L2. 
    L2 should be fibre whose length is above 1km.
    Wait for several seconds and type in Enter to continue.""")
        except Exception as e:
            pass
        
        delay_info = self.pcn.get_link_delay()
        rt_delay_l2 = delay_info[0]
        rt_delay_l2_ms = delay_info[1]
        rt_delay_l2_sm = delay_info[2]

        try:
            input("""
    Connect PCN master port and PCN slave port with fibre L1+L2. 
    Wait for several seconds and type in Enter to continue.""")
        except Exception as e:
            pass
        
        delay_info = self.pcn.get_link_delay()
        rt_delay_l1_l2 = delay_info[0]
        rt_delay_l1_l2_ms = delay_info[1]
        rt_delay_l1_l2_sm = delay_info[2]

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
            sfp0_pn = "AXGE-GE-BX"
            sfp1_pn = "AXGE-GE-BX"
            fixed_delay_asym_master = 0

        fixed_delay_asym_slave = fixed_delay_asym_master - fixed_delay_asym
        sfp0_tx = fixed_delay_sum//4 + fixed_delay_asym_master
        sfp0_rx = fixed_delay_sum//4 - fixed_delay_asym_master
        sfp1_tx = fixed_delay_sum//4 + fixed_delay_asym_slave
        sfp1_rx = fixed_delay_sum//4 - fixed_delay_asym_slave

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

        self.save_data()

        print("""
    The wr calibration prepration has finished.""")

    # def pre_calibration(self):
    #     """
    #     Calibration preparation.

    #     Determine several key parameters used in normal calibration mode.
    #     """
    #     input("""
    # Now you are in calibration preparation phase. 
    # Connect PCN master port and PCN slave port with fibre L1.
    # L1 should be fibre of several meters.
    # Wait for several seconds and type in Enter to continue.""")
    #     # Todo
    #     # Modify the PCN to get the delayMM, delay_ms, delay_sm.
    #     delay_info = self.pcn.get_link_delay()
    #     rt_delay_l1 = delay_info[0]
    #     rt_delay_l1_ms = delay_info[1]
    #     rt_delay_l1_sm = delay_info[2]

    #     input("""
    # Connect PCN master port and PCN slave port with fibre L2. 
    # L2 should be fibre whose length is above 1km.
    # Wait for several seconds and type in Enter to continue.""")
    #     delay_info = self.pcn.get_link_delay()
    #     rt_delay_l2 = delay_info[0]
    #     rt_delay_l2_ms = delay_info[1]
    #     rt_delay_l2_sm = delay_info[2]

    #     input("""
    # Connect PCN master port and PCN slave port with fibre L1+L2. 
    # Wait for several seconds and type in Enter to continue.""")
    #     delay_info = self.pcn.get_link_delay()
    #     rt_delay_l1_l2 = delay_info[0]
    #     rt_delay_l1_l2_ms = delay_info[1]
    #     rt_delay_l1_l2_sm = delay_info[2]

    #     # Todo
    #     # Get the exact L1 fibre delay.
    #     fibre_delay_rt = rt_delay_l1_l2 - rt_delay_l2
    #     # Get fixed delay summary
    #     fixed_delay_sum = rt_delay_l1 + rt_delay_l2 - rt_delay_l1_l2
    #     # Get fixed delay asymmetry between master&slave port of PCN
    #     fixed_delay_asym= (rt_delay_l1_ms + rt_delay_l2_ms - rt_delay_l1_l2_ms) - \
    #                       (rt_delay_l1_sm + rt_delay_l2_sm - rt_delay_l1_l2_sm)
    #     try:
    #         config.read('config/pcn_normal_calibration.ini')
    #         sfp0_pn = config.get('WR','sfp0_pn')
    #         sfp1_pn = config.get('WR','sfp1_pn')
    #         fixed_delay_asym_master = int(config.get('WR','fixed_delay_asym_master'))
    #     except:
    #         sfp0_pn = "AXGE-1254-0531"
    #         sfp1_pn = "AXGE-3454-0531"
    #         fixed_delay_asym_master = 0

    #     fixed_delay_asym_slave = fixed_delay_asym_master - fixed_delay_asym
    #     sfp0_tx = fixed_delay_sum//4 + fixed_delay_asym_master
    #     sfp0_rx = fixed_delay_sum//4 - fixed_delay_asym_master
    #     sfp1_tx = fixed_delay_sum//4 + fixed_delay_asym_slave
    #     sfp1_rx = fixed_delay_sum//4 - fixed_delay_asym_slave

    #     # Get alpha
    #     fibre_alpha = (float(rt_delay_l1_l2_ms - rt_delay_l1_ms) / float(rt_delay_l1_l2_sm - rt_delay_l1_sm)) - 1
    #     fibre_alpha_int = int(fibre_alpha * (2**40))
    #     sfp0_alpha = fibre_alpha_int
    #     sfp1_alpha = -fibre_alpha_int
    #     self.pcn.sfp0_pn    = sfp0_pn
    #     self.pcn.sfp0_tx    = sfp0_tx
    #     self.pcn.sfp0_rx    = sfp0_rx
    #     self.pcn.sfp0_alpha = sfp0_alpha
    #     self.pcn.sfp1_pn    = sfp1_pn
    #     self.pcn.sfp1_tx    = sfp1_tx
    #     self.pcn.sfp1_rx    = sfp1_rx
    #     self.pcn.sfp1_alpha = sfp1_alpha
        
    #     self.pcn.set_sfp_info(0)
    #     self.pcn.set_sfp_info(1)
    #     print("Update PCN sfp database.")

    #     input("""
    # L1 is chosen as the reference fibre in following calibration process.
    # Now disconnect the PCN ports. Plug two mPPS signals of PCN into two TDC inputs.
    # Wait for several seconds and type in Enter to continue.""")
    #     # Todo
    #     # start the TDC.
    #     self.tdc.meas_start()

    #     # Todo
    #     # Measure the PPS skew
    #     tdc_rise_diff_list_1 = self.tdc.calc_rise_diff()
    #     #ch1_input_delay = 0 
    #     ch1_ch2_diff_1 = numpy.mean(tdc_rise_diff_list_1)

    #     input("""
    # Now exchange the two mPPS input signals.
    # Wait for several seconds and type in Enter to continue.""")

    #     # Todo
    #     # Measure the PPS skew again
    #     self.tdc.meas_start()
    #     tdc_rise_diff_list_2 = self.tdc.calc_rise_diff()
    #     ch1_ch2_diff_2 = numpy.mean(tdc_rise_diff_list_2)
        
    #     ch2_input_delay = ch1_input_delay - (ch1_ch2_diff_1+ch1_ch2_diff_2)//2

    #     config = configparser.ConfigParser()
    #     config['DEFAULT'] = {'loop_num':'2',
    #                          'calib_threshold':self.calib_threshold}
    #     config['WR'] = {'fibre_delay_rt' : fibre_delay_rt,
    #                     'fixed_delay_asym_master': fixed_delay_asym_master,
    #                     'fixed_delay_asym_slave' : fixed_delay_asym_slave,
    #                     'sfp0_pn': sfp0_pn,
    #                     'sfp1_pn': sfp1_pn,
    #                     'sfp0_tx': sfp0_tx,
    #                     'sfp0_rx': sfp0_rx,
    #                     'sfp1_tx': sfp1_tx,
    #                     'sfp1_rx': sfp1_rx,
    #                     'sfp0_alpha'  : sfp0_alpha,
    #                     "sfp1_alpha"  : sfp1_alpha
    #                     }
    #     config['TDC'] = {'ch1_input_delay':ch1_input_delay,
    #                      'ch2_input_delay':ch2_input_delay}
    #     with open('config/pcn_normal_calibration.ini','w') as configfile:
    #         config.write(configfile)

    #     print("""
    # The calibration prepration has finished.""")
    
def main():
    """
    NAME:
        Portable calibration node self calibration mode.

    SYNOPSIS:
        ./pcn_self_calibration.py [-h] [-w] [-t] [-tw]
    
    DESCRIPTION:
        This script is used for portable calibration node. Following some 
        steps and it can calculate some parameter automatically so that 
        it can calibrate wrns more accurately. And it can save those 
        parameter in pcn, you can use it next time.

    OPTIONS: 
        -h, --help
              print out usage of this program.
         
        -t
              Calibrate the TDC delay parameter.
        
        -w
              Calibrate the WR sfp delay parameter and fibre delay.
        
        -a
              Calibrate the WR and TDC parameter.
    """  

    try:
        opts, args = getopt.getopt(sys.argv[1:], "htwa",["help"])
    except getopt.GetoptError:
        usage()
        sys.exit()
    if len(opts) == 0:
        usage()
        sys.exit()
    else:
        for opt,value in opts:
            if opt in ("-h","--help"):
                usage()
                sys.exit()
            if opt in ("-t"):
                precalib=pcn_self_calibration()
                precalib.tdc_self_calibration()
            elif opt in ("-w"):
                precalib=pcn_self_calibration()
                precalib.wr_self_calibration()
            elif opt in ("-a"):
                precalib=pcn_self_calibration()
                precalib.tdc_self_calibration()
                precalib.wr_self_calibration()
            else:
                usage()
                sys.exit()

if __name__ == '__main__':
    main()

