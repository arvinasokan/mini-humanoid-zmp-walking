#!/usr/bin/env python
import os
import dynamixel
import time
import random
import sys
import subprocess
import optparse
import yaml
import numpy as np

#Importing Ach
import hubo_ach as ha
import ach
from ctypes import *

#rad to dynamixel
def rad2dyn(rad):
    return np.int(np.floor( ((rad + np.pi)/(2.0 * np.pi) * 1024)*0.83333 ))


#dynamixel to rad
def dyn2rad(en):
    return en / 4096.0 * 2.0 * np.pi - np.pi
def mapping(x):
    return np.int(np.floor((x + 3.14159265359) * (1024 - 0) / (3.14159265359 + 3.14159265359) + 0))


def main(settings):
    # Open HUBO-Ach feed-forward and feed-back (reference and state) channels
    s = ach.Channel(ha.HUBO_CHAN_STATE_NAME)
    e = ach.Channel(ha.HUBO_CHAN_ENC_NAME)
    r = ach.Channel(ha.HUBO_CHAN_REF_NAME)
    s.flush()
    r.flush()

    # feed-forward will now be refered to as "state"
    state = ha.HUBO_STATE()

    # encoder channel will be refered to as "encoder"
    encoder = ha.HUBO_ENC()

    # feed-back will now be refered to as "ref"
    ref = ha.HUBO_REF()

    # Get the current feed-forward (state) 
    [statuss, framesizes] = s.get(state, wait=False, last=True)
    [statuss, framesizes] = e.get(encoder, wait=False, last=True)
    [statuss, framesizes] = r.get(state, wait=False, last=True)

    portName = settings['port']
    baudRate = settings['baudRate']
    highestServoId = settings['highestServoId']

    # Establish a serial connection to the dynamixel network.
    # This usually requires a USB2Dynamixel
    serial = dynamixel.SerialStream(port=portName, baudrate=baudRate, timeout=1)
    net = dynamixel.DynamixelNetwork(serial)
    
    # Ping the range of servos that are attached
    print "Scanning for Dynamixels..."
    net.scan(1, highestServoId)
    
    myActuators = []
    
    for dyn in net.get_dynamixels():
        print dyn.id
        myActuators.append(net[dyn.id])
    
    if not myActuators:
      print 'No Dynamixels Found!'
      sys.exit(0)
    else:
      print "...Done"
    
    for actuator in myActuators:
        actuator.moving_speed = 50
        actuator.synchronized = True
        actuator.torque_enable = True
        actuator.torque_limit = 800
        actuator.max_torque = 800
    
    # Randomly vary servo position within a small range
    print "Actuators Ready"
    while True:
        r.get(ref)
        for actuator in myActuators:
            if ( actuator.id == 1):
                actuator.goal_position = mapping(-ref.ref[ha.RAR])-10
                r.get(ref)
                print 'ref',(actuator.goal_position)
            if ( actuator.id == 2):
                actuator.goal_position = mapping(ref.ref[ha.RAP])
                r.get(ref)
            if ( actuator.id == 3):
                actuator.goal_position = mapping(ref.ref[ha.RKN])
                r.get(ref)
            if ( actuator.id == 4):
                actuator.goal_position = mapping(-ref.ref[ha.RHP])
                r.get(ref)
            if ( actuator.id == 5):
                actuator.goal_position = mapping(ref.ref[ha.RHR])-10
                r.get(ref)
            if ( actuator.id == 6):
                actuator.goal_position = mapping(-ref.ref[ha.RHY])-160
                r.get(ref) 
            if ( actuator.id == 7):
                actuator.goal_position = mapping(-ref.ref[ha.LHY])+160
                r.get(ref)
            if ( actuator.id == 8):
                actuator.goal_position = mapping(ref.ref[ha.LHR])+10
                r.get(ref)  
            if ( actuator.id == 9):
                actuator.goal_position = mapping(ref.ref[ha.LHP])
                r.get(ref)
            if ( actuator.id == 10):
                actuator.goal_position = mapping(-ref.ref[ha.LKN])
                r.get(ref)
            if ( actuator.id == 11):
                actuator.goal_position = mapping(-ref.ref[ha.LAP])
                r.get(ref)
            if ( actuator.id == 12):
                actuator.goal_position = mapping(-ref.ref[ha.LAR])+10
                r.get(ref)
    
        net.synchronize()
   
        for actuator in myActuators:
            actuator.read_all()
            time.sleep(0.01)
        for actuator in myActuators:
            #print actuator._id, "\t", actuator.current_position
            time.sleep(0.05)

def validateInput(userInput, rangeMin, rangeMax):
    '''
    Returns valid user input or None
    '''
    try:
        inTest = int(userInput)
        if inTest < rangeMin or inTest > rangeMax:
            print "ERROR: Value out of range [" + str(rangeMin) + '-' + str(rangeMax) + "]"
            return None
    except ValueError:
        print("ERROR: Please enter an integer")
        return None
    
    return inTest

if __name__ == '__main__':
    
    parser = optparse.OptionParser()
    parser.add_option("-c", "--clean",
                      action="store_true", dest="clean", default=False,
                      help="Ignore the settings.yaml file if it exists and \
                      prompt for new settings.")
    
    (options, args) = parser.parse_args()
    
    # Look for a settings.yaml file
    settingsFile = 'settings.yaml'
    if not options.clean and os.path.exists(settingsFile):
        with open(settingsFile, 'r') as fh:
            settings = yaml.load(fh)
    # If we were asked to bypass, or don't have settings
    else:
        settings = {}
        if os.name == "posix":
            portPrompt = "Which port corresponds to your USB2Dynamixel? \n"
            # Get a list of ports that mention USB
            try:
                possiblePorts = subprocess.check_output('ls /dev/ | grep -i usb',
                                                        shell=True).split()
                possiblePorts = ['/dev/' + port for port in possiblePorts]
            except subprocess.CalledProcessError:
                sys.exit("USB2Dynamixel not found. Please connect one.")
                
            counter = 1
            portCount = len(possiblePorts)
            for port in possiblePorts:
                portPrompt += "\t" + str(counter) + " - " + port + "\n"
                counter += 1
            portPrompt += "Enter Choice: "
            portChoice = None
            while not portChoice:                
                portTest = raw_input(portPrompt)
                portTest = validateInput(portTest, 1, portCount)
                if portTest:
                    portChoice = possiblePorts[portTest - 1]

        else:
            portPrompt = "Please enter the port name to which the USB2Dynamixel is connected: "
            portChoice = raw_input(portPrompt)
    
        settings['port'] = portChoice
        
        # Baud rate
        baudRate = None
        while not baudRate:
            brTest = raw_input("Enter baud rate [Default: 1000000 bps]:")
            if not brTest:
                baudRate = 1000000
            else:
                baudRate = validateInput(brTest, 9600, 1000000)
                    
        settings['baudRate'] = baudRate
        
        # Servo ID
        highestServoId = None
        while not highestServoId:
            hsiTest = raw_input("Please enter the highest ID of the connected servos: ")
            highestServoId = validateInput(hsiTest, 1, 255)
        
        settings['highestServoId'] = highestServoId
        
        # Save the output settings to a yaml file
        with open(settingsFile, 'w') as fh:
            yaml.dump(settings, fh)
            print("Your settings have been saved to 'settings.yaml'. \nTo " +
                   "change them in the future either edit that file or run " +
                   "this example with -c.")
    
    main(settings)
