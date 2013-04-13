'''
USB missile launcher class. Instantialization of dev and usb transmissions 
attributable to Nathan Milford at: https://github.com/nmilford
'''

import os
import sys
import time
import usb.core
import math

class Turret():
   '''
   this is the class of a USB missile launcher, complete with targetting and 
   firing capabilities.
   '''
   def __init__(self):
      # pyUSB stuff:
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

      # statistics, determined via experimentation:
      self._rotation_rate = 49.3
      self._pitch_up_rate = 64.748
      self._pitch_down_rate = 59.603
      
      self._shot_time = 1.0
      self._full_firing_time = 4.0

   # Accessors:
   def get_facing(self):
      '''
      get the curent facing of the turret, returns an angle relative to this 
      turret's far left, which is measured to be 0 degrees.
      '''
      return self._current_facing

   def get_rotation_rate(self):
      '''
      gets this turrets rate of rotation. Rotation rate is assumed to be 
      symmetric in both directions
      '''
      return self._rotation_rate

   def get_pitch_up_rate(self):
      '''
      gets the rate at which this turret pitches upward
      '''
      return self._pitch_up_rate

   def get_pitch_down_rate(self):
      '''
      gets the rate at which this turret pitches downward
      '''
      return self._pitch_down_rate

   def get_firing_time(self, full = None):
      '''
      gets this turret's firing rate. For this launcher there are two firing 
      rates:
      1) the time it takes for this launcher to fire a shot and
      2) the time it takes for this launcher to fire a shot and reload into 
      resting position

      because the reload time is substantially greater than the firing time, 
      this launcher reports on both possible states since lead_target is very 
      dependent on this gun's capacity for accurate self-evaluation.
      '''
      if full:
         return self._full_firing_time
      return self._shot_time

   def set_facing(self, facing):
      '''
      sets this launchers facing attribute to the given argument
      '''
      self._current_facing = facing

   def can_fire(self):
      '''
      determines if this launcher can fire, ie whether it has any remaining 
      bullets
      '''
      return self._bullets

   def decrement_bullets(self):
      '''
      reduces this launchers number of bullets by one
      '''
      self._bullets += -1


   # Commands: batch data sent via USB:
   def rotate_up(self):
      self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x02,0,0,0,0,0,0])
      
   def rotate_down(self):
      self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x01,0,0,0,0,0,0])

   def rotate_left(self):
      self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x04,0,0,0,0,0,0])

   def rotate_right(self):
      self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x08,0,0,0,0,0,0])

   def stop(self):
      self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x20,0,0,0,0,0,0])

   def fire(self):
      '''
      firing command; additionally, after each shot we fully rotate the launcher
      to the left; this was a necessity due to the launcher's inability to 
      determine its own state as well as the slight inaccuracy of our 
      measurements which when paired with the launcher's inability to rotate a 
      precise amount means that this launcher's errors in evaluating its own 
      state would compound after each shot and eliminate all hopes of accurate 
      firing
      '''
      if self.can_fire():
         self.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x10,0,0,0,0,0,0])
         # rotation rate is not precise, so we reset every shot so that errors
         # in approximating rotation rates do not build upon themselves
         time.sleep(self.get_firing_time(1))
         self.face_left_fully() 

   # Compund Commands
   def rotate_left_for(self, seconds):
      '''
      rotates this launcher to the left for the given number of seconds
      '''
      self.rotate_left()
      time.sleep(float(seconds))
      self.stop()

   def rotate_right_for(self, seconds):
      '''
      rotates this launcher t the right for the given number of seconds
      '''
      self.rotate_right()
      time.sleep(float(seconds))
      self.stop()
      
   def face_left_fully(self):
      '''
      faces this launcher fully to the left
      '''
      self.rotate_left()
      time.sleep(6.0)
      self.stop()
      self.set_facing(0)

   # Other:
   def turn_time(self, angle):
      '''
      the amount of time it will take for this launcher to turn by angle
      '''
      rotation_rate = self.get_rotation_rate()
      return angle / rotation_rate
      
   def angle_to_left(self, angle):
      '''
      determine if the given angle is to the left of this launcher's current 
      facing
      '''
      return (angle - self.get_facing() < 0)

   def face_angle(self, angle):
      """
      turns the launcher to face the given angle, and updates the stored facing
      accordingly.
      """
      facing = self.get_facing()
      rotation_needed = abs(angle - facing) # the amount I need to rotate

      rotation_time = self.turn_time(rotation_needed) # the time to rotate 
      
      if (self.angle_to_left(angle)): # rotate for determined time to face angle
         self.rotate_left_for(rotation_time)
      else:
         self.rotate_right_for(rotation_time)

      self.set_facing(angle)

   def lead_target(self, target_angle, target_velocity):
      '''
      turn to and fire at the nearest spot this launcher will be able to hit the
      target with the given radial velocity, using this launcher's rate of 
      rotation and firing time.
      '''
      rot_rate = self.get_rotation_rate()
      fire_time = self.get_firing_time()
      # determine the amount of time needed to catch up to the target
      time = (target_velocity * fire_time) + target_angle
      time = time / (rot_rate - target_velocity)

      target_rev_time = abs(360.0 / target_velocity) # target's revolution time

      # get the angle at which this launcher will catch the target
      angle = time * rot_rate
      if 0 < angle < 270: # can this launcher rotate there?
         # if so, face that way and return to the server that this launcher does
         # not need to wait to fire on the target
         self.face_angle(angle)
         return 0
      else:
         # if not, determine the amount of time this launcher needs to wait 
         # before the target will re-enter this launcher's current facing,
         # assuming the target is travelling at a constant angular velocity
         relative_target_facing = math.copysign(target_angle, target_velocity)
         time_until_aligned = (360-relative_target_facing)/abs(target_velocity)
         time_until_shot = time_until_aligned - fire_time
         
         extra_revs = 0
         if (fire_time-time_until_shot) > 0: # if I can't hit next time 'round
            # determine the number of revolutions the target needs to make
            # before I can shoot at it
            extra_revs = math.ceil((fire_time-time_until_shot)/target_rev_time)
         # return the time to shot to the server
         return time_until_shot + target_rev_time*extra_revs


if __name__ == '__main__':
   pass
   '''
   turret = Turret()
   j = 0
   while 1:
      turret.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x10,0,0,0,0,0,0])
      time.sleep(3.5)
      
      j += 0.1
      turret.dev.ctrl_transfer(0x21,0x09,0,0,[0x02,0x10,0,0,0,0,0,0])
      time.sleep(j)
      turret.stop()
      print(j)
      time.sleep(3.5)
   '''


   

