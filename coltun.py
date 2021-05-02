# Color Tracking Unit (ColTUn) main code 
# Written for MXET 300-502 Final Project
# Spring 2021
# This file is passed as an argument to the BASH command when running setup_mjpg_streamer
# We added features to log values such as the radius, calculated distance to ball, and moving direction and speed.
# Also added feature to select between the three colors with HSV values already predetermined.

# Import external libraries
import cv2
import numpy as np
import L2_log as log
import rotate as no_brakes
import go_straight as all_gas
import L1_encoder as enc
import L2_kinematics as kine
import L1_adc as adc
#import L1_camera as cam    # would give errors as it interupted the live stream

#pictimer = 0  # initializes timer for pictures
width  = 120  # width of image to process (pixels)
height = 80 # height of image to process (pixels)
filter = 'HSV'  # Use HSV to describe pixel color values
color_range = np.array([[0, 0, 0], [255, 255, 255]]) # declare HSV range before overwrighting with user inputs

class MyFilter:

    def colorTracking(self, image, range=color_range, min_size=6, max_size=6):

        image = cv2.resize(image,(width,height)) # resize the image
        
        # Read ADC voltage
        voltage = adc.getDcJack()
        log.tmpFile(voltage,"adcread.txt")

        # Grab the HSV inputs from the NodeRed selections by accesing the files 
        if filter == 'RGB':
            frame_to_thresh = image.copy()
        
        else:
            frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # convert image to hsv colorspace RENAME THIS TO IMAGE_HSV

        # Logs predetermined HSV values to allow for the slider in NodeRed to work
        # use the NodeRed slider to determine which color to track
        with open('/tmp/slider_choice') as slider_choice_file:  
            slider_choice_file.seek(0)
            try:
                slider_choice = int(slider_choice_file.read())
            except:
                slider_choice= 0

        # predetermined HSV values to use
        if slider_choice == 1:  # Pink
            h_min = 0
            h_max = 105
            s_min = 120
            s_max = 190
            v_min = 145
            v_max = 220
            
        if slider_choice == 2:  # Blue
            h_min = 90
            h_max = 150
            s_min = 50
            s_max = 165
            v_min = 30
            v_max = 175
            
        if slider_choice == 3:  # Green
            h_min = 35
            h_max = 95
            s_min = 35
            s_max = 165
            v_min = 40
            v_max = 165


        # PROCESS THE IMAGE     
        color_range = (((h_min), (s_min), (v_min)),((h_max), (s_max), (v_max)))
        thresh = cv2.inRange(frame_to_thresh, color_range[0], color_range[1]) # Converts a 240x160x3 matrix to a 240x160x1 matrix
        # cv2.inrange discovers the pixels that fall within the specified range and assigns 1's to these pixels and 0's to the others.

        # Apply a blur function
        kernel = np.ones((5,5),np.uint8)
        mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel) # Apply blur
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel) # Blur again
        mask = thresh

        # Number of pixels within the HSV range that are next to eachother
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2] #generates number of contiguous "1" pixels
        center = None # create a variable for x, y location of target

        # If there is at least 1 pixels of the object, track it
        if len(cnts) > 0:   # begin processing if there are "1" pixels discovered
        
            # Define the circle around object based on cluster of pixels
            c = max(cnts, key=cv2.contourArea)  # return the largest target area
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            # M = cv2.moments(c)
            # center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))  # defines a circle around the largest target area
            center = (int(x), int(y))  # defines a circle around the largest target area

            # draw the center point and circle if object detected is big enough
            if radius > min_size:
                cv2.circle(image, (int(x), int(y)), int(radius),(0, 255, 255), 2) #draw a circle on the image
                cv2.circle(image, (int(x), int(y)), 3, (0, 0, 0), -1) # draw a dot on the target center
                cv2.circle(image, (int(x), int(y)), 1, (255, 255, 255), -1) # draw a dot on the target center

                cv2.putText(image,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.2,(0,0,0),2,cv2.LINE_AA)
                cv2.putText(image,"("+str(center[0])+","+str(center[1])+")", (center[0]+10,center[1]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.2,(255,255,255),1,cv2.LINE_AA)
                
                # calculate the distance the ball is from camera in cm by converting the radius value
                distance_away = (993)*(radius**(-0.991))   # using power equation
                #distance_away = (0.242*(radius**2))-(13*radius)+209   # using polynomial equation
                
                # Print the values in the terminal and log to file used in NodeRed
                print ("Distance away(cm):",distance_away,"Radius(pixels):",radius,'Color Selection(1,2,or3):', slider_choice)   # prints the calculated distance, radius, and color selection in the terminal
                log.tmpFile(distance_away, "distance_away.txt")     # logs distance values to tmp file to be displayed in NodeRed
                log.tmpFile(radius, "radius.txt")    # logs radius values to tmp file to be displayed in NodeRed
           
            # Actuation to track the selected ball       
            if center[0]>45 and center[0]<75:       # if the ball IS in center frame, SCUTTLE moves to be 40 cm away
               
                #pictimer+=1  # counts the picture timer
                #if pictimer%70:
                #   cam.newImage(width,height)
                
                # stop moving if the ball is centered, 40 cm away, and not moving
                if distance_away < 45 and distance_away>35:
                    all_gas.stop()
                    xandtdot = kine.getMotion()
                    print ("Chassis Speed (x dot) ",xandtdot[0], "(t dot) ",xandtdot[1])   # prints the speed of chassis
                    log.tmpFile(xandtdot[0], "xdot.txt")    # logs x dot values
                    log.tmpFile(xandtdot[1], "tdot.txt")    # logs theta dot values
                    detection = "Target Located and in range"   # message if ColTUn has properly tracked the ball to where it has stopped 
                    log.stringTmpFile(detection, "detection.txt")
                
                # if the ball is centered and NOT 40cm away, move so that it is
                else:
                    all_gas.getdiff(distance_away)
                    xandtdot = kine.getMotion()
                    print ("Chassis Speed (x dot) ",xandtdot[0], "(t dot) ",xandtdot[1])   # prints the speed of chassis
                    log.tmpFile(xandtdot[0], "xdot.txt")    # logs x dot values
                    log.tmpFile(xandtdot[1], "tdot.txt")    # logs theta dot values
                    detection = "BALL DETECTED"     # message if the ball is in frame and being tracked
                    log.stringTmpFile(detection, "detection.txt")                
            
            # if ball NOT in center frame, rotates until lined up straight with the selected ball (45<x<75)  
            else:
                no_brakes.center(center[0])     
                xandtdot = kine.getMotion()
                print ("Chassis Speed (x dot) ",xandtdot[0], "(t dot) ",xandtdot[1])   # prints the speed of chassis
                log.tmpFile(xandtdot[0], "xdot.txt")
                log.tmpFile(xandtdot[1], "tdot.txt") 
                detection = "BALL DETECTED"     # message if the ball is in frame and being tracked
                log.stringTmpFile(detection, "detection.txt")
                

        # if there's less than 1 pixels of the object, go into lost routine               
        else:
            no_brakes.lost()    # enter lost protocol and search for ball not in frame
            detection = "NOT DETECTED"  # message if the ball is NOT in frame
            log.stringTmpFile(detection, "detection.txt")
            if len(cnts) < 7:
                no_brakes.lost_stage2()
            else:
                return
        
# -----------------------------------------------------------------------------------------------------
# GENERATE 3 IMAGES SHOWING STAGES OF FILTER & STACK THEM VERTICALLY TO OUTPUT FOR THE USER
        image_height, image_width, channels = image.shape   # get image dimensions

        spacer = np.zeros((image_height,3,3), np.uint8)
        spacer[:,0:width//2] = (255,255,255)      # (B, G, R)

        # make 3 images to have the same colorspace, for combining
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        # border1 = np.array() # use H, height of photos to define
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        # border2 = np.array() # same as above

        # draw text on top of the image for identification
        cv2.putText(image,'Original',(10,int(image_height/10)), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(0,0,0),2,cv2.LINE_AA)
        cv2.putText(image,'Original',(10,int(image_height/10)), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(255,255,255),1,cv2.LINE_AA)

        # draw text on top of the image for identification
        cv2.putText(thresh,'Thresh',(10,int(image_height/10)), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(0,0,0),2,cv2.LINE_AA)
        cv2.putText(thresh,'Thresh',(10,int(image_height/10)), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(255,255,255),1,cv2.LINE_AA)

        # draw text on top of the image for identification
        cv2.putText(mask,'Mask',(10,int(image_height/10)), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(0,0,0),2,cv2.LINE_AA)
        cv2.putText(mask,'Mask',(10,int(image_height/10)), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(255,255,255),1,cv2.LINE_AA)

        all = np.vstack((image, thresh, mask))
        return all
        
        
def init_filter():  # The function MJPG-Streamer calls.
    f = MyFilter()
    return f.colorTracking
