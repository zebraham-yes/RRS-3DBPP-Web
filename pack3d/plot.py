import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
# from mpl_toolkits.mplot3d import axes3d
from numpy import array,random
from pack3d.item import Item,Block


def float_round_6(x):
    return round(float(x),6)

def get_item_dict(solution_dicts):
    json_dict={}
    for date in solution_dicts:
        json_dict[date]={}
        for des in solution_dicts[date]:
            json_dict[date][des]=[]
            
            for packer in solution_dicts[date][des]:
                truck_dict={}  # 新增车辆信息字典
                items_list=[]  # 原来每辆车是一个列表，现在是一个字典
                
                for item in packer.best_bin.items:
                    
                    # 未来在这里应该区分item和block，并对block进行拆分，在录入信息的时候直接录入item的信息
                    if type(item)==Item:
                        item_dict={}   # 是一个货物的信息
                        if item.rotation_type==0:
                            item_dict["scale"]=[float_round_6(i) for i in item.scale]
                        else:
                            item_dict["scale"]=[float_round_6(i) for i in [float_round_6(item.scale[1]),float_round_6(item.scale[0]),float_round_6(item.scale[2])]]
                        item_dict["position"]=[float_round_6(i) for i in item.position]
                        item_dict["kind"]=item.kind
                        item_dict["weight"]=float_round_6(item.weight)
                        item_dict["item_ID"]=item.item_ID
                        item_dict["name"]=item.name
                        item_dict["color"]="rgb("+str(item.color[0])+","+str(item.color[1])+","+str(item.color[2])+")"
                        items_list.append(item_dict)
                        
                    elif type(item)==Block:
                        if item.rotation_type==0:
                            z_position=0
                            for parent_item in item.parent_items:
                                item_dict={}
                                item_dict["scale"]=[float_round_6(i) for i in [parent_item.length,parent_item.width,parent_item.height]]
                                item_dict["position"]=[float_round_6(item.position[0]),float_round_6(item.position[1]),z_position]
                                item_dict["kind"]=parent_item.kind
                                item_dict["weight"]=float_round_6(parent_item.weight)
                                item_dict["item_ID"]=parent_item.item_ID
                                item_dict["name"]=parent_item.name
                                item_dict["color"]="rgb("+str(parent_item.color[0])+","+str(parent_item.color[1])+","+str(parent_item.color[2])+")"
                                items_list.append(item_dict)
                                z_position+=float_round_6(parent_item.height)
                        else:  # 旋转了90°
                            z_position=0
                            for parent_item in item.parent_items:
                                item_dict={}
                                item_dict["scale"]=[float_round_6(i) for i in [parent_item.width,parent_item.length,parent_item.height]]
                                item_dict["position"]=[float_round_6(item.position[0]),float_round_6(item.position[1]),z_position]
                                item_dict["kind"]=parent_item.kind
                                item_dict["weight"]=float_round_6(parent_item.weight)
                                item_dict["item_ID"]=parent_item.item_ID
                                item_dict["name"]=parent_item.name
                                item_dict["color"]="rgb("+str(parent_item.color[0])+","+str(parent_item.color[1])+","+str(parent_item.color[2])+")"
                                items_list.append(item_dict)
                                z_position+=float_round_6(parent_item.height)
                    else:
                        print("error")
                    
                    truck_dict["items_list"]=items_list
                    truck_dict["truck_scale"]=[float_round_6(i) for i in packer.best_bin.scale]
                    truck_dict["v_ratio"]=round(float(packer.best_bin.get_filling_ratio()),5)
                    truck_dict["w_ratio"]=round(float(packer.best_bin.get_weight_ratio()),5)
                    
                json_dict[date][des].append(truck_dict)
    return json_dict




def plot_box(ax,ori_point,vector,linewidths=1,edgecolors='black',facecolors=random.rand(3),alpha=0.5):
    a,b,c=ori_point
    x,y,z=vector

    verts=[
        [[a,b,c],[a,y,c],[a,y,z],[a,b,z]],  # behind
        [[x,b,c],[x,y,c],[x,y,z],[x,b,z]],  # forward
        [[a,b,c],[a,b,z],[x,b,z],[x,b,c]],  # left
        [[a,y,c],[a,y,z],[x,y,z],[x,y,c]],  # right
        [[a,b,c],[a,y,c],[x,y,c],[x,b,c]],  # bottom
        [[a,b,z],[a,y,z],[x,y,z],[x,b,z]]   # up
    ]
    # 绘制长方体
    ax.add_collection(Poly3DCollection(verts, 
                                        facecolors=facecolors, 
                                        edgecolors=edgecolors, 
                                        linewidths=linewidths, 
                                        alpha=alpha))
    return ax

# 装箱效果可视化
def plot_truck(bin,show=True,save=False,save_dir=""):
    ax = plt.axes(projection='3d')
    truck_scale=bin.scale
    plot_info=[]
    plot_box(ax,[0,0,0],truck_scale,alpha=0,linewidths=2)

    for item in bin.items:
        if type(item)==Item:   # 如果不是block
            position=array([float(i) for i in item.position])
            x,y,z=[float(i) for i in item.scale]
            plot_info.append([position,[x,y,z],item.weight])  # 查看位置信息

            if item.rotation_type==1:
                
                plot_box(ax,position,position+array([y,x,z]),facecolors=random.rand(3))
            else:
                plot_box(ax,position,position+array([x,y,z]),facecolors=random.rand(3))
        else:   # 如果是block
            position=array([float(i) for i in item.position])
            x,y,z=[float(i) for i in item.scale]
            num_parents=len(item.parent_items)
            # print("ploting a block")
            for i in range(num_parents):
                if item.rotation_type==1:
                    plot_box(ax,position,position+array([y,x,z/num_parents]),facecolors=random.rand(3))
                    position[2]+=(z/num_parents)
                else:
                    plot_box(ax,position,position+array([x,y,z/num_parents]),facecolors=random.rand(3))
                    position[2]+=(z/num_parents)
        
    ax.set_xlim([0, 20])
    ax.set_ylim([0, 20])
    ax.set_zlim([0, 20])
    
    if show:
        plt.show()
    if save:
        plt.savefig(save_dir,dpi=200)

    return ax,plot_info