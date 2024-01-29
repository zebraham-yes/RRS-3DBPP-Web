from decimal import Decimal
from numpy import array
from numpy.linalg import norm

DEFAULT_NUMBER_OF_DECIMALS = 3
START_POSITION = [0, 0, 0]

def get_limit_number_of_decimals(number_of_decimals):
    return Decimal('1.{}'.format('0' * number_of_decimals))

def set_to_decimal(value, number_of_decimals):
    number_of_decimals = get_limit_number_of_decimals(number_of_decimals)

    return Decimal(value).quantize(number_of_decimals)

def in_rectangle(xy1,xy2,pointxy):  # 验证一个点是不是在矩形内（仅适用于xy2比xy1大的情形）
    # print(xy1,xy2,pointxy)
    # print(xy1[0]<pointxy[0]<xy2[0])
    # print(xy1[1]<pointxy[1]<xy2[1])
    return (xy1[0]<pointxy[0]<xy2[0]) and (xy1[1]<pointxy[1]<xy2[1])

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


# class RotationType:
#     RT_LWH = 0
#     RT_HLW = 1
#     RT_HWL = 2
#     RT_WHL = 3
#     RT_WLH = 4
#     RT_LHW = 5
    
#     ALL = [RT_LWH, RT_HLW, RT_HWL, RT_WHL, RT_WLH, RT_LHW]


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
    
    def format_numbers(self, number_of_decimals):
        self.length = set_to_decimal(self.length, number_of_decimals)
        self.height = set_to_decimal(self.height, number_of_decimals)
        self.width = set_to_decimal(self.width, number_of_decimals)
        self.capacity = set_to_decimal(self.capacity, number_of_decimals)
        self.number_of_decimals = number_of_decimals
    
    def get_volume(self):
        return set_to_decimal(
            self.length * self.height * self.width, self.number_of_decimals)
     
    def get_total_weight(self):
        total_weight = 0
        
        for item in self.items:
            total_weight += item.weight
        
        return set_to_decimal(total_weight, self.number_of_decimals)
    
    def get_filling_ratio(self):
        total_filling_volume = 0
        total_filling_ratio = 0
        
        for item in self.items:
            total_filling_volume += item.get_volume()
            
        total_filling_ratio = total_filling_volume / self.get_volume()
        return set_to_decimal(total_filling_ratio, self.number_of_decimals)
    
    def get_weight_ratio(self):
        return self.get_total_weight()/self.capacity

    def get_s_ratio(self):
        s_sum=sum([item.length*item.width for item in self.items])
        return s_sum/(self.length*self.width)
    
    def can_hold_item_with_rotation(self, item, pivot): 
        """Evaluate whether one item can be placed into bin with all optional orientations.
        Args:
            item: any item in item list.
            pivot: an (x, y, z) coordinate, the back-lower-left corner of the item will be placed at the pivot.
            其实pivot就是关键点
        Returns:
            a list containing all optional orientations. If not, return an empty list.
        """
        
        fit = False 
        item.position = pivot
        # print(pivot,type(pivot))
        # if (pivot==array([0,0,0])).all():
        #     print("warning")

        rotation_type_list = []   # 在这个pivot上，有几种rotation是可以允许的
        if self.get_total_weight() + item.weight > self.capacity: # estimate whether bin reaches its capacity
            item.position = 0#[0, 0, 0]
            return rotation_type_list  # 如果超重了，那就没有任何rotation是可以的，返回空列表
        
        for i in range(0, len(RotationType.ALL)): 
            item.rotation_type = i
            dimension = item.get_dimension()    #根据item的rotationtype获取了item的xyz方向长度
            if (
                pivot[0] + dimension[0] <= self.length and  # x-axis
                pivot[1] + dimension[1] <= self.width and  # y-axis
                pivot[2] + dimension[2] <= self.height     # z-axis
            ):
            # 验证了是否在箱子里面
                fit = True
                
                for current_item_in_bin in self.items:   # 验证是否与其它已经装入的item相交，相交了返回false
                    if intersect(current_item_in_bin, item): 
                        fit = False
                        # item.position = 0#[0, 0, 0]不同在这里设置，后面会针对fit=False的情形统一设置
                        break
                # ————————————这里要增加一个验证：验证相互压的货物情况！！！————————————
                z_level=pivot[2]  # 高度
                # print("height",z_level)
                if z_level != 0:  # 如果不在地面上
                    supported=False
                    if item.rotation_type==0:
                        # item1_x=item.width + pivot[0]
                        # item1_y=item.length + pivot[1]
                        item1_vector=array([item.length,item.width])
                    else:
                        # item1_x=item.length + pivot[0]
                        # item1_y=item.width + pivot[1]
                        item1_vector=array([item.width,item.length])
                    

                    for item2 in self.items:
                        # print(item2.position[2]+item2.height)
                        if (item2.position[2]+item2.height)==z_level:  # 如果存在与该货物同等高度的其它货物，就看看是不是上下关系
                            if item2.rotation_type==0:
                                # item2_x=item.width + item2.position[0]
                                # item2_y=item.length + item2.position[1]
                                item2_vector=array([item2.length,item2.width])
                            else:  # 旋转了90度
                                # item2_x=item.length + item2.position[0]
                                # item2_y=item.width+ item2.position[1]
                                item2_vector=array([item2.width,item2.length])

                            # 求对角线两点的坐标
                            item1_pos_xy1=array(pivot[:2])
                            # item1_pos_xy2=array([item1_x,item1_y])
                            item1_pos_xy2=item1_pos_xy1+item1_vector

                            item2_pos_xy1=array(item2.position[:2])
                            item2_pos_xy2=item2_pos_xy1+item2_vector
                            
                            item1_pos_xy1_shrink=item1_pos_xy1+item1_vector/norm(item1_vector)/1000 # decimal只能同整数进行运算
                            item1_pos_xy2_shrink=item1_pos_xy2-item1_vector/norm(item1_vector)/1000
                            item2_pos_xy1_shrink=item2_pos_xy1+item2_vector/norm(item2_vector)/1000
                            item2_pos_xy2_shrink=item2_pos_xy2-item2_vector/norm(item2_vector)/1000
                            if in_rectangle(item1_pos_xy1,item1_pos_xy2,item2_pos_xy1_shrink) or in_rectangle(item1_pos_xy1,item1_pos_xy2,   # 如果第三个变量在以前两个变量为对角线的矩形里
                                item2_pos_xy2_shrink) or in_rectangle(item2_pos_xy1,item2_pos_xy2,item1_pos_xy1_shrink) or in_rectangle(item2_pos_xy1,item2_pos_xy2,item1_pos_xy2_shrink):
                            # if in_rectangle(item2_pos_xy1,item2_pos_xy2,item1_pos_xy1_shrink) or in_rectangle(item2_pos_xy1,item2_pos_xy2,item1_pos_xy2_shrink):
                                supported=True
                                if item.kind!=item2.kind:  # 不同类货物混放则不行
                                    fit=False
                                elif item.kind==item2.kind=="shelf":  # 货架只能同类互压
                                    if item.item_ID!=item2.item_ID:
                                        fit=False
                                    if (item1_pos_xy1.tolist()!=item2_pos_xy1.tolist()) or (item1_pos_xy2.tolist()!=item2_pos_xy2.tolist()):
                                        fit = False
                                elif item.kind==item2.kind=="collar":  # 如果都是围板箱，必须同样尺寸
                                    if (item1_pos_xy1.tolist()!=item2_pos_xy1.tolist()) or (item1_pos_xy2.tolist()!=item2_pos_xy2.tolist()):
                                        fit = False
                                # elif item.    # 增加判断条件：上面的货物压强不能超过下面的1.5倍
                                
                    if not supported:
                        fit = False

                if fit: 
                    rotation_type_list.append(item.rotation_type)   # 表示这种rotation是可以的
            
            else:
                continue 

        if not rotation_type_list:  # 如果没有一个rotation是好用的
            item.position=0

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
        rotation_type_list = self.can_hold_item_with_rotation(item, pivot)   # 对于一个pivot，有哪几种rotation是可行的
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
            
            # 有几种放进去的方式
            if len(rotation_type_list) == 1: 
                item.rotation_type = rotation_type_list[0] 
                self.items.append(item)
                self.total_items += 1
                return fit 
            
            else:   # 如果有多种rotation都可以
                # 其实完全可以直接在这里加一个前置判断，让“剩余空间%某一方向长度==0”的方向优先，如果没有再按照“最小坐标差最小”来选装
                length_dist=self.length-pivot[0]
                width_dist=self.width-pivot[1]
                # 求出剩余空间的长宽
                rot0x,rot0x_res=length_dist//item.length,length_dist%item.length
                rot0y,rot0y_res=width_dist//item.width,width_dist%item.width
                rot1x,rot1x_res=length_dist//item.width,length_dist%item.width
                rot1y,rot1y_res=width_dist//item.length,width_dist%item.length
                four_places=[rot0y,rot1y,rot0x,rot1x]
                four_res=[rot0y_res,rot1y_res,rot0x_res,rot1x_res]
                
                # 同类货物还剩多少个
                if item.kind=="shelf":
                    num_same_item=len([i for i in self.unplaced_items if (i.item_ID==item.item_ID) and (i not in self.items)])  
                elif item.kind=="collar":
                    num_same_item=len([i for i in self.unplaced_items if (i.kind!="shelf") and (i.length==item.length and i.height==item.height and i.width==item.width) and (i not in self.items)])
                elif item.kind=="pallet":
                    num_same_item=len([i for i in self.unplaced_items if (i.kind=="pallet") and (i not in self.items)])
                
                for i in range(4):
                    if four_res[i]==0 and four_places[i]<=num_same_item:
                        if i==0 or i==2:
                            item.rotation_type=RotationType.RT_LWH   # 0
                        else:
                            item.rotation_type=RotationType.RT_WLH   # 1

                        self.items.append(item)
                        self.total_items += 1
                        return fit
            
                for rotation in rotation_type_list: 
                    item.rotation_type = rotation
                    dimension = item.get_dimension()
                    margins_3d = [distance_3d[0] - dimension[0], 
                                 distance_3d[1] - dimension[1], 
                                 distance_3d[2] - dimension[2]]  # 放置后，货物的顶点到箱子对角点的距离，目前的算法是尽可能让这个最小的维度最小
                    margins_3d_temp = sorted(margins_3d)  # 从小到大排序
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
