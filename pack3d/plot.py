import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
# from mpl_toolkits.mplot3d import axes3d
from numpy import array,random
from pack3d.item import Item

def get_item_dict(solution_dicts):
    json_dict={}
    for date in solution_dicts:
        json_dict[date]={}
        for des in solution_dicts[date]:
            json_dict[date][des]=[]
            
            for packer in solution_dicts[date][des]:
                items_list=[]
                
                for item in packer.best_bin.items:
                    item_dict={}
                    if item.rotation_type==0:
                        item_dict["scale"]=[round(float(i),6) for i in item.scale]
                    else:
                        item_dict["scale"]=[round(float(i),6) for i in [item.scale[1],item.scale[0],item.scale[2]]]
                    item_dict["position"]=[round(float(i),6) for i in item.position]
                    item_dict["kind"]=item.kind
                    item_dict["weight"]=float(item.weight)
                    item_dict["item_ID"]=item.item_ID
                    item_dict["name"]=item.name
                    
                    items_list.append(item_dict)
                json_dict[date][des].append(items_list)
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