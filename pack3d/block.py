from numpy import prod
from pack3d.item import set_to_decimal,Block

def get_Shelf_info(must_items):
    shelves=[]
    shelf_ID=[]
    for item in must_items:
        if item.kind=="shelf":
            shelves.append(item)  # 所有的货架item
            shelf_ID.append(item.item_ID)  # 所有货架item的ID
    shelf_ID=list(set(shelf_ID))
    n=len(shelf_ID)  # 一共有多少种货架

    shelf_num=[]
    shelf_vol=[]
    shelf_weight=[]
    shelf_item=[]
    shelf_scale=[]
    
    for i in range(n):
        items=[]
        for shelf in shelves:
            if shelf_ID[i]==shelf.item_ID:
                    items.append(shelf)
        shelf_item.append(items)
        shelf_num.append(len(items))
        shelf_weight.append(float(items[0].weight))
        shelf_vol.append(float(prod(items[0].scale)))
        shelf_scale.append(items[0].scale)

    shelf_info=dict()
    shelf_info['ID']=shelf_ID
    shelf_info['num']=shelf_num
    shelf_info['weight']=shelf_weight
    shelf_info['vol']=shelf_vol
    shelf_info['item']=shelf_item
    shelf_info["scale"]=shelf_scale
    
    return shelf_info

def group_items_by_height(items, target_sum, threshold):
    result = []
    previous_groups = []
    
    if not items:
        return result

    if threshold == "auto":
        threshold = target_sum - min(item.height for item in items)

    for item in items:
        # 尝试将当前item放入之前未满足2.5的组中
        added_to_previous_group = False
        for i in range(len(previous_groups)):
            test_sum = sum(item.height for item in previous_groups[i]) + item.height
            if test_sum <= target_sum:
                previous_groups[i].append(item)
                if test_sum > threshold:  # 一旦已经超过thresh了，就放进结果中，不再检查了
                    result.append(previous_groups.pop(i))
                added_to_previous_group = True
                break

        # 如果当前item没有被放入之前的组，则检查是否需要开始新的组
        if not added_to_previous_group:
            # 如果当前组的和加上当前item的height超过目标值，则将当前组加入结果列表，并初始化一个新的组
            previous_groups.append([item])

    previous_groups = [group for group in previous_groups if group]
    result.extend(previous_groups)
    return result

# # 示例使用
# class Item:
#     def __init__(self, height):
#         self.height = height

# original_items = [Item(1.1), Item(3), Item(2.0), Item(0.8), Item(1.4), Item(0.5), Item(0.7), Item(1.0), Item(0.4), Item(1.2)]
# target_sum = 3.3
# threshold = "auto"

# result_groups = group_items_by_height(original_items, target_sum, threshold)

# print("原始列表:", [item.height for item in original_items])
# print("分组结果:", [[item.height for item in group] for group in result_groups])


def blocker_items(must_items,H,global_item_ID):
    # global global_item_ID
    blocks=[]
    shelf_info=get_Shelf_info(must_items)
    
    error_log=[]
    
    # 1
    standard_boxes=[item for item in must_items if item.kind!="shelf" and (item.length==1.2) and (item.width==1)]  # 所有的托盘和可以被视为托盘的围板箱
    # box_num=len(standard_boxes)
    best_num=int((set_to_decimal(H,number_of_decimals=3)-set_to_decimal(0.2,3))//set_to_decimal(1.1,number_of_decimals=3))  # 能放下几层托盘
    grouped_boxes=group_items_by_height(items=standard_boxes, target_sum=H, threshold="auto")
    
    for group in grouped_boxes:
        blocks.append(Block(name="B"+str(global_item_ID),item_ID=global_item_ID,parent_items=group,kind="collar"))

    # 2
    unstandard_boxes=[item for item in must_items if item.kind=="collar" and item not in must_items]  # 所有不可以被视为托盘的围板箱
    while unstandard_boxes:  # 对这里面每一种长宽高的围板箱进行循环
        sample_box=unstandard_boxes[0]
        temp_boxes=[box for box in unstandard_boxes if (box.length==sample_box.length and box.width==sample_box.width) or (box.length==sample_box.width and box.width==sample_box.length)]
        for box in temp_boxes:
            unstandard_boxes.remove(box)
        
        grouped_unstandard_temp_box=group_items_by_height(items=temp_boxes, target_sum=H, threshold="auto")
        
        for group in grouped_unstandard_temp_box:
            blocks.append(Block(name="B"+str(global_item_ID),item_ID=global_item_ID,parent_items=group,kind="collar"))
    # 3
    # shelves_boxes=[box for box in must_items if box.kind=="shelf"]
    # kinds_of_shelves=np.unique([shelf.])
    for i in range(len(shelf_info['ID'])):  # 对于每一种货架
        best_num=int((set_to_decimal(H,number_of_decimals=3)-set_to_decimal(0.2,3))//set_to_decimal(shelf_info['scale'][i][2],number_of_decimals=3))  # 应该堆几层
        # shelves=[item for item in must_items if item.item_ID==shelf_info["ID"][i]]  # 所有这类器具
        shelves=shelf_info["item"][i]
        shelf_num=len(shelves)
        
        index=0
        while shelf_num>0:
            block_num=min(best_num,shelf_num)  # 本次堆几层
            i_next=int(index+block_num)
            group=shelves[index:i_next]
            height=sum([item.height for item in group])

            if height>3.5:
                print("错误的货架block：shelf_num",shelf_num,"best_num",best_num,shelf_info["scale"][i],shelf_info["ID"][i],shelf_info["weight"][i])
                # error_log.append([shelves,shelf_num])
                
            blocks.append(Block(name="B"+str(global_item_ID),item_ID=global_item_ID,parent_items=group,kind="shelf"))
            global_item_ID+=1
            shelf_num-=block_num
            index=i_next
    
    if error_log:
        print(error_log)
        
    return blocks
