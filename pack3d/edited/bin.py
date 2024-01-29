DEFAULT_NUMBER_OF_DECIMALS = 3
START_POSITION = [0, 0, 0]

def rect_intersect(item1, item2, x, y):
    """Estimate whether two items get intersection in one dimension.
    Args:
        item1, item2: any two items in item list.
        x,y: Axis.LENGTH/ Axis.Height/ Axis.WIDTH.
    Returns:
        Boolean variable: False when two items get intersection in one dimension; True when two items do not intersect in one dimension.
    """
    
    d1 = item1.get_dimension() 
    d2 = item2.get_dimension() 
    
    cx1 = item1.position[x] + d1[x]/2 
    cy1 = item1.position[y] + d1[y]/2
    cx2 = item2.position[x] + d2[x]/2 
    cy2 = item2.position[y] + d2[y]/2
    
    ix = max(cx1, cx2) - min(cx1, cx2) # ix: |cx1-cx2|
    iy = max(cy1, cy2) - min(cy1, cy2) # iy: |cy1-cy2|
    
    return ix < (d1[x] + d2[x])/2 and iy < (d1[y] + d2[y])/2 

def intersect(item1, item2):
    """Estimate whether two items get intersection in 3D dimension.
    Args:
        item1, item2: any two items in item list.
    Returns:
        Boolean variable: False when two items get intersection; True when two items do not intersect.
    """
    
    return ( 
    rect_intersect(item1, item2, Axis.LENGTH, Axis.HEIGHT) and # xz dimension
    rect_intersect(item1, item2, Axis.HEIGHT, Axis.WIDTH) and # yz dimension
    rect_intersect(item1, item2, Axis.LENGTH, Axis.WIDTH)) # xy dimension

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

# (x, y, z) --> (length, width, height)
class Axis:
    LENGTH = 0
    WIDTH = 1
    HEIGHT = 2
    
    ALL = [LENGTH, WIDTH, HEIGHT]

class Bin:
    def __init__(self, size, length, width, height, capacity):
        self.size = size 
        self.length = length
        self.width = width
        self.height = height
        self.scale=[length,width,height]
        self.capacity = capacity
        self.total_items = 0 # number of total items in one bin
        self.items = [] # item in one bin -- a blank list initially
        self.unplaced_items = []
        self.unfitted_items = [] # unfitted item in one bin -- a blank list initially
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
    
    def get_volume(self):
        return self.length * self.height * self.width
     
    def get_total_weight(self):
        total_weight = 0
        
        for item in self.items:
            total_weight += item.weight
        
        return total_weight
    
    def get_filling_ratio(self):
        total_filling_volume = 0
        total_filling_ratio = 0
        
        for item in self.items:
            total_filling_volume += item.get_volume()
            
        total_filling_ratio = total_filling_volume / self.get_volume()
        return total_filling_ratio
    
    def can_hold_item_with_rotation(self, item, pivot): 
        """Evaluate whether one item can be placed into bin with all optional orientations.
        Args:
            item: any item in item list.
            pivot: an (x, y, z) coordinate, the back-lower-left corner of the item will be placed at the pivot.
        Returns:
            a list containing all optional orientations. If not, return an empty list.
        """
        
        fit = False 
        valid_item_position = [0, 0, 0]
        item.position = pivot 
        rotation_type_list = [] 
        
        
        for i in range(0, len(RotationType.ALL)): 
            item.rotation_type = i 
            dimension = item.get_dimension() 
            if (
                pivot[0] + dimension[0] <= self.length and  # x-axis
                pivot[1] + dimension[1] <= self.width and  # y-axis
                pivot[2] + dimension[2] <= self.height     # z-axis
            ):
            
                fit = True
                
                for current_item_in_bin in self.items: 
                    if intersect(current_item_in_bin, item): 
                        fit = False
                        item.position = [0, 0, 0]
                        break 
                
                if fit: 
                    if self.get_total_weight() + item.weight > self.capacity: # estimate whether bin reaches its capacity
                        fit = False
                        item.position = [0, 0, 0]
                        continue 
                    
                    else: 
                        rotation_type_list.append(item.rotation_type) 
            
            else:
                continue 
        
        return rotation_type_list 

    def put_item(self, item, pivot, distance_3d): 
        """Evaluate whether an item can be placed into a certain bin with which orientation. If yes, perform put action.
        Args:
            item: any item in item list.
            pivot: an (x, y, z) coordinate, the back-lower-left corner of the item will be placed at the pivot.
            distance_3d: a 3D parameter to determine which orientation should be chosen.
        Returns:
            Boolean variable: False when an item couldn't be placed into the bin; True when an item could be placed and perform put action.
        """
        
        fit = False 
        rotation_type_list = self.can_hold_item_with_rotation(item, pivot)
        margins_3d_list = []
        margins_3d_list_temp = []
        margin_3d = []
        margin_2d = []
        margin_1d = []
        
        n = 0
        m = 0
        p = 0
        
        if not rotation_type_list:
            return fit 
        
        else:
            fit = True 
            
            rotation_type_number = len(rotation_type_list)
            
            if rotation_type_number == 1: 
                item.rotation_type = rotation_type_list[0] 
                self.items.append(item)
                self.total_items += 1
                return fit 
            
            else: 
                for rotation in rotation_type_list: 
                    item.rotation_type = rotation
                    dimension = item.get_dimension()
                    margins_3d = [distance_3d[0] - dimension[0], 
                                 distance_3d[1] - dimension[1], 
                                 distance_3d[2] - dimension[2]]
                    margins_3d_temp = sorted(margins_3d)
                    margins_3d_list.append(margins_3d)
                    margins_3d_list_temp.append(margins_3d_temp)
                
                while p < len(margins_3d_list_temp):
                    margin_3d.append(margins_3d_list_temp[p][0])
                    p += 1
                
                p = 0
                while p < len(margins_3d_list_temp):
                    if margins_3d_list_temp[p][0] == min(margin_3d):
                        n += 1
                        margin_2d.append(margins_3d_list_temp[p][1])
                    
                    p += 1
                
                if n == 1:
                    p = 0
                    while p < len(margins_3d_list_temp):
                        if margins_3d_list_temp[p][0] == min(margin_3d):
                            item.rotation_type = rotation_type_list[p]
                            self.items.append(item)
                            self.total_items += 1
                            return fit 
                        
                        p += 1
                
                else:
                    p = 0
                    while p < len(margins_3d_list_temp):
                        if (
                            margins_3d_list_temp[p][0] == min(margin_3d) and
                            margins_3d_list_temp[p][1] == min(margin_2d)
                        ):
                            m += 1
                            margin_1d.append(margins_3d_list_temp[p][2])
                        
                        p += 1
                
                if m == 1:
                    p = 0
                    while p < len(margins_3d_list_temp):
                        if (
                            margins_3d_list_temp[p][0] == min(margin_3d) and
                            margins_3d_list_temp[p][1] == min(margin_2d)
                        ):
                            item.rotation_type = rotation_type_list[p]
                            self.items.append(item)
                            self.total_items += 1
                            return fit 
                        
                        p += 1
                
                else:
                    p = 0
                    while p < len(margins_3d_list_temp):
                        if (
                            margins_3d_list_temp[p][0] == min(margin_3d) and
                            margins_3d_list_temp[p][1] == min(margin_2d) and
                            margins_3d_list_temp[p][2] == min(margin_1d)
                        ):
                            item.rotation_type = rotation_type_list[p]
                            self.items.append(item)
                            self.total_items += 1
                            return fit 
                        
                        p += 1
        
    def string(self):
        return "%s(%sx%sx%s, max_weight:%s) vol(%s) item_number(%s) filling_ratio(%s)" % (
            self.size, self.length, self.width, self.height, self.capacity,
            self.get_volume(), self.total_items, self.get_filling_ratio())
