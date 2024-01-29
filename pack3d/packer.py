DEFAULT_NUMBER_OF_DECIMALS = 3
START_POSITION = [0, 0, 0]
from numpy import array
from pandas import DataFrame
from copy import copy

# (x, y, z) --> (length, width, height)
class Axis:
    LENGTH = 0
    WIDTH = 1
    HEIGHT = 2
    
    ALL = [LENGTH, WIDTH, HEIGHT]

class Packer:
    def __init__(self):
        self.bins = [] 
        self.unplaced_items = []
        self.placed_items = []
        self.unfit_items = []
        self.total_items = 0
        self.total_used_bins = 0 # not used yet
        self.used_bins = [] # not used yet
        self.max_items_got = 0
    
    def add_bin(self, bin):
        return self.bins.append(bin)
    
    def add_item(self, item): 
        """Add unplaced items into bin's unplaced_items list.
        Args:
            item: an unplaced item.
        Returns:
            The unplaced item is added into bin's unplaced_items list."""
        
        self.total_items += 1
        return self.unplaced_items.append(item) 
    
    def pivot_dict(self, bin, item):
        """For each item to be placed into a certain bin, obtain a corresponding comparison parameter of 
        each optional pivot that the item can be placed.
        Args:
            bin: a bin in bin list that a certain item will be placed into.
            item: an unplaced item in item list.
        Returns:
            a pivot_dict contain all optional pivot point and their comparison parameter(从关键点到原点斜对角的距离) of the item.
            a empty dict may be returned if the item couldn't be placed into the bin.

        """
        
        pivot_dict = {}
        can_put = False
        
        for axis in range(0, 3): 
            items_in_bin = bin.items 
            items_in_bin_temp = items_in_bin[:] # 复制一份
            
            # 对已经装进去的item进行两两比较
            n = 0
            while n < len(items_in_bin):
                pivot = [0, 0, 0] 
                
                if axis == Axis.LENGTH: # axis = 0/ x-axis
                    ib = items_in_bin[n]
                    pivot = [ib.position[0] + ib.get_dimension()[0],
                            ib.position[1],
                            ib.position[2]]
                    try_put_item = bin.can_hold_item_with_rotation(item, pivot) 
                    
                    if try_put_item: 
                        can_put = True
                        # q = 0
                        q = 0
                        ib_neigh_x_axis = []
                        ib_neigh_y_axis = []
                        ib_neigh_z_axis = []
                        right_neighbor = False
                        front_neighbor = False
                        above_neighbor = False
                        
                        # 对于其它的item
                        while q < len(items_in_bin_temp):
                            if items_in_bin_temp[q] == items_in_bin[n]: 
                                q += 1
                            
                            else:
                                ib_neighbor = items_in_bin_temp[q]
                                
                                if (
                                    ib_neighbor.position[0] > ib.position[0] + ib.get_dimension()[0] and 
                                    ib_neighbor.position[1] + ib_neighbor.get_dimension()[1] > ib.position[1] and 
                                    ib_neighbor.position[2] + ib_neighbor.get_dimension()[2] > ib.position[2] 
                                ): 
                                    right_neighbor = True
                                    x_distance = ib_neighbor.position[0] - (ib.position[0] + ib.get_dimension()[0])
                                    ib_neigh_x_axis.append(x_distance)
                                    
                                elif (
                                    ib_neighbor.position[1] >= ib.position[1] + ib.get_dimension()[1] and 
                                    ib_neighbor.position[0] + ib_neighbor.get_dimension()[0] > ib.position[0] + ib.get_dimension()[0] and 
                                    ib_neighbor.position[2] + ib_neighbor.get_dimension()[2] > ib.position[2] 
                                ):
                                    front_neighbor = True
                                    y_distance = ib_neighbor.position[1] - ib.position[1]
                                    ib_neigh_y_axis.append(y_distance)
                                
                                elif (
                                    ib_neighbor.position[2] >= ib.position[2] + ib.get_dimension()[2] and 
                                    ib_neighbor.position[0] + ib_neighbor.get_dimension()[0] > ib.position[0] + ib.get_dimension()[0] and 
                                    ib_neighbor.position[1] + ib_neighbor.get_dimension()[1] > ib.position[1] 
                                ):
                                    above_neighbor = True
                                    z_distance = ib_neighbor.position[2] - ib.position[2]
                                    ib_neigh_z_axis.append(z_distance)
                                
                                q += 1
                                
                        if not right_neighbor: 
                            x_distance = bin.length - (ib.position[0] + ib.get_dimension()[0])
                            ib_neigh_x_axis.append(x_distance)
                        
                        if not front_neighbor: 
                            y_distance = bin.width - ib.position[1]
                            ib_neigh_y_axis.append(y_distance)
                        
                        if not above_neighbor: 
                            z_distance = bin.height - ib.position[2]
                            ib_neigh_z_axis.append(z_distance)
                        
                        distance_3D = [min(ib_neigh_x_axis), min(ib_neigh_y_axis), min(ib_neigh_z_axis)]
                        pivot_dict[tuple(pivot)] = distance_3D
                
                elif axis == Axis.WIDTH: # axis = 1/ y-axis
                    ib = items_in_bin[n]
                    pivot = [ib.position[0],
                            ib.position[1] + ib.get_dimension()[1],
                            ib.position[2]]
                    try_put_item = bin.can_hold_item_with_rotation(item, pivot) 
                    
                    if try_put_item: 
                        can_put = True
                        q = 0
                        ib_neigh_x_axis = []
                        ib_neigh_y_axis = []
                        ib_neigh_z_axis = []
                        right_neighbor = False
                        front_neighbor = False
                        above_neighbor = False
                        
                        while q < len(items_in_bin_temp):
                            if items_in_bin_temp[q] == items_in_bin[n]: 
                                q += 1 
                            
                            else:
                                ib_neighbor = items_in_bin_temp[q]
                                
                                if (
                                    ib_neighbor.position[0] >= ib.position[0] + ib.get_dimension()[0] and 
                                    ib_neighbor.position[1] + ib_neighbor.get_dimension()[1] > ib.position[1] + ib.get_dimension()[1] and 
                                    ib_neighbor.position[2] + ib_neighbor.get_dimension()[2] > ib.position[2] 
                                ):
                                    right_neighbor = True
                                    x_distance = ib_neighbor.position[0] - ib.position[0]
                                    ib_neigh_x_axis.append(x_distance)
                                
                                elif (
                                    ib_neighbor.position[1] > ib.position[1] + ib.get_dimension()[1] and 
                                    ib_neighbor.position[0] + ib_neighbor.get_dimension()[0] > ib.position[0] and 
                                    ib_neighbor.position[2] + ib_neighbor.get_dimension()[2] > ib.position[2] 
                                ):
                                    front_neighbor = True
                                    y_distance = ib_neighbor.position[1] - (ib.position[1] + ib.get_dimension()[1])
                                    ib_neigh_y_axis.append(y_distance)
                                
                                elif (
                                    ib_neighbor.position[2] >= ib.position[2] + ib.get_dimension()[2] and 
                                    ib_neighbor.position[0] + ib_neighbor.get_dimension()[0] > ib.position[0] and 
                                    ib_neighbor.position[1] + ib_neighbor.get_dimension()[1] > ib.position[1] + ib.get_dimension()[1] 
                                ):
                                    above_neighbor = True
                                    z_distance = ib_neighbor.position[2] - ib.position[2]
                                    ib_neigh_z_axis.append(z_distance)
                                
                                q += 1
                        
                        if not right_neighbor: 
                            x_distance = bin.length - ib.position[0]
                            ib_neigh_x_axis.append(x_distance)
                        
                        if not front_neighbor: 
                            y_distance = bin.width - (ib.position[1] + ib.get_dimension()[1])
                            ib_neigh_y_axis.append(y_distance)
                        
                        if not above_neighbor: 
                            z_distance = bin.height - ib.position[2]
                            ib_neigh_z_axis.append(z_distance)
                        
                        distance_3D = [min(ib_neigh_x_axis), min(ib_neigh_y_axis), min(ib_neigh_z_axis)]
                        pivot_dict[tuple(pivot)] = distance_3D
            
                elif axis == Axis.HEIGHT: # axis = 2/ z-axis
                    ib = items_in_bin[n]
                    pivot = [ib.position[0],
                            ib.position[1],
                            ib.position[2] + ib.get_dimension()[2]]
                    try_put_item = bin.can_hold_item_with_rotation(item, pivot) 
                    
                    if try_put_item: 
                        can_put = True
                        q = 0
                        ib_neigh_x_axis = []
                        ib_neigh_y_axis = []
                        ib_neigh_z_axis = []
                        right_neighbor = False
                        front_neighbor = False
                        above_neighbor = False
                        
                        while q < len(items_in_bin_temp):
                            if items_in_bin_temp[q] == items_in_bin[n]: 
                                q += 1 
                            
                            else:
                                ib_neighbor = items_in_bin_temp[q]
                                
                                if (
                                    ib_neighbor.position[0] >= ib.position[0] + ib.get_dimension()[0] and 
                                    ib_neighbor.position[1] + ib_neighbor.get_dimension()[1] > ib.position[1] and 
                                    ib_neighbor.position[2] + ib_neighbor.get_dimension()[2] > ib.position[2] + ib.get_dimension()[2] 
                                ):
                                    right_neighbor = True
                                    x_distance = ib_neighbor.position[0] - ib.position[0]
                                    ib_neigh_x_axis.append(x_distance)
                                
                                elif (
                                    ib_neighbor.position[1] > ib.position[1] + ib.get_dimension()[1] and 
                                    ib_neighbor.position[0] + ib_neighbor.get_dimension()[0] > ib.position[0] and 
                                    ib_neighbor.position[2] + ib_neighbor.get_dimension()[2] > ib.position[2] + ib.get_dimension()[2] 
                                ):
                                    front_neighbor = True
                                    y_distance = ib_neighbor.position[1] - (ib.position[1] + ib.get_dimension()[1])
                                    ib_neigh_y_axis.append(y_distance)
                                
                                elif (
                                    ib_neighbor.position[2] >= ib.position[2] + ib.get_dimension()[2] and 
                                    ib_neighbor.position[1] + ib_neighbor.get_dimension()[1] > ib.position[1] and 
                                    ib_neighbor.position[0] + ib_neighbor.get_dimension()[0] > ib.position[0] 
                                ):
                                    above_neighbor = True
                                    z_distance = ib_neighbor.position[2] - ib.position[2]
                                    ib_neigh_z_axis.append(z_distance)
                                
                                q += 1
                                
                        if not right_neighbor: 
                            x_distance = bin.length - ib.position[0]
                            ib_neigh_x_axis.append(x_distance)
                        
                        if not front_neighbor: 
                            y_distance = bin.width - ib.position[1]
                            ib_neigh_y_axis.append(y_distance)
                        
                        if not above_neighbor: 
                            z_distance = bin.height - (ib.position[2] + ib.get_dimension()[2])
                            ib_neigh_z_axis.append(z_distance)
                        
                        distance_3D = [min(ib_neigh_x_axis), min(ib_neigh_y_axis), min(ib_neigh_z_axis)]
                        pivot_dict[tuple(pivot)] = distance_3D
                
                n += 1
        
        return pivot_dict
    
    # def pivot_list(self, bin, item):   # 为什么不直接pivot_dict.keys?
    #     """Obtain all optional pivot points that one item could be placed into a certain bin.
    #     Args:
    #         bin: a bin in bin list that a certain item will be placed into.
    #         item: an unplaced item in item list.
    #     Returns:
    #         a pivot_list containing all optional pivot points that the item could be placed into a certain bin.
    #         这里似乎也会包含已经使用过的关键点，但是pivot_dict当中不会包含
    #     """
        
    #     pivot_list = []
        
    #     for axis in range(0, 3): 
    #         items_in_bin = bin.items 
            
    #         for ib in items_in_bin: 
    #             pivot = [0, 0, 0] 
    #             if axis == Axis.LENGTH: # axis = 0/ x-axis
    #                 pivot = [ib.position[0] + ib.get_dimension()[0],
    #                         ib.position[1],
    #                         ib.position[2]]
    #             elif axis == Axis.WIDTH: # axis = 1/ y-axis
    #                 pivot = [ib.position[0],
    #                         ib.position[1] + ib.get_dimension()[1],
    #                         ib.position[2]]
    #             elif axis == Axis.HEIGHT: # axis = 2/ z-axis
    #                 pivot = [ib.position[0],
    #                         ib.position[1],
    #                         ib.position[2] + ib.get_dimension()[2]]
        
    #             pivot_list.append(pivot)
            
    #     return pivot_list 
    
    def choose_pivot_point(self, bin, item):
        """Choose the optimal one from all optional pivot points of the item after comparison.
        Args:
            bin: a bin in bin list that a certain item will be placed into.
            item: an unplaced item in item list.
        Returns:
            the optimal pivot point that a item could be placed into a bin.
            这里并不是按照简单规则推箱子，而是真的在优化
        """
        
        can_put = False
        pivot_available = []
        pivot_available_temp = []
        # vertex_3d = []
        # vertex_2d = []
        # vertex_1d = []
        
        # n = 0
        # m = 0
        # p = 0
        
        # pivot_list = self.pivot_list(bin, item)   # 为什么不直接pivot_dict.keys?
        pivot_dict=self.pivot_dict(bin,item)
        pivot_list=list(pivot_dict.keys())
        
        for pivot in pivot_list:
            try_put_item = bin.can_hold_item_with_rotation(item, pivot)  # 要在这里面验证好哪种rotation可以
            
            if try_put_item:
                can_put = True
                pivot_available.append(pivot)  # 看一下这些关键点里有几个是能装这个货物的，如果能就放进pivot_available里
                pivot_temp = sorted(pivot,reverse=True)   # 从大到小排序，reverse之后选择关键点的策略是：让关键点的最大坐标最小
                pivot_available_temp.append(pivot_temp)
        
        if pivot_available:  # 如果有可行的关键点
            pivot_table=DataFrame(pivot_available_temp,columns=["max","mid","min"])
            pivot_table=pivot_table.sort_values(by=['max','mid',"min"],ascending=True)
            return pivot_available[pivot_table.index[0]],pivot_dict

        else:
            # print("here")
            return can_put,pivot_dict
            
            
        
    def pack_to_bin(self, bin, item): 
        """For each item and each bin, perform whole pack process with optimal orientation and pivot point.
        Args:
            bin: a bin in bin list that a certain item will be placed into.
            item: an unplaced item in item list.
        Returns: return value is void.
        """
        
        if not bin.items:  # 如果之前没有，就放在初始点
            response = bin.put_item(item, START_POSITION, [bin.length, bin.width, bin.height])
            # print("start")
            if not response:
                bin.unfitted_items.append(item)
            
            return response
        
        else:  # 如果之前有item了
            pivot_point,pivot_dict = self.choose_pivot_point(bin, item)           
            
            if not pivot_point:
                bin.unfitted_items.append(item)
                return False
                
            # print(pivot_dict)
            # print(pivot_point)
            # print(pivot_dict,pivot_point)
            distance_3D = pivot_dict[tuple(pivot_point)]
            response = bin.put_item(item, pivot_point, distance_3D)
            return response  # 如果是True就放进去了，是False就没放进去（但是经过我修改另一个bug之后，好像这个功能已经不太对了，不敢用）
            
    def pack(
        self, bigger_first=True, sort_volume=True ,number_of_decimals=DEFAULT_NUMBER_OF_DECIMALS):
        """For a list of items and a list of bins, perform the whole pack process.
        Args:
            bin: a bin in bin list that a certain item will be placed into.
            item: an unplaced item in item list.
        Returns:
            For each bin, print detailed information about placed and unplaced items.
            Then, print the optimal bin with highest packing rate.
        """
        
        for bin in self.bins:
            bin.format_numbers(number_of_decimals)
            
        for unplaced_item in self.unplaced_items:
            unplaced_item.format_numbers(number_of_decimals)
        

        # 对车厢进行排序
        self.bins.sort(
            key = lambda bin: bin.get_volume()) # default order of bins: from smallest to biggest
        
        # 托盘永远在器具前面进入
        # if sort_volume==True:
        #     unplaced_QJ=[i for i in self.unplaced_items if i.QJ]  # 如果是器具
        #     unplaced_tuopan=[i for i in self.unplaced_items if not i.QJ]
        #     unplaced_QJ.sort(
        #         key = lambda unplaced_item: unplaced_item.length*unplaced_item.width, reverse=bigger_first) # default order of items: from biggest to smallest
        #     self.unplaced_items=unplaced_tuopan+unplaced_QJ

        # # filling_ratio_list = []
        
        for bin in self.bins: 
            for unplaced_item in self.unplaced_items: 
                bin.unplaced_items.append(unplaced_item) 
        
        for bin in self.bins:
            bin.item_position={}
            for unplaced_item in self.unplaced_items:
                self.pack_to_bin(bin, unplaced_item)
                
            if len(self.bins)>1:
                for packed_item in bin.items:  # 对bin的放置信息进行记录
                    bin.item_position[packed_item]=[packed_item.position,packed_item.rotation_type]
            
        self.max_items_got=max([len(bin.items) for bin in self.bins])
        ok_bins=[bin for bin in self.bins if len(bin.items)==self.max_items_got]
        max_filling_ratio = max([bin.get_filling_ratio() for bin in ok_bins]) 
        
        for bin in ok_bins:
            if bin.get_filling_ratio() == max_filling_ratio:
                self.best_bin=bin
                for item in bin.items:
                    self.placed_items.append(item)
                # print("\nSelected bin with highest filling ratio: ", bin.string())
        if len(self.bins)>1 and self.best_bin!=self.bins[-1]:  # 如果有不止一个bin，则需要更新一遍信息
            for packed_item in self.best_bin.items:
                packed_item.position,packed_item.rotation_type=self.best_bin.item_position[packed_item]
                
                