#!/usr/bin/python3
import sys,getopt
import time
# import wrn 
# import tdc
# import numpy
# import configparser

def usage():
    """
    Usage of PCN Normal Calibration
    """
    print(" ")
    print("PCN normal calibration mode.")
    print(" ")
    print("-h, --help")
    print("      Print out usage of this program.")
    print(" ")
    print("-m, --mode")
    print("      Choose the work mode.")
    print("      0 : using default value.")
    print("      1 : do some extra process to get current value.")
    print("      default value is 0")
    print("")
    print("-r, --role")
    print("      Choose the wrn role")
    print("      0 : wrn is in slave  mode.")
    print("      1 : wrn is in master mode.")
    print("      default value is 0")
    print("")

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
            self.wrn_ip = int(config.get('LOG','wrn_ip'))%256
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
            self.wrn_ip = 0
        self.pcn = wrn.wrn("pcn")
        self.wrn_role = wrn_role
        self.wrn = wrn.wrn(wrn_role)
        self.tdc = tdc.tdc()

    def tdc_reset(self):
        return (self.tdc.restart())

    
    #Todo
    #Need to consider the ch1_input_delay and ch2_input_delay
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
                print len(calc_rise_list)
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
        
        calc_rise_diff = calc_rise_diff // self.loop_num + self.ch1_input_delay - self.ch2_input_delay
        calc_fall_diff = calc_fall_diff // self.loop_num + self.ch1_input_delay - self.ch2_input_delay

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
            delay_mm, delay_ms, delay_sm = self.pcn.get_link_delay()
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
        self.tdc_reset()
        time.sleep(1)
        timeout = 0
        print "do_veri"
        while(abs(self.do_verification())>self.calib_threshold):
            if self.wrn_role=="slave":
                self.wrn.restart(True)
            else:
                self.pcn.restart(True)
            time.sleep(1)
            if timeout<5:
                timeout += 1
            else:
                return 1


        config = configparser.ConfigParser()
        config['LOG'] = {'wrn_ip' : wrn_ip+1}
        with open('config/pcn_normal_calibration.ini','w') as configfile:
            config.write(configfile)        
        

        wrn_log_index = str(wrn_ip+1)
        config[wrn_log_index] ={
                        'wrn_sfp0_pn': self.wrn.sfp0_pn,
                        'wrn_sfp0_tx': self.wrn.sfp0_tx,
                        'wrn_sfp0_rx': self.wrn.sfp0_rx,
                        'wrn_sfp0_alpha'  : self.wrn.sfp0_alpha
                        }
                        
        with open('config/calibration_log.ini','w') as configfile:
            config.write(configfile)
        print("Calibration has finished!")

        return 0




def main():
    """
    NAME:
        Portable calibration node normal calibration mode.

    SYNOPSIS:
        ./pcn_normal_calibration.py [-h] [-m mode] [-r role]
    
    DESCRIPTION:
        This script is used for portable calibration node. It 
        has two parameter to choose.The parameter "mode" decides 
        the calibration mode and the parameter "role" decides 
        the wrn mode in pcn. 

    OPTIONS:
        -h, --help
              print out usage of this program.
         
        -m, --mode
              Choose the work mode.
              0 : using default value.
              1 : do some extra process to get current TDC parameter.
              default value is 0
        
        -r, --role
              Choose the wrn role
              0 : wrn is in slave  mode.
              1 : wrn is in master mode.
              default value is 0
        
    """  
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hm:r:",["help","mode ","role "])
    except getopt.GetoptError:
        usage()
        sys.exit()
    if len(opts) == 0:
        print("Running in default mode.")
    else:
        for opt,value in opts:
            if opt in ("-h","--help"):
                usage()
                sys.exit()
            if opt in ("-m","--mode"):
                mode = int(value)
                if mode==0:
                    print("Using default TDC paremeter.")
                elif mode==1:
                    print("Enter TDC parameter test.")
                else:
                    print("Wrong mode parameter") 
                    usage()

            if opt in ("-r","--role"):
                if int(value)==0:
                    print ("Wrn is in slave mode")
                    wrn_role="slave"
                elif int(value)==1:
                    print ("Wrn is in master mode")
                    wrn_role="master"
                else :
                    print ("Wrong role parameter")
                    sys.exit()

    if (not ('mode' in dir())):
        mode = 0
        print("Using default TDC paremeter.")

    if (not ('role' in dir())):
        wrn_role = "slave"
        print ("Wrn is in slave mode")


    if mode == 0:    
        calib = pcn_normal_calibration(wrn_role)
        calib.do_calibration()

    elif mode == 1:
        print ("")
    
    else:
        pass
    
    # #calib.pre_calibration()
    # calib.do_calibration()
    # # calib.tdc_reset()
    # #calib.do_verification()

if __name__ == '__main__':
    main()

