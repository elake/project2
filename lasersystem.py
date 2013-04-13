'''
this is the class for representing a series of lasers
'''
max_rotation = 270

class LaserSystem():
    '''
    simple laser system class
    '''
    def __init__(self, num_lasers):
        self._num_lasers = num_lasers
        self._spread = (max_rotation / (num_lasers - 1))
        self._facing = 0

        # store the angles of each laser in a dictionary for faster access
        self._angles = dict()        
        n = 0
        for i in range(num_lasers):
            self._angles[i] = n
            n += self._spread

    def get_angle(self, laser):
        '''
        return the angle of the given laser, relative to the default facing of
        0 degrees (defined by the 0th laser)
        '''
        return (self._angles[laser])
    
    
