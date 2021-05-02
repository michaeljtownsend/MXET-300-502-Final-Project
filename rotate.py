# Color Tracking Unit (ColTUn) supplementary code 
# Written for MXET 300-502 Final Project
# Spring 2021
# Functions used to determine if the tracked ball is centered or not
# tells SCUTTLE which direction to rotate to become centered
# called in main script coltun.py

import L1_motors as mtr
import L2_log as log
import time

# SCUTTLE rotates to the left
def left():             
    i = 0
    mtr.MotorR(0.6)
    mtr.MotorL(-0.6)
    while i <= 25000:
        i+=1
    
    print("left")
    mtr.MotorR(0)
    mtr.MotorL(0)
    return
    
# SCUTTLE rotates to the right
def right():             
    i = 0
    mtr.MotorR(-0.6)
    mtr.MotorL(0.6)
    while i <= 25000:
        i+=1
    
    print("right")
    mtr.MotorR(0)
    mtr.MotorL(0)
    return
    
# Checks if the x-value of object is centered in frame
def center(tolerance):      
    if tolerance>65:    # If ball is to the right of the SCUTTLE, rotate right
        right()
        log.stringTmpFile("Right", "RL.txt")
    if tolerance<55:    # If ball is to the left of the SCUTTLE, rotate left
        left()
        log.stringTmpFile("Left", "RL.txt")
    return

# First part of lost routine, move backwards in case ball is only slightly out of frame
def lost():                 # back up 
    mtr.MotorR(-1)
    mtr.MotorL(-1)
    print("lost")
    return 

# Second part of lost routine, rotate to the left to find the ball that is not in frame
def lost_stage2():                 # rotate 
    mtr.MotorR(0.75)
    mtr.MotorL(-0.75)
    print("lost")
    return 
