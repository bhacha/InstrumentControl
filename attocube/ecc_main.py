import os
import sys
import time
import numpy as np
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ecc100_control import ECC100Control
ecc = ECC100Control()


class Attocube:
    def __init__(self):
        self.ecc = ecc


    def get_position(self, axis):
        try:
            self._pos = self.ecc.get_position(axis)/1000
        except:
            print ('Could not get current position')

    def set_step_size(self, voltage, axis):
        try:
            self.ecc.set_amplitude(axis,voltage*1000)
        except:
            print('Could not change voltage')

    def set_step_freq(self,val,axis):
        try:
             self.ecc.set_frequency(axis,val*1000)
        except:
             print ('Could not change frequency')
             
    def get_step_freq(self,axis):
        try:
            self._freq = self.ecc.get_frequency(axis)/1000
        except:
            print('Could not get voltage')

    def take_step (self,axis,backwards=False):
        try:
            self.ecc.set_single_step(axis,backwards)
            time.sleep(0.2)
            self.position(axis)
        except:
             print ('Could not move stepwise')
             
    def halt (self,axis):
         try:
              self.ecc.stop_stepping(axis)
              time.sleep(0)
              self.position(axis)
         except:
              print('didnt stop')

    def move_by(self,axis,distance=None,targetRange=1000):
        if distance == None:
            raise ValueError("Must enter a value to move to a targeted position")
        self.ecc.move_enabled_feedback(axis)
        initialPosition = self.ecc.get_position(axis)
        self.ecc.set_target(axis,initialPosition+distance) # makes the target relative to the current position for easier use
        targetPosition = self.ecc.get_target(axis)
        if self.ecc.wait_until_position(axis):
            return
        if initialPosition < targetPosition:
            self.ecc.control_continuous_forward(axis,enable=True,set=True)
        elif initialPosition > targetPosition:
            self.ecc.control_continuous_backward(axis,enable=True,set=True)
        self.ecc.enable_output(axis)
        while not self.ecc.wait_until_position(axis,targetRange=targetRange):
            pass
        self.ecc.stop_stepping(axis)
        
    def move_to(self,axis,target=None,targetRange=1000):
        if target == None:
            raise ValueError("Must enter a value to move to a targeted position")
        self.ecc.move_enabled_feedback(axis)
        initialPosition = self.ecc.get_position(axis)
        targetPosition = self.ecc.get_target(axis)
        self.ecc.set_target(axis,target)
        targetPosition = self.ecc.get_target(axis)
        if self.ecc.wait_until_position(axis):
            return
        if initialPosition < targetPosition:
            self.ecc.control_continuous_forward(axis,enable=True,set=True)
        elif initialPosition > targetPosition:
            self.ecc.control_continuous_backward(axis,enable=True,set=True)
        self.ecc.enable_output(axis)
        while not self.ecc.wait_until_position(axis,targetRange=targetRange):
            pass
        self.ecc.stop_stepping(axis)