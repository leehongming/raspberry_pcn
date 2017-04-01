#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import lib.SerialTx as uart
import time

class wrn(object):
    """
    WR node abstract. 
    The PCN and node under calibration are all WR nodes with almost the same WRPC.
    """
    def __init__(self, role):
        super(wrn, self).__init__()
        self.role = role
        if role == 'pcn':
            self.device = "/dev/ttyAMA0"
        else:
            self.device = "/dev/ttyUSB0"
        self.sfp0_pn    = "AXGE-1254-0531"
        self.sfp0_tx    = 0
        self.sfp0_rx    = 0
        self.sfp0_alpha = 0
        self.sfp1_pn    = "AXGE-3454-0531"
        self.sfp1_tx    = 0
        self.sfp1_rx    = 0
        self.sfp1_alpha = 0

    def get_sfp_info(self,dualport=True):
        """
        Read the sfp info through uart.

        :param null
        :returns:
            0 : everything is ok
            1 : error happens
        """
        if(uart.SerialTxEsc(self.device)):
            return 1

        # Todo
        # Get SFP0&SFP1 pn from sfp match
        # uart_output = (uart.SerialTx(self.device,"sfp match")).split("\n")
        # sfp0_info_pn = ""
        # sfp1_info_pn = ""        
        # if (dualport):
        #     sfp1_info_pn = uart_output.split("\n")[4]
        #     print(sfp1_info_pn)
        #     sfp1_info_pn = sfp0_info_pn[sfp0_info_pn.find(":"):]
        
        uart_output = uart.SerialTx(self.device,"sfp show")
        
        # Todo
        # Add sfp pn check
        if uart_output == "null":
            return 1
        else:
            for sfp_info in uart_output.split("\n"):
                if "PN" in sfp_info:
                    sfp_info_tmp = sfp_info[sfp_info.find("PN:")+3:]
                    sfp_info_pn = sfp_info_tmp[:sfp_info_tmp.find(" ")].strip()
                    if "port" in sfp_info_tmp:
                        sfp_info_port = int(sfp_info_tmp[sfp_info_tmp.find("port:")+5:sfp_info_tmp.find("dTx:")].strip())
                    else:
                        sfp_info_port = 0
                    sfp_info_dTx = int(sfp_info_tmp[sfp_info_tmp.find("dTx:")+4:sfp_info_tmp.find("dRx:")].strip())
                    sfp_info_dRx = int(sfp_info_tmp[sfp_info_tmp.find("dRx:")+4:sfp_info_tmp.find("alpha:")].strip())
                    sfp_info_alpha = int(sfp_info_tmp[sfp_info_tmp.find("alpha")+6:].strip())
                    if sfp_info_port == 0:
                        if len(sfp_info_pn)>2:
                            self.sfp0_pn    = sfp_info_pn
                        self.sfp0_tx    = sfp_info_dTx
                        self.sfp0_rx    = sfp_info_dRx
                        self.sfp0_alpha = sfp_info_alpha
                    else:
                        if len(sfp_info_pn)>2:
                            self.sfp1_pn    = sfp_info_pn
                        self.sfp1_tx    = sfp_info_dTx
                        self.sfp1_rx    = sfp_info_dRx
                        self.sfp1_alpha = sfp_info_alpha
            return 0

    def set_sfp_info(self,port=0):
        """
        reset the sfp database and set the new value

        :param null
        :returns:
            0 : everything is ok
            1 : error happens
        """
        if(uart.SerialTxEsc(self.device)):
            return 1
        if(port==0):
            sfp_add_sentence = "sfp add "+self.sfp0_pn+" "+str(self.sfp0_tx)+" "+str(self.sfp0_rx)+" "+str(self.sfp0_alpha)
            uart.SerialTx(self.device,sfp_add_sentence)
        elif(port==1):
            sfp_add_sentence = "sfp add "+self.sfp1_pn+" "+str(self.sfp1_tx)+" "+str(self.sfp1_rx)+" "+str(self.sfp1_alpha)+" 1"
            uart.SerialTx(self.device,sfp_add_sentence)
        else:
            print("Port is invalid.")
            return 1
        print(uart.SerialTx(self.device,"sfp show"))
        return 0

    def erase_sfp_info(self):
        """
        reset the sfp database and set the new value

        :param null
        :returns:
            0 : everything is ok
            1 : error happens
        """
        if(uart.SerialTxEsc(self.device)):
            return 1
        uart_read = uart.SerialTx(self.device,"sfp erase")
        return 0

    def restart(self,check_status=False):
        """
        restart the WRPC in WR node.

        :param null
        :returns:
            0 : everything is ok
            1 : error happens
        """
        if (uart.SerialTxEsc(self.device)):
            return 1
        # Restart the LM32 software
        # Todo
        # Bug: after running "init boot", the slave cannot sync to master
        print(uart.SerialTx(self.device,"init boot"))


        time.sleep(10)
        
        if (check_status):
            timeout = 0
            sync_state = "IDLE"
            while (not ("TRACK_PHASE" in sync_state)):
                print "wait sync..."
                timeout += 1
                sync_state = self.get_sync_state()
                if (timeout>80):
                    print("The synchronization cannot be achieved.")
                    return 1
                else:
                    timeout+=1
            print("Restart the device "+str(self.role))
        return 0

    def get_sync_state(self):
        if (uart.SerialTxEsc(self.device)):
            return ("null")

        # Get sync state through command "stat"
        state_output = uart.SerialTx(self.device,"stat",1.2,1000)
        # turn off the stat statistics
        uart.SerialTx(self.device,"stat",0.2,200)

        if len(state_output)>50:
            return state_output
        return ("null")

    def get_link_delay(self):

        # Get sync state through command "stat"
        link_delay_output = uart.SerialTx(self.device,"stat",1.2,1000)
        # turn off the stat statistics
        uart.SerialTx(self.device,"stat",0.2,200)
        # Todo
        # Get delayMM/delayMS/delaySM from WRPC, bitslide has been removed.
        link_info = (link_delay_output.split("lnk")[1]).split(" ")
        print link_info
        delay_mm = int((link_info[9].split(":"))[1])
        delay_ms = int((link_info[10].split(":"))[1])
        delay_sm = delay_mm-delay_ms
        return delay_mm,delay_ms,delay_sm

def main():
    wrn_pcn = wrn("wrn")
    # wrn_pcn.get_sync_state()
    # wrn_pcn.get_sfp_info()
    #wrn_pcn.restart(True)
    print wrn_pcn.get_link_delay()
    # print(wrn_pcn.sfp0_pn)
    # print(wrn_pcn.sfp0_tx)
    # print(wrn_pcn.sfp0_rx)
    # print(wrn_pcn.sfp0_alpha)
    # print(wrn_pcn.sfp1_pn)
    # print(wrn_pcn.sfp1_tx)
    # print(wrn_pcn.sfp1_rx)
    # print(wrn_pcn.sfp1_alpha)
    # wrn_pcn.set_sfp_info()

if __name__ == "__main__":
    main()
