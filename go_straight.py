# Color Tracking Unit (ColTUn) supplementary code 
# Written for MXET 300-502 Final Project
# Spring 2021
# Functions used to determine if the tracked ball is too close or too far (based on radius conversion)
# tells SCUTTLE what distance to move forward/backward so that the ball is 0.4m / 40cm away
# called in main script coltun.py

import L1_motors as mtr
import L2_log as log
import time

# SCUTTLE moves forward
def drivef():             
    mtr.MotorR(0.6)        
    mtr.MotorL(0.6)
    print("forward")
    return
    
# SCUTTLE moves backward
def driveb():            
    mtr.MotorR(-0.6)      
    mtr.MotorL(-0.6)
    print("backward")
    return
 
# Analyzes if distance away is closer or farther than target distance and moves to cover the distance
def getdiff(difference):    
    if difference>45:   # Ball too far away
        difference-=40  # calculate difference
        drivef()        # drive forward until 40 cm away
        log.stringTmpFile("Forward", "FB.txt")
        
    elif difference<35:     # Ball too close
        difference-=40      # calculate difference
        driveb()            # drive backward until 40 cm away
        log.stringTmpFile("Backward", "FB.txt")
        
    else:
        return
    
#Stop moving if ball is centered and correct distance away
def stop():    
    mtr.MotorR(0)       
    mtr.MotorL(0)
    return
