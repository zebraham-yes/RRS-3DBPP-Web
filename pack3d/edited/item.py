
DEFAULT_NUMBER_OF_DECIMALS = 3
START_POSITION = [0, 0, 0]


# length in x-axis; width in y-axis; height in z-axis
class RotationType:
    RT_LWH = 0
    RT_WLH = 1

    # RT_HLW = 1
    # RT_HWL = 2
    # RT_WHL = 3
    # RT_WLH = 4
    # RT_LHW = 5
    
    # ALL = [RT_LWH, RT_HLW, RT_HWL, RT_WHL, RT_WLH, RT_LHW]
    ALL = [RT_LWH, RT_WLH]
    

class Item:
    def __init__(self, name, length, width, height, weight):
        self.name = name
        self.length = length
        self.width = width
        self.height = height
        self.weight = weight
        self.scale=[length,width,height]
        self.rotation_type = 0 # initial rotation type: (x, y, z) --> (l, w, h)
        self.position = START_POSITION # initial position: (0, 0, 0)
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
    

        
    def get_volume(self):
        return self.length * self.height * self.width
    
    def get_dimension(self): # 6 orientation types -- (x-axis, y-axis, z-axis)
        if self.rotation_type == RotationType.RT_LWH:
            dimension = [self.length, self.width, self.height]
        # elif self.rotation_type == RotationType.RT_HLW:
        #     dimension = [self.height, self.length, self.width]
        # elif self.rotation_type == RotationType.RT_HWL:
        #     dimension = [self.height, self.width, self.length]
        # elif self.rotation_type == RotationType.RT_WHL:
        #     dimension = [self.width, self.height, self.length]
        elif self.rotation_type == RotationType.RT_WLH:
            dimension = [self.width, self.length, self.height]
        # elif self.rotation_type == RotationType.RT_LHW:
        #     dimension = [self.length, self.height, self.width]
        else:
            dimension = []
        
        return dimension
        
    def string(self):
        return "%s(%sx%sx%s, weight: %s) pos(%s) rt(%s) vol(%s)" % (
            self.name, self.length, self.width, self.height, self.weight,
            self.position, self.rotation_type, self.get_volume()
        )