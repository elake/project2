'''
this is the class for representing a series of lasers
'''
max_rotation = 270

class LaserSystem():
    '''
    '''
    def __init__(self, num_lasers):
        self._num_lasers = num_lasers
        self._spread = (max_rotation / num_lasers)
        self._facing = 0

    def fire_at(self, laser):
        self.face(laser)
        


    
