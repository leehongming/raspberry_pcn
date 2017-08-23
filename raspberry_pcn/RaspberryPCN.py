#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys,getopt
import time

ver_major = 0 # major version num
ver_minor = 1 # minor version num
ver_y = 2017  # year
ver_m = 8     # month 
ver_d = 21    # date

def usage():
    """
    Usage of RaspberryPCN.
    """
    print(" ")
    print("Project RaspberryPCN used for portable calibration node.")
    print(" ")
    print("-h, --help")
    print("      Print out usage of this program.")
    print(" ")
    print("-m    Choose the work mode.")
    print("      0:self-calibration mode.")
    print("      1:normal calibration mode.")
    print("      2:verification mode.")
    print(" ")
    print("-s    Choose the service offered by PCN.")
    print("      ssh : remote connect server through terminal.")
    print("      http: http server which can be accessed through browser.")
    print(" ")
    print("--ch1=local --ch2=remote")
    print("      Designate the source of each TDC input. 'local' means the PPS")
    print("      signal comes from the PCN itself, 'remote' means the PPS signal")
    print("      is from other WR nodes.")
    print(" ")
    print("--version")
    print("      Prints out this program version information.")
    print(" ")
    print("--test")
    print("      PCN works in test mode whose function is not fixed.")
    print("")

def version():
    """
    Version of RaspberryPCN.
    """    
    print("Raspberry PCN Ver:%d.%d,Compiled in %d.%d.%d"%(ver_major,ver_minor,ver_y,ver_m,ver_d))

def main():
    """
    NAME:
        Project RaspberryPCN used for portable calibration node.

    SYNOPSIS:
        ./RaspberryPCN.py [-h] [-m mode] [-s service]
                  [--ch1=local --ch2=remote]
                  [--version] [--test] [--help]
    
    DESCRIPTION:
        RaspberryPCN is used for portable calibration node, which is the
        combination of CUTEWR-DP and raspberry, to accomplish the calibr-
        ation work. It acts in three mode: self-calibration mode, normal
        calibration mode and verification mode.
        The CUTEWR-DP works in two ports cascade mode, in which port SFP0
        acts as the WR master while port SFP1 acts as the WR slave.The 
        function of each port is fixed. It also contains two TDC inputs to 
        measure the PPS skew between the PCN and other WR nodes to be cali-
        brated. The options ch1 && ch2 are used to designate the source of 
        each TDC input.
        The raspberry runs the python program to control the CUTEWR-DP 
        through GPIO and SPI interface. The user can run the python program 
        with the ssh service or http service.

    OPTIONS:
        -h, --help
              Print out usage of this program.

        -m    Choose the work mode. 
              0:self-calibration mode.
              1:normal calibration mode.
              2:verification mode.
        
        -s    Choose the service offered by PCN.
              ssh : remote connect server through terminal.
              http: http server which can be accessed through browser.

        --ch1=local --ch2=remote
              Designate the source of each TDC input. "local" means the PPS
              signal comes from the PCN itself, "remote" means the PPS signal 
              is from other WR nodes.

        --version
              Prints out this program version information.

        --test
              PCN works in test mode whose function is not fixed.
    """        

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvm:s:",["help","test","version","ch1=","ch2="])
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
            if opt in ("-v","--version"):
                version()
                sys.exit()
            if opt in ("-m"):
                mode = int(value)
            if opt in ("-s"):
                service = value
            if opt in ("--ch1"):
                ch1 = value
            if opt in ("--ch2"):
                ch2 = value
    if (not ('mode' in dir())):
        mode = 1
    if (not ('service' in dir())):
        service = "ssh"
    if (not ('ch1' in dir())):
        ch1 = 'local'
    if (not ('ch2' in dir())):
        ch2 = 'remote'

if __name__ == "__main__":
    main()
