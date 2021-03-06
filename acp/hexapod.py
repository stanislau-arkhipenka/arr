#***********************************************************************
# Hexapod Program
# originally developed by Mark W
# translated to python by Stanislau Arkhipenka
#***********************************************************************

#***********************************************************************
# IK and Hexapod gait references:
#  https:#www.projectsofdan.com/?cat=4
#  http:#www.gperco.com/2015/06/hex-inverse-kinematics.html
#  http:#virtual-shed.blogspot.com/2012/12/hexapod-inverse-kinematics-part-1.html
#  http:#virtual-shed.blogspot.com/2013/01/hexapod-inverse-kinematics-part-2.html
#  https:#www.robotshop.com/community/forum/t/inverse-kinematic-equations-for-lynxmotion-3dof-legs/21336
#  http:#arduin0.blogspot.com/2012/01/inverse-kinematics-ik-implementation.html?utm_source=rb-community&utm_medium=forum&utm_campaign=inverse-kinematic-equations-for-lynxmotion-3dof-legs
#***********************************************************************
import os
import time
import logging
import math
import json
from typing import List, Dict
from common import map, constrain
from dummy import DummyController, DummyServo

logger = logging.getLogger(__name__)


class Hexapod:
  #***********************************************************************
  # Constant Declarations
  #***********************************************************************
  RAD_TO_DEG = 57.29577951
  M_PI = 3.141592

  BATT_VOLTAGE = 0           #12V Battery analog voltage input port

  RUMBLE = True
  PRESSURES = False

  COXA_LENGTH = 51           #leg part lengths
  FEMUR_LENGTH = 65
  TIBIA_LENGTH = 121

  TRAVEL = 30                #translate and rotate travel limit constant

  A12DEG = 209440           #12 degrees in radians x 1,000,000
  A30DEG = 523599           #30 degrees in radians x 1,000,000

  SERVO_TIME_MS = 100
  FRAME_TIME_MS = 10         #frame time (20msec = 50Hz)

  HOME_X = [  82.0,   0.0, -82.0,  -82.0,    0.0,  82.0]  #coxa-to-toe home positions
  HOME_Y = [  82.0, 116.0,  82.0,  -82.0, -116.0, -82.0]
  HOME_Z = [ -80.0, -80.0, -80.0,  -80.0,  -80.0, -80.0]

  BODY_X = [ 110.4,  0.0, -110.4, -110.4,    0.0, 110.4]  #body center-to-coxa servo distances 
  BODY_Y = [  58.4, 90.8,   58.4,  -58.4,  -90.8, -58.4]
  BODY_Z = [   0.0,  0.0,    0.0,    0.0,    0.0,   0.0]

  COXA_CAL  = [0, 0, 0, 0, 0, 0]                       #servo calibration constants
  FEMUR_CAL = [0, 0, 0, 0, 0, 0]
  TIBIA_CAL = [0, 0, 0, 0, 0, 0]

  BUT_A = 'a'
  BUT_B = 'b'
  BUT_X = 'x'
  BUT_Y = 'y'
  BUT_SELECT = 'select'
  BUT_START = 'start'
  BUT_THUMBL = 'thumbl'
  BUT_THUMBR = 'thumbr'
  BUT_TL = 'tl'
  BUT_TR = 'tr'
  BUT_L2 = 'l2'
  BUT_R2 = 'r2'

  PAD_UP = 'pad_up'
  PAD_DOWN = 'pad_down'
  PAD_LEFT = 'pad_left'
  PAD_RIGHT = 'pad_right'

  AS_LX = 'lx'
  AS_LY = 'ly'
  
  AS_RX = 'rx'
  AS_RY = 'ry'

  THROTTLE_L = "throttle_l"
  THROTTLE_R = "throttle_r"

  GAIT_TRIP = 0
  GAIT_WAVE = 1
  GAIT_RIPP = 2
  GAIT_TETR = 3
  GAIT_DEFAULT = GAIT_TRIP

  gait_id_to_name: Dict[int,str] = {
    GAIT_TRIP: "Tripod", 
    GAIT_WAVE: "Wave", 
    GAIT_RIPP: "Ripple", 
    GAIT_TETR: "Tetrapod"
    }

  MODE_IDLE = 0
  MODE_WALK = 1
  MODE_CXYZ = 2
  MODE_CYPR = 3
  MODE_OLEG = 4
  MODE_CALI = 99

  mode_id_to_name: Dict[int,str] = {
    MODE_IDLE: "Idle", 
    MODE_WALK: "Walk", 
    MODE_CXYZ: "Control x-y-z", 
    MODE_CYPR: "Control y-p-r", 
    MODE_OLEG: "One leg", 
    MODE_CALI: "Calibration"
    }

 
  #***********************************************************************
  # Initialization Routine
  #***********************************************************************
  def __init__(self, config_file_path: str):
    
    self.cal_values = {
      "coxa": self.COXA_CAL,
      "femur": self.FEMUR_CAL,
      "tibia": self.TIBIA_CAL
    }

    self.config_file_path = config_file_path
    self.reload_config()

    # Variable Declarations
    self.batt_voltage_array = []
    self.batt_voltage = 0
    self.currentTime = self.get_current_time_ms()
    self.previousTime = self.get_current_time_ms()

    self.offset_X: List[float] = [0] * 6
    self.offset_Y: List[float] = [0] * 6
    self.offset_Z: List[float] = [0] * 6
    self.current_X: List[float] = [0] * 6
    self.current_Y: List[float] = [0] * 6
    self.current_Z: List[float] = [0] * 6

    self.tripod_case   = [1,2,1,2,1,2]     #for tripod gait walking
    self.ripple_case   = [2,6,4,1,3,5]     #for ripple gait
    self.wave_case     = [1,2,3,4,5,6]     #for wave gait
    self.tetrapod_case = [1,3,2,1,2,3]     #for tetrapod gait

    # Object Declarations
    self.controller = DummyController()    # gamepad controller

    self.coxa1_servo  = DummyServo()        #18 servos = Servo()
    self.femur1_servo = DummyServo()
    self.tibia1_servo = DummyServo()
    self.coxa2_servo  = DummyServo()
    self.femur2_servo = DummyServo()
    self.tibia2_servo = DummyServo()
    self.coxa3_servo  = DummyServo()
    self.femur3_servo = DummyServo()
    self.tibia3_servo = DummyServo()
    self.coxa4_servo  = DummyServo()
    self.femur4_servo = DummyServo()
    self.tibia4_servo = DummyServo()
    self.coxa5_servo  = DummyServo()
    self.femur5_servo = DummyServo()
    self.tibia5_servo = DummyServo()
    self.coxa6_servo  = DummyServo()
    self.femur6_servo = DummyServo()
    self.tibia6_servo = DummyServo()

    self.capture_offsets = False
    self.step_height_multiplier = 1

    self.mode: int = self.MODE_IDLE
    self.gait: int = self.GAIT_DEFAULT
    self.gait_speed: int = 0
    self.reset_position: bool = True
    self.leg1_IK_control: bool = True
    self.leg6_IK_control: bool = True

    self.gamepad_vibrate: int = 0
    self.tick: int = 0

    self.z_height_left = 0
    self.z_height_right = 0

    self.n_cycles = 0

    self.cal_pntr: int = 0
    self.cal_inner_pntr: int = 0

  #***********************************************************************
  # Main Program
  #***********************************************************************
  def run(self):
    while True:
      self.loop()
      time.sleep(self.FRAME_TIME_MS/1000)

  def loop(self):

    #set up frame time
    self.currentTime = self.get_current_time_ms()
    if self.currentTime - self.previousTime > self.FRAME_TIME_MS:
      self.previousTime = self.currentTime

      #read controller and process inputs
      self.controller.read_gamepad(self.gamepad_vibrate) # TODO vibrate not implemented     
      self.process_gamepad()

      #reset legs to home position when commanded
      if self.reset_position == True:
        for leg_num in range(0,6):
          self.current_X[leg_num] = self.HOME_X[leg_num]
          self.current_Y[leg_num] = self.HOME_Y[leg_num]
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
        self.reset_position = False 
      
      #position legs using IK calculations - unless set all to 90 degrees mode
      if self.mode != self.MODE_CALI:
        for leg_num in range(0,6):
          self.leg_IK(leg_num,self.current_X[leg_num]+self.offset_X[leg_num],self.current_Y[leg_num]+self.offset_Y[leg_num],self.current_Z[leg_num]+self.offset_Z[leg_num])       

      #reset leg lift first pass flags if needed
      if self.mode != self.MODE_OLEG:
        self.leg1_IK_control = True 
        self.leg6_IK_control = True

      self.print_debug()                            #print debug data

      #process modes (mode 0 is default 'home idle' do-nothing mode)
      if self.mode == self.MODE_WALK:               #walking mode
        if self.gait == self.GAIT_TRIP:
          self.tripod_gait()
        elif self.gait == self.GAIT_WAVE:
          self.wave_gait()
        elif self.gait == self.GAIT_RIPP:
          self.ripple_gait()
        elif self.gait == self.GAIT_TETR:
          self.tetrapod_gait()
      elif self.mode == self.MODE_CXYZ:
        self.translate_control()
      elif self.mode == self.MODE_CYPR:
        self.rotate_control()
      elif self.mode == self.MODE_OLEG:
        self.one_leg_lift()
      elif self.mode == self.MODE_CALI:
        self.set_all_90()
      
      self.n_cycles += 1


  #***********************************************************************
  # Process gamepad controller inputs
  #***********************************************************************
  def process_gamepad(self):
    if self.controller.button_pressed(self.PAD_DOWN) and self.mode != self.MODE_CALI:    #stop & select gait 0
      self.set_mode(self.MODE_IDLE)
      self.set_gait(self.GAIT_TRIP)
      self.reset_position = True
    if self.controller.button_pressed(self.PAD_LEFT) and self.mode != self.MODE_CALI:    #stop & select gait 1 
      self.set_mode(self.MODE_IDLE)
      self.set_gait(self.GAIT_WAVE)
      self.reset_position = True
    if self.controller.button_pressed(self.PAD_UP) and self.mode != self.MODE_CALI:      #stop & select gait 2  
      self.set_mode(self.MODE_IDLE)
      self.set_gait(self.GAIT_RIPP)
      self.reset_position = True
    if self.controller.button_pressed(self.PAD_RIGHT) and self.mode != self.MODE_CALI:   #stop & select gait 3
      self.set_mode(self.MODE_IDLE)
      self.set_gait(self.GAIT_TETR)
      self.reset_position = True
    if self.controller.button_pressed(self.BUT_Y):    #select walk mode
      self.set_mode(self.MODE_WALK)
      self.reset_position = True
    if self.controller.button(self.BUT_Y):           #vibrate controller if walk button held
      self.gamepad_vibrate = 64 
    else:
      self.gamepad_vibrate = 0
    if self.controller.button_pressed(self.BUT_X):      #control x-y-z with joysticks mode
      self.set_mode(self.MODE_CXYZ)
      self.reset_position = True
    if self.controller.button_pressed(self.BUT_B):      #control y-p-r with joysticks mode
      self.set_mode(self.MODE_CYPR)
      self.reset_position = True
    if self.controller.button_pressed(self.BUT_A):       #one leg lift mode
      self.set_mode(self.MODE_OLEG)
      self.reset_position = True
    if self.controller.button_pressed(self.BUT_START):       #change self.gait speed
      if self.gait_speed == 0:
        self.gait_speed = 1
      else:
        self.gait_speed = 0
    if self.controller.button_pressed(self.BUT_SELECT):      #set all servos to 90 degrees for calibration
      if self.mode != self.MODE_CALI:
        self.set_mode(self.MODE_CALI)
      else:
        self.set_mode(self.MODE_IDLE)
        self.set_gait(self.GAIT_DEFAULT)
    if self.mode == self.MODE_CALI:
      self.process_gamepad_calibration()
    if self.controller.button_pressed(self.BUT_TL) or self.controller.button_pressed(self.BUT_TR):
      #capture offsets in translate, rotate, and translate/rotate modes
      self.capture_offsets = True
    if self.controller.button_pressed(self.BUT_L2) or self.controller.button_pressed(self.BUT_R2):   # TODO ANALOG to BIN
      for leg_num in range(0,6):  #clear offsets
        self.offset_X[leg_num] = 0
        self.offset_Y[leg_num] = 0
        self.offset_Z[leg_num] = 0
      self.leg1_IK_control = True               #reset leg lift first pass flags
      self.leg6_IK_control = True
      self.step_height_multiplier = 1.0         #reset step height multiplier


  def process_gamepad_calibration(self):
    pressed = False
    if self.controller.button_pressed(self.BUT_SELECT):
      logger.info("coxa: %s", self.COXA_CAL)
      logger.info("femur: %s", self.FEMUR_CAL)
      logger.info("tibia: %s", self.TIBIA_CAL)
      data, name, i = self.get_cal_pntr()
      pressed = True
    if self.controller.button_pressed(self.PAD_UP):
      data, name, i = self.get_cal_pntr()
      data[i] = data[i] + 1
      pressed = True
      self.write_config()
    elif self.controller.button_pressed(self.PAD_DOWN):
      data, name, i = self.get_cal_pntr()
      data[i] = data[i] - 1
      pressed = True
      self.write_config()
    elif self.controller.button_pressed(self.PAD_LEFT):
      data, name, i = self.get_cal_pntr(move = -1)
      pressed = True
    elif self.controller.button_pressed(self.PAD_RIGHT):
      data, name, i = self.get_cal_pntr(move = 1)
      pressed = True
    if pressed:
      logger.info(f"{name}[{i}] = {data[i]}")


  # I'm not proud about this functions
  # It's just nesessary hacks for manipulating data
  # which is structured in not very convinient way
  # Ideally I need to refactor data structures (to use dicts)
  # and all this junky code will go away
  def get_cal_structure(self, move: int = 0):
    self.cal_pntr += move
    if self.cal_pntr > 2:
      self.cal_pntr = 0
    elif self.cal_pntr < 0:
      self.cal_pntr = 2
    if self.cal_pntr == 0:
      return self.COXA_CAL, "coxa"
    elif self.cal_pntr == 1:
      return self.FEMUR_CAL, "femur"
    elif self.cal_pntr == 2:
      return self.TIBIA_CAL, "tibia"

  def get_cal_pntr(self, move: int = 0):
    self.cal_inner_pntr += move
    if self.cal_inner_pntr >= len(self.get_cal_structure()[0]):
      data, name = self.get_cal_structure(move = 1)
      self.cal_inner_pntr = 0
    elif self.cal_inner_pntr < 0:
      data, name = self.get_cal_structure(move = -1)
      self.cal_inner_pntr = len(data) - 1
    else:
      data, name = self.get_cal_structure(move = 0)
    return data, name, self.cal_inner_pntr


  #***********************************************************************
  # Leg IK Routine
  #***********************************************************************
  def leg_IK(self, leg_num: int, X: float, Y: float, Z: float):
    #compute target femur-to-toe (L3) length
    L0 = math.sqrt(pow(X,2) + pow(Y,2)) - self.COXA_LENGTH
    L3 = math.sqrt(pow(L0,2) + pow(Z,2))
    

    #process only if reach is within possible range (not too long or too short!)
    if L3 < self.TIBIA_LENGTH+self.FEMUR_LENGTH and L3 > self.TIBIA_LENGTH-self.FEMUR_LENGTH:  
      #compute tibia angle
      phi_tibia = math.acos((pow(self.FEMUR_LENGTH,2) + pow(self.TIBIA_LENGTH, 2) - pow(L3,2))/(2*self.FEMUR_LENGTH*self.TIBIA_LENGTH))  # TODO check pow(self.TIBIA_LENGTH, 2????)
      theta_tibia = phi_tibia*self.RAD_TO_DEG - 23.0 + self.TIBIA_CAL[leg_num]
      theta_tibia = constrain(theta_tibia,0.0,180.0)
    
      #compute femur angle
      gamma_femur = math.atan2(Z,L0)
      phi_femur = math.acos((pow(self.FEMUR_LENGTH,2) + pow(L3,2) - pow(self.TIBIA_LENGTH,2))/(2*self.FEMUR_LENGTH*L3))
      theta_femur = (phi_femur + gamma_femur)*self.RAD_TO_DEG + 14.0 + 90.0 + self.FEMUR_CAL[leg_num]
      theta_femur = constrain(theta_femur,0.0,180.0)  

      #compute coxa angle
      theta_coxa = math.atan2(X,Y)*self.RAD_TO_DEG + self.COXA_CAL[leg_num]

      #output to the appropriate leg
      if leg_num == 0:
        if self.leg1_IK_control == True:                       #flag for IK or manual control of leg
          theta_coxa = theta_coxa + 45.0                 #compensate for leg mounting
          theta_coxa = constrain(theta_coxa,0.0,180.0)
          self.coxa1_servo.write(int(theta_coxa)) 
          self.femur1_servo.write(int(theta_femur)) 
          self.tibia1_servo.write(int(theta_tibia)) 
        
      elif leg_num == 1:
        theta_coxa = theta_coxa + 90.0                 #compensate for leg mounting
        theta_coxa = constrain(theta_coxa,0.0,180.0)
        self.coxa2_servo.write(int(theta_coxa)) 
        self.femur2_servo.write(int(theta_femur)) 
        self.tibia2_servo.write(int(theta_tibia)) 
        
      elif leg_num == 2:
        theta_coxa = theta_coxa + 135.0                 #compensate for leg mounting
        theta_coxa = constrain(theta_coxa,0.0,180.0)
        self.coxa3_servo.write(int(theta_coxa)) 
        self.femur3_servo.write(int(theta_femur)) 
        self.tibia3_servo.write(int(theta_tibia)) 
        
      elif leg_num == 3:
        if theta_coxa < 0:                                #compensate for leg mounting
          theta_coxa = theta_coxa + 225.0                # (need to use different
        else:                                              #  positive and negative offsets 
          theta_coxa = theta_coxa - 135.0                #  due to atan2 results above!)
        theta_coxa = constrain(theta_coxa,0.0,180.0)
        self.coxa4_servo.write(int(theta_coxa)) 
        self.femur4_servo.write(int(theta_femur)) 
        self.tibia4_servo.write(int(theta_tibia)) 
        
      if leg_num == 4:
        if theta_coxa < 0:                                #compensate for leg mounting
          theta_coxa = theta_coxa + 270.0                # (need to use different
        else:                                              #  positive and negative offsets 
          theta_coxa = theta_coxa - 90.0                 #  due to atan2 results above!)
        theta_coxa = constrain(theta_coxa,0.0,180.0)
        self.coxa5_servo.write(int(theta_coxa)) 
        self.femur5_servo.write(int(theta_femur)) 
        self.tibia5_servo.write(int(theta_tibia)) 
        
      if leg_num == 5:
        if self.leg6_IK_control == True:                       #flag for IK or manual control of leg
          if theta_coxa < 0:                              #compensate for leg mounting
            theta_coxa = theta_coxa + 315.0              # (need to use different
          else:                                            #  positive and negative offsets 
            theta_coxa = theta_coxa - 45.0               #  due to atan2 results above!)
          theta_coxa = constrain(theta_coxa,0.0,180.0)
          self.coxa6_servo.write(int(theta_coxa)) 
          self.femur6_servo.write(int(theta_femur)) 
          self.tibia6_servo.write(int(theta_tibia)) 


  #***********************************************************************
  # Tripod Gait
  # Group of 3 legs move forward while the other 3 legs provide support
  #***********************************************************************
  def tripod_gait(self):
    #read commanded values from controller
    val_x = self.controller.analog(self.THROTTLE_R) - self.controller.analog(self.THROTTLE_L)
    commandedY = map(val_x, -255, 255, 127, -127)
    
    commandedX = map(self.controller.analog(self.AS_RY),0,255,127,-127) 
    commandedR = map(self.controller.analog(self.AS_RX),0,255,127,-127)
      
    #if commands more than deadband then process
    if abs(commandedX) > 15 or abs(commandedY) > 15 or abs(commandedR) > 15 or self.tick>0:
      self.compute_strides(commandedX, commandedY, commandedR)
      numTicks = round(self.duration / self.SERVO_TIME_MS / 2.0) #total ticks divided into the two cases
      for leg_num in range(0,6):
        self.compute_amplitudes(leg_num)
        if self.tripod_case[leg_num] == 1:                               #move foot forward (raise and lower)
          self.current_X[leg_num] = self.HOME_X[leg_num] - self.amplitudeX*math.cos(self.M_PI*self.tick/numTicks)
          self.current_Y[leg_num] = self.HOME_Y[leg_num] - self.amplitudeY*math.cos(self.M_PI*self.tick/numTicks)
          self.current_Z[leg_num] = self.HOME_Z[leg_num] + abs(self.amplitudeZ)*math.sin(self.M_PI*self.tick/numTicks)
          if self.tick >= numTicks-1:
            self.tripod_case[leg_num] = 2
        elif self.tripod_case[leg_num] == 2:                               #move foot back (on the ground)
          self.current_X[leg_num] = self.HOME_X[leg_num] + self.amplitudeX*math.cos(self.M_PI*self.tick/numTicks)
          self.current_Y[leg_num] = self.HOME_Y[leg_num] + self.amplitudeY*math.cos(self.M_PI*self.tick/numTicks)
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.tripod_case[leg_num] = 1
      #increment tick
      if self.tick < numTicks-1:
        self.tick+=1
      else: 
        self.tick = 0


  #***********************************************************************
  # Wave Gait
  # Legs move forward one at a time while the other 5 legs provide support
  #***********************************************************************
  def wave_gait(self):
    #read commanded values from controller
    val_x = self.controller.analog(self.THROTTLE_R) - self.controller.analog(self.THROTTLE_L)
    commandedY = map(val_x, -255, 255, 127, -127)
    
    commandedX = map(self.controller.analog(self.AS_RY),0,255,127,-127) 
    commandedR = map(self.controller.analog(self.AS_RX),0,255,127,-127)

    #if commands more than deadband then process
    if abs(commandedX) > 15 or abs(commandedY) > 15 or abs(commandedR) > 15 or self.tick>0:
      self.compute_strides(commandedX, commandedY, commandedR)
      numTicks = round(self.duration / self.SERVO_TIME_MS / 6.0) #total ticks divided into the six cases
      for leg_num in range(0,6):
        self.compute_amplitudes(leg_num)
        if self.wave_case[leg_num] == 1:                               #move foot forward (raise and lower)
          self.current_X[leg_num] = self.HOME_X[leg_num] - self.amplitudeX*math.cos(self.M_PI*self.tick/numTicks)
          self.current_Y[leg_num] = self.HOME_Y[leg_num] - self.amplitudeY*math.cos(self.M_PI*self.tick/numTicks)
          self.current_Z[leg_num] = self.HOME_Z[leg_num] + abs(self.amplitudeZ)*math.sin(self.M_PI*self.tick/numTicks)
          if self.tick >= numTicks-1: 
            self.wave_case[leg_num] = 6
        elif self.wave_case[leg_num] == 2:                               #move foot back one-fifth (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks/2.5
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks/2.5
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.wave_case[leg_num] = 1
        elif self.wave_case[leg_num] == 3:                               #move foot back one-fifth (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks/2.5
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks/2.5
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.wave_case[leg_num] = 2
        elif self.wave_case[leg_num] == 4:                               #move foot back one-fifth (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks/2.5
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks/2.5
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.wave_case[leg_num] = 3
        elif self.wave_case[leg_num] == 5:                               #move foot back one-fifth (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks/2.5
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks/2.5
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.wave_case[leg_num] = 4
        elif self.wave_case[leg_num] == 6:                               #move foot back one-fifth (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks/2.5
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks/2.5
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.wave_case[leg_num] = 5
      #increment tick
      if self.tick < numTicks-1:
        self.tick+=1
      else:
        self.tick = 0


  #***********************************************************************
  # Ripple Gait
  # Left legs move forward rear-to-front while right also do the same,
  # but right side is offset so RR starts midway through the LM stroke
  #***********************************************************************
  def ripple_gait(self):
    #read commanded values from controller
    val_x = self.controller.analog(self.THROTTLE_R) - self.controller.analog(self.THROTTLE_L)
    commandedY = map(val_x, -255, 255, 127, -127)
    
    commandedX = map(self.controller.analog(self.AS_RY),0,255,127,-127) 
    commandedR = map(self.controller.analog(self.AS_RX),0,255,127,-127)

    #if commands more than deadband then process
    if abs(commandedX) > 15 or abs(commandedY) > 15 or abs(commandedR) > 15 or self.tick>0:
      self.compute_strides(commandedX, commandedY, commandedR)
      numTicks = round(self.duration / self.SERVO_TIME_MS / 6.0) #total ticks divided into the six cases
      for leg_num in range(0,6):
        self.compute_amplitudes(leg_num)
        if self.ripple_case[leg_num] == 1:                               #move foot forward (raise)
          self.current_X[leg_num] = self.HOME_X[leg_num] - self.amplitudeX*math.cos(self.M_PI*self.tick/(numTicks*2))
          self.current_Y[leg_num] = self.HOME_Y[leg_num] - self.amplitudeY*math.cos(self.M_PI*self.tick/(numTicks*2))
          self.current_Z[leg_num] = self.HOME_Z[leg_num] + abs(self.amplitudeZ)*math.sin(self.M_PI*self.tick/(numTicks*2))
          if self.tick >= numTicks-1:
            self.ripple_case[leg_num] = 2
        elif self.ripple_case[leg_num] == 2:                               #move foot forward (lower)
          self.current_X[leg_num] = self.HOME_X[leg_num] - self.amplitudeX*math.cos(self.M_PI*(numTicks+self.tick)/(numTicks*2))
          self.current_Y[leg_num] = self.HOME_Y[leg_num] - self.amplitudeY*math.cos(self.M_PI*(numTicks+self.tick)/(numTicks*2))
          self.current_Z[leg_num] = self.HOME_Z[leg_num] + abs(self.amplitudeZ)*math.sin(self.M_PI*(numTicks+self.tick)/(numTicks*2))
          if self.tick >= numTicks-1:
            self.ripple_case[leg_num] = 3
        elif self.ripple_case[leg_num] == 3:                               #move foot back one-quarter (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks/2.0
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks/2.0
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.ripple_case[leg_num] = 4
        elif self.ripple_case[leg_num] == 4:                               #move foot back one-quarter (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks/2.0
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks/2.0
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.ripple_case[leg_num] = 5
        elif self.ripple_case[leg_num] == 5:                               #move foot back one-quarter (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks/2.0
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks/2.0
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.ripple_case[leg_num] = 6
        elif self.ripple_case[leg_num] == 6:                               #move foot back one-quarter (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks/2.0
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks/2.0
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.ripple_case[leg_num] = 1

      #increment tick
      if self.tick < numTicks-1:
        self.tick+=1
      else:
        self.tick = 0


  #***********************************************************************
  # Tetrapod Gait
  # Right front and left rear legs move forward together, then right  
  # rear and left middle, and finally right middle and left front.
  #***********************************************************************
  def tetrapod_gait(self):
    #read commanded values from controller
    val_x = self.controller.analog(self.THROTTLE_R) - self.controller.analog(self.THROTTLE_L)
    commandedY = map(val_x, -255, 255, 127, -127)
    
    commandedX = map(self.controller.analog(self.AS_RY),0,255,127,-127) 
    commandedR = map(self.controller.analog(self.AS_RX),0,255,127,-127)

    #if commands more than deadband then process
    if abs(commandedX) > 15 or abs(commandedY) > 15 or abs(commandedR) > 15 or self.tick>0:
      self.compute_strides(commandedX, commandedY, commandedR)
      numTicks = round(self.duration / self.SERVO_TIME_MS / 3.0) #total ticks divided into the three cases
      for leg_num in range(0,6):
        self.compute_amplitudes(leg_num)
        if self.tetrapod_case[leg_num] == 1:                               #move foot forward (raise and lower)
          self.current_X[leg_num] = self.HOME_X[leg_num] - self.amplitudeX*math.cos(self.M_PI*self.tick/numTicks)
          self.current_Y[leg_num] = self.HOME_Y[leg_num] - self.amplitudeY*math.cos(self.M_PI*self.tick/numTicks)
          self.current_Z[leg_num] = self.HOME_Z[leg_num] + abs(self.amplitudeZ)*math.sin(self.M_PI*self.tick/numTicks)
          if self.tick >= numTicks-1:
            self.tetrapod_case[leg_num] = 2
          break
        elif self.tetrapod_case[leg_num] == 2:                               #move foot back one-half (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.tetrapod_case[leg_num] = 3
          break
        elif self.tetrapod_case[leg_num] == 3:                               #move foot back one-half (on the ground)
          self.current_X[leg_num] = self.current_X[leg_num] - self.amplitudeX/numTicks
          self.current_Y[leg_num] = self.current_Y[leg_num] - self.amplitudeY/numTicks
          self.current_Z[leg_num] = self.HOME_Z[leg_num]
          if self.tick >= numTicks-1:
            self.tetrapod_case[leg_num] = 1
      #increment tick
      if self.tick < numTicks-1:
        self.tick+=1
      else:
        self.tick = 0


  #***********************************************************************
  # Compute walking stride lengths
  #***********************************************************************
  def compute_strides(self, commandedX, commandedY, commandedR):
    #compute stride lengths
    self.strideX = 90*commandedX/127
    self.strideY = 90*commandedY/127
    self.strideR = 35*commandedR/127

    #compute rotation trig
    self.sinRotZ = math.sin(math.radians(self.strideR))
    self.cosRotZ = math.cos(math.radians(self.strideR))

    #set duration for normal and slow speed modes
    if self.gait_speed == 0:
      self.duration = 1080 
    else:
      self.duration = 3240


  #***********************************************************************
  # Compute walking amplitudes
  #***********************************************************************
  def compute_amplitudes(self, leg_num: int):
    #compute total distance from center of body to toe
    self.totalX = self.HOME_X[leg_num] + self.BODY_X[leg_num]
    self.totalY = self.HOME_Y[leg_num] + self.BODY_Y[leg_num]

    #compute rotational offset
    self.rotOffsetX = self.totalY*self.sinRotZ + self.totalX*self.cosRotZ - self.totalX
    self.rotOffsetY = self.totalY*self.cosRotZ - self.totalX*self.sinRotZ - self.totalY

    #compute X and Y amplitude and constrain to prevent legs from crashing into each other
    self.amplitudeX = ((self.strideX + self.rotOffsetX)/2.0)
    self.amplitudeY = ((self.strideY + self.rotOffsetY)/2.0)
    self.amplitudeX = constrain(self.amplitudeX,-50,50)
    self.amplitudeY = constrain(self.amplitudeY,-50,50)

    #compute Z amplitude
    if abs(self.strideX + self.rotOffsetX) > abs(self.strideY + self.rotOffsetY):
      self.amplitudeZ = self.step_height_multiplier * (self.strideX + self.rotOffsetX) /4.0
    else:
      self.amplitudeZ = self.step_height_multiplier * (self.strideY + self.rotOffsetY) / 4.0
        

  #***********************************************************************
  # Body translate with controller (xyz axes)
  #***********************************************************************
  def translate_control(self):
    #compute X direction move
    self.translateX = map(self.controller.analog(self.AS_RY),0,255,-2*self.TRAVEL,2*self.TRAVEL)
    for leg_num in range(0,6):
      self.current_X[leg_num] = self.HOME_X[leg_num] + self.translateX
      
    #compute Y direction move
    self.translateY = map(self.controller.analog(self.AS_RX),0,255,2*self.TRAVEL,-2*self.TRAVEL)
    for leg_num in range(0,6):
      self.current_Y[leg_num] = self.HOME_Y[leg_num] + self.translateY

    #compute Z direction move
    self.translateZ = self.controller.analog(self.AS_LY)
    if self.translateZ > 127:
      self.translateZ = map(self.translateZ,128,255,0,self.TRAVEL) 
    else:
      self.translateZ = map(self.translateZ,0,127,-3*self.TRAVEL,0)    
    for leg_num in range(0,6):
      self.current_Z[leg_num] = self.HOME_Z[leg_num] + self.translateZ

    #lock in offsets if commanded
    if self.capture_offsets == True:
      for leg_num in range(0,6):
        self.offset_X[leg_num] = self.offset_X[leg_num] + self.translateX
        self.offset_Y[leg_num] = self.offset_Y[leg_num] + self.translateY
        self.offset_Z[leg_num] = self.offset_Z[leg_num] + self.translateZ
        self.current_X[leg_num] = self.HOME_X[leg_num]
        self.current_Y[leg_num] = self.HOME_Y[leg_num]
        self.current_Z[leg_num] = self.HOME_Z[leg_num]

      logger.info("Offsets are saved")
      self.capture_offsets = False
      self.set_mode(self.MODE_IDLE)


  #***********************************************************************
  # Body rotate with controller (xyz axes)
  #***********************************************************************
  def rotate_control(self):
    #compute rotation sin/cos values using controller inputs
    sinRotX = math.sin((map(self.controller.analog(self.AS_RX),0,255,self.A12DEG,-self.A12DEG))/1000000.0)
    cosRotX = math.cos((map(self.controller.analog(self.AS_RX),0,255,self.A12DEG,-self.A12DEG))/1000000.0)
    sinRotY = math.sin((map(self.controller.analog(self.AS_RY),0,255,self.A12DEG,-self.A12DEG))/1000000.0)
    cosRotY = math.cos((map(self.controller.analog(self.AS_RY),0,255,self.A12DEG,-self.A12DEG))/1000000.0)
    self.sinRotZ = math.sin((map(self.controller.analog(self.AS_LX),0,255,-self.A30DEG,self.A30DEG))/1000000.0)
    self.cosRotZ = math.cos((map(self.controller.analog(self.AS_LX),0,255,-self.A30DEG,self.A30DEG))/1000000.0)

    #compute Z direction move
    self.translateZ = self.controller.analog(self.AS_LY)
    if self.translateZ > 127:
      self.translateZ = map(self.translateZ,128,255,0,self.TRAVEL) 
    else:
      self.translateZ = map(self.translateZ,0,127,-3*self.TRAVEL,0)    

    for leg_num in range(0,6):
      #compute total distance from center of body to toe
      self.totalX = self.HOME_X[leg_num] + self.BODY_X[leg_num]
      self.totalY = self.HOME_Y[leg_num] + self.BODY_Y[leg_num]
      self.totalZ = self.HOME_Z[leg_num] + self.BODY_Z[leg_num]

      #perform 3 axis rotations
      self.rotOffsetX =  self.totalX*cosRotY*self.cosRotZ + self.totalY*sinRotX*sinRotY*self.cosRotZ + self.totalY*cosRotX*self.sinRotZ - self.totalZ*cosRotX*sinRotY*self.cosRotZ + self.totalZ*sinRotX*self.sinRotZ - self.totalX
      self.rotOffsetY = -self.totalX*cosRotY*self.sinRotZ - self.totalY*sinRotX*sinRotY*self.sinRotZ + self.totalY*cosRotX*self.cosRotZ + self.totalZ*cosRotX*sinRotY*self.sinRotZ + self.totalZ*sinRotX*self.cosRotZ - self.totalY
      self.rotOffsetZ =  self.totalX*sinRotY         - self.totalY*sinRotX*cosRotY                                  + self.totalZ*cosRotX*cosRotY                                  - self.totalZ

      # Calculate foot positions to achieve desired rotation
      self.current_X[leg_num] = self.HOME_X[leg_num] + self.rotOffsetX
      self.current_Y[leg_num] = self.HOME_Y[leg_num] + self.rotOffsetY
      self.current_Z[leg_num] = self.HOME_Z[leg_num] + self.rotOffsetZ + self.translateZ

      #lock in offsets if commanded
      if self.capture_offsets == True:
        self.offset_X[leg_num] = self.offset_X[leg_num] + self.rotOffsetX
        self.offset_Y[leg_num] = self.offset_Y[leg_num] + self.rotOffsetY
        self.offset_Z[leg_num] = self.offset_Z[leg_num] + self.rotOffsetZ + self.translateZ
        self.current_X[leg_num] = self.HOME_X[leg_num]
        self.current_Y[leg_num] = self.HOME_Y[leg_num]
        self.current_Z[leg_num] = self.HOME_Z[leg_num]

    #if offsets were commanded, exit current mode
    if self.capture_offsets == True:
      self.capture_offsets = False
      self.set_mode(self.MODE_IDLE)


  #***********************************************************************
  # One leg lift mode
  # also can set z step height using capture offsets
  #***********************************************************************
  def one_leg_lift(self):
    #read current leg servo 1 positions the first time
    if self.leg1_IK_control == True:
      self.leg1_coxa  = self.coxa1_servo.read() 
      self.leg1_femur = self.femur1_servo.read() 
      self.leg1_tibia = self.tibia1_servo.read() 
      self.leg1_IK_control = False

    #read current leg servo 6 positions the first time
    if self.leg6_IK_control == True:
      self.leg6_coxa  = self.coxa6_servo.read() 
      self.leg6_femur = self.femur6_servo.read() 
      self.leg6_tibia = self.tibia6_servo.read() 
      self.leg6_IK_control = False

    #process right joystick left/right axis
    self.temp = self.controller.analog(self.AS_RX)
    self.temp = map(self.temp,0,255,45,-45)
    self.coxa1_servo.write(constrain(int(self.leg1_coxa+self.temp),45,135))

    #process right joystick up/down axis
    self.temp = self.controller.analog(self.AS_RY)
    if self.temp < 117:                                #if joystick moved up
      self.temp = map(self.temp,116,0,0,24)                #move leg 1
      self.femur1_servo.write(constrain(int(self.leg1_femur+self.temp),0,170))
      self.tibia1_servo.write(constrain(int(self.leg1_tibia+4*self.temp),0,170))
    else:                                          #if joystick moved down
      self.z_height_right = constrain(self.temp,140,255)   #set Z step height
      self.z_height_right = map(self.z_height_right,140,255,1,8)

    #process left joystick left/right axis
    self.temp = self.controller.analog(self.AS_LX)
    self.temp = map(self.temp,0,255,45,-45)
    self.coxa6_servo.write(constrain(int(self.leg6_coxa+self.temp),45,135))

    #process left joystick up/down axis
    self.temp = self.controller.analog(self.AS_LY)
    if self.temp < 117:                                #if joystick moved up
      self.temp = map(self.temp,116,0,0,24)                #move leg 6
      self.femur6_servo.write(constrain(int(self.leg6_femur+self.temp),0,170))
      self.tibia6_servo.write(constrain(int(self.leg6_tibia+4*self.temp),0,170))
    else:                                          #if joystick moved down
      self.z_height_left = constrain(self.temp,140,255)    #set Z step height
      self.z_height_left = map(self.z_height_left,140,255,1,8)

    #process z height adjustment
    if self.z_height_left>self.z_height_right: 
      self.z_height_right = self.z_height_left             #use max left or right value
    if self.capture_offsets == True:                   #lock in Z height if commanded
      self.step_height_multiplier = 1.0 + ((self.z_height_right - 1.0) / 3.0)
      self.capture_offsets = False


  #***********************************************************************
  # Set all servos to 90 degrees
  # Note: this is useful for calibration/alignment of the servos
  # i.e: set COXA_CAL[6], FEMUR_CAL[6], and TIBIA_CAL[6] values in  
  #      constants section above so all angles appear as 90 degrees
  #***********************************************************************
  def set_all_90(self):
    self.coxa1_servo.write(90+self.COXA_CAL[0]) 
    self.femur1_servo.write(90+self.FEMUR_CAL[0]) 
    self.tibia1_servo.write(90+self.TIBIA_CAL[0]) 
    
    self.coxa2_servo.write(90+self.COXA_CAL[1]) 
    self.femur2_servo.write(90+self.FEMUR_CAL[1]) 
    self.tibia2_servo.write(90+self.TIBIA_CAL[1]) 
    
    self.coxa3_servo.write(90+self.COXA_CAL[2]) 
    self.femur3_servo.write(90+self.FEMUR_CAL[2]) 
    self.tibia3_servo.write(90+self.TIBIA_CAL[2]) 
    
    self.coxa4_servo.write(90+self.COXA_CAL[3]) 
    self.femur4_servo.write(90+self.FEMUR_CAL[3]) 
    self.tibia4_servo.write(90+self.TIBIA_CAL[3]) 
    
    self.coxa5_servo.write(90+self.COXA_CAL[4]) 
    self.femur5_servo.write(90+self.FEMUR_CAL[4]) 
    self.tibia5_servo.write(90+self.TIBIA_CAL[4]) 
    
    self.coxa6_servo.write(90+self.COXA_CAL[5]) 
    self.femur6_servo.write(90+self.FEMUR_CAL[5]) 
    self.tibia6_servo.write(90+self.TIBIA_CAL[5])



  #***********************************************************************
  # Print Debug Data
  #***********************************************************************
  def print_debug(self):
    #display elapsed frame time (ms) and battery voltage (V)
    if self.n_cycles % 1000 == 0:
      self.currentTime = self.get_current_time_ms()
      logger.debug("%s, %s",self.currentTime-self.previousTime,float(self.batt_voltage)/100.0)

  def set_mode(self, mode_id: int) -> None:
    if self.mode != mode_id:
      logger.info("%s mode applied", self.mode_id_to_name.get(mode_id))
      if mode_id == 1:
        logger.info("%s gait applied", self.gait_id_to_name.get(self.gait))
      self.mode = mode_id
    
  def set_gait(self, gait_id: int) -> None:
    if self.gait != gait_id:
      logger.info("%s gait selected (but not applied)", self.gait_id_to_name.get(gait_id))
      self.gait = gait_id


  @staticmethod
  def get_current_time_ms():
    return round(time.time() * 1000)

  def reload_config(self):
    if not os.path.exists(self.config_file_path):
      logger.warning("Config file not found. Wirting default values to %s", self.config_file_path)
      self.write_config()

    logger.info("Loading config from %s", self.config_file_path)
    with open(self.config_file_path, 'rt') as f:
      config = json.loads(f.read())
      for key, values in config.items():
        if key in self.cal_values:
          for k, v in enumerate(values):
            if k< len(self.cal_values[k]):
              self.cal_values[k] = v
      self.COXA_CAL = config["COXA_CAL"]
      self.FEMUR_CAL = config["FEMUR_CAL"]
      self.TIBIA_CAL = config["TIBIA_CAL"]


  def write_config(self):
    config = {
        "COXA_CAL": self.COXA_CAL,
        "FEMUR_CAL": self.FEMUR_CAL,
        "TIBIA_CAL": self.TIBIA_CAL
    }
    with open(self.config_file_path, 'wt') as f:
      f.write(json.dumps(config, indent=4))
