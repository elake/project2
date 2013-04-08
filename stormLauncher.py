#!/usr/bin/python

# Copyright 2012, Nathan Milford

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# The following script will control the Dream Cheeky Storm & Thunder USB
# Missile Launchers.  There are a few projects for using older launchers
# in Linux, but I couldn't find any for this launcher, so... enjoy.

# Thunder: http://www.dreamcheeky.com/thunder-missile-launcher
# O.I.C Storm: http://www.dreamcheeky.com/storm-oic-missile-launcher

# This script requires:
# * PyUSB 1.0+, apt in Debian/Ubuntu installs 0.4.
# * The ImageTk library. On Debian/Ubuntu 'sudo apt-get install python-imaging-tk'
# Also, unless you want to toggle with udev rules, it needs to be run as root

# Use arrows to aim.  Sse the left enter to fire.

# BTW, Leeroy Jenkins Mode .wav is from: http://www.leeroyjenkins.net/soundbites/warcry.wav

import os
import sys
import time
import usb.core
import math

class launchControl():
   def __init__(self):
      self.dev = usb.core.find(idVendor=0x2123, idProduct=0x1010)
      if self.dev is None:
         raise ValueError('Launcher not found.')
      if self.dev.is_kernel_driver_active(0) is True:
         self.dev.detach_kernel_driver(0)
      self.dev.set_configuration()

      # state:
      self.face_left_fully()
      self._current_facing = 0
      self._bullets = 4

      # determined via experimentation:
      self._rotation_rate = 49.3
      self._pitch_up_rate = 64.748
      self._pitch_down_rate = 59.603
      
      self._shot_time = 1.0
      self._full_firing_time = 3.5

   # Accessors:
   def get_facing(self):
      return self._current_facing

   def get_rotation_rate(self):
      return self._rotation_rate

   def get_pitch_up_rate(self):
      return self._pitch_up_rate

   def get_pitch_down_rate(self):
      return self._pitch_down_rate

   def get_firing_time(self, full = None):
      if full:
         return self._full_firing_time
      return self._shot_time

   def set_facing(self, facing):
      self._current_facing = facing

   def can_fire(self):
      return self._bullets

   def decrement_bullets(self):
      self._bullets += -1


   # Commands:
   def turretUp(self):
      self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x02,0,0,0,0,0,0])
      
   def turretDown(self):
      self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x01,0,0,0,0,0,0])

   def turretLeft(self):
      self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x04,0,0,0,0,0,0])

   def turretRight(self):
      self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x08,0,0,0,0,0,0])

   def turretStop(self):
      self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x20,0,0,0,0,0,0])

   def turretFire(self):
      if self.can_fire():
         self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x10,0,0,0,0,0,0])
         self.decrement_bullets()
         # rotation rate is not precise, so we reset every shot so that errors
         # in approximating rotation rates do not build upon themselves
         time.sleep(self.get_firing_time(1))
         self.face_left_fully() 

   def rotate_left_for(self, seconds):
      self.turretLeft()
      time.sleep(float(seconds))
      self.turretStop()

   def rotate_right_for(self, seconds):
      self.turretRight()
      time.sleep(float(seconds))
      self.turretStop()
      
   def face_left_fully(self):
      self.turretLeft()
      time.sleep(6.0)
      self.turretStop()
      self.set_facing(0)

   # Other:
   def turn_time(self, angle):
      '''
      the amount of time it will take for me to turn by angle
      '''
      rotation_rate = self.get_rotation_rate()
      return angle / rotation_rate
      
   def angle_to_left(self, angle):
      return (angle - self.get_facing() < 0)

   def face_angle(self, angle):
      """
      turns the launcher to face the given angle, and updates the stored
      _current_facing accordingly.
      """
      facing = self.get_facing()
      rotation_needed = abs(angle - facing) # the amount I need to rotate

      rotation_time = self.turn_time(rotation_needed) 
      
      if (self.angle_to_left(angle)): # rotate for determined time to face angle
         self.rotate_left_for(rotation_time)
      else:
         self.rotate_right_for(rotation_time)

      self.set_facing(angle)
      print(self.get_facing())

   def lead_target(self, target_angle, target_velocity):
      '''
      turn to and fire at the nearest spot this launcher will be able to hit the
      target with the given radial velocity, using this launcher's rate of 
      rotation and firing time.
      '''
      rot_rate = self.get_rotation_rate()
      fire_time = self.get_firing_time()

      time = (target_velocity * fire_time) + target_angle
      time = time / (rot_rate - target_velocity)

      target_velocity = abs(target_velocity)

      target_rev_time = 360 / target_velocity # target's revolution time
      clip = target_rev_time*math.ceil(fire_time / target_rev_time)

      angle = time * rot_rate
      self.face_angle(angle % 270)
      #print(repr((angle / target_velocity)))
      print("clip = {}".format(repr(clip)))
      print("angle = {}".format(angle))
      print("target_velocity = {}".format(target_velocity))
      retval = (angle / target_velocity) % clip - ((angle % 270) / rot_rate)
      print("retval = {}".format(retval))
      return retval


if __name__ == '__main__':
   pass
   '''
   turret = launchControl()
   j = 0
   while 1:
      turret.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x10,0,0,0,0,0,0])
      time.sleep(3.5)
      
      j += 0.1
      turret.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x10,0,0,0,0,0,0])
      time.sleep(j)
      turret.turretStop()
      print(j)
      time.sleep(3.5)
   '''


   

