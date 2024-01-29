from decimal import Decimal

DEFAULT_NUMBER_OF_DECIMALS = 3
START_POSITION = [0, 0, 0]

def get_limit_number_of_decimals(number_of_decimals):
    return Decimal('1.{}'.format('0' * number_of_decimals))

def set_to_decimal(value, number_of_decimals):
    number_of_decimals = get_limit_number_of_decimals(number_of_decimals)

    return Decimal(value).quantize(number_of_decimals)


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

# class RotationType:
#     RT_LWH = 0
#     RT_HLW = 1
#     RT_HWL = 2
#     RT_WHL = 3
#     RT_WLH = 4
#     RT_LHW = 5
    
#     ALL = [RT_LWH, RT_HLW, RT_HWL, RT_WHL, RT_WLH, RT_LHW]


class Item:
    def __init__(self, name, length, width, height, weight,kind="",item_ID=""):
        self.name = str(name) # 这个就是item的编号，可以用来验证两个item是否是同一个
        self.item_ID=item_ID
        self.length = length
        self.width = width
        self.height = height
        self.scale=[length,width,height]
        self.weight = weight
        self.kind=kind
        self.rotation_type = 0 # initial rotation type: (x, y, z) --> (l, w, h)
        self.position = 0#START_POSITION # initial position: (0, 0, 0)
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
        self.v=self.get_volume()
        self.s=self.width*self.length
    
    def format_numbers(self, number_of_decimals):
        self.length = set_to_decimal(self.length, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.weight = set_to_decimal(self.weight, number_of_decimals)
        self.number_of_decimals = number_of_decimals
        
    def get_volume(self):
        return set_to_decimal(
            self.length * self.height * self.width, self.number_of_decimals)
    
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
    
    # def get_dimension(self): # 6 orientation types -- (x-axis, y-axis, z-axis)
    #     if self.rotation_type == RotationType.RT_LWH:
    #         dimension = [self.length, self.width, self.height]
    #     elif self.rotation_type == RotationType.RT_HLW:
    #         dimension = [self.height, self.length, self.width]
    #     elif self.rotation_type == RotationType.RT_HWL:
    #         dimension = [self.height, self.width, self.length]
    #     elif self.rotation_type == RotationType.RT_WHL:
    #         dimension = [self.width, self.height, self.length]
    #     elif self.rotation_type == RotationType.RT_WLH:
    #         dimension = [self.width, self.length, self.height]
    #     elif self.rotation_type == RotationType.RT_LHW:
    #         dimension = [self.length, self.height, self.width]
    #     else:
    #         dimension = []
        
    #     return dimension
        
    def string(self):
        return "%s(%sx%sx%s, weight: %s) pos(%s) rt(%s) vol(%s)" % (
            self.name, self.length, self.width, self.height, self.weight,
            self.position, self.rotation_type, self.get_volume()
        )
    
    
class Block(Item):
    def __init__(self, name,parent_items,kind="",item_ID=""):
        self.name = str(name) # 名起为“B”+global_item_ID
        self.item_ID=item_ID
        for item in parent_items:
            if (item.length!=parent_items[0].length and item.width!=parent_items[0].width) or (item.length!=parent_items[0].width and item.width!=parent_items[0].length):
                pass
            else:  # 检查所有item是否长宽一致
                raise AssertionError(f"items in the block don't have the same width and length, where item {item.item_ID} has length {item.length} and width {item.width} but item {parent_items[0].item_ID} has length {parent_items[0].length} and width {parent_items[0].width}")
        
        self.length = item.length
        self.width = item.width
        self.height = sum(i.height for i in parent_items)
        self.scale=[self.length,self.width,self.height]
        self.weight = sum(i.weight for i in parent_items)
        self.kind=kind
        self.rotation_type = 0 # initial rotation type: (x, y, z) --> (l, w, h)
        self.position = 0#START_POSITION # initial position: (0, 0, 0)
        self.number_of_decimals = DEFAULT_NUMBER_OF_DECIMALS
        self.v=self.get_volume()
        self.s=self.length*self.width
        self.parent_items=sorted(parent_items,key=lambda x:x.weight,reverse=True)  # 从下往上越来越轻

    def disassembly(self):
        return self.parent_items