from .packer import Packer
from .bin import Bin
from .item import Item
from .plot import plot_box,plot_truck,get_item_dict
from .block import blocker_items
from .excel import get_excel
from numpy import min,unique
from numpy.random import randint
from pandas import read_excel
from threading import Thread


# global_item_ID=0
trucks=read_excel("trucks.xlsx")
easy_trucks=trucks.loc[trucks["类型"].apply(lambda x: "实际" not in x)]

class Agent_Thread(Thread):
    def __init__(self,agent,orders,global_item_ID,socket,stop_event):
        super(Agent_Thread, self).__init__()
        self.stop_event = stop_event
        self.agent=agent
        self.orders=orders
        self.global_item_ID=global_item_ID
        self.socket=socket
        self.date_solution_dict={}

    def run(self):
        dates=unique(self.orders["装车日期"])
        for date in dates:
            if self.stop_event.is_set():  # 设定终止情形
                break
            self.date_solution_dict[date]={}
            print("day:", date)
            date_orders=self.orders.loc[self.orders["装车日期"]==date]
            ori_warehouse=unique(date_orders["始发仓库"])  # 当日有几个仓库要发货
            num_of_ori=str(len(ori_warehouse))  # 一共有几个要发往的地点
            # ori_solution_dict={}
            ori_count=0
            
            for ori in ori_warehouse:
                if self.stop_event.is_set():  # 设定终止情形
                    break
            
                ori_count+=1
                print("————————来自 %s 的货物 开始————————\n"%ori)            
                des_orders=date_orders.loc[date_orders["始发仓库"]==ori]   # 提取发往一个地区的订单信息
                must_item_table=des_orders.sample(frac=1)  # 对订单进行打乱
                # get_must(bills.loc[bills["始发仓库"]==ori],date).sample(frac=1)
                if len(must_item_table)==0:  # 没有要发的货
                    continue
                ori_packers=self.agent.excute(must_item_table=must_item_table,global_item_ID=self.global_item_ID,socket=self.socket,date=date,ori=ori,ori_count=ori_count,num_of_ori=num_of_ori,stop_event=self.stop_event)
                self.date_solution_dict[date][ori]=ori_packers
                print("————————%s 结束————————\n"%ori)
                
            # self.date_solution_dict[date]=ori_solution_dict
            print("————————****************%s 结束****************————————\n"%date)
                

    def stop(self):
        # 设置停止标志，线程会在下一个循环迭代中退出
        self._stop_event = True

class Agent:  # 定义智能体
    def __init__(self) -> None:
        self.first_batch_size=70
        self.second_batch_size=5
        self.ori_packers=[]   # 临时
        self.satisfying_v_ratio=0.75
        self.satisfying_w_ratio=0.90  # 这两个只要有一个达到了，就停止迭代装箱
        self.unplacable_v=100000  # 初始值设为极大，如果剩余的剩余的货物中没有比这个还小的，也停止迭代装箱
        self.search_batch=5
        self.unplacable_items=[]
    
    def get_item_list(self,item_table):  # 之后这个函数当中要集成blocking的功能，让进入must_item的东西已经尽可能地成为适合装入17.5m车的block，
        # 同时，block最好又具有解散的功能，这样一旦装不进去了，又可以变回零散的item（或许可以通过构建一个继承自item的类来实现）
        must_items=[]
        for i,item in item_table.iterrows():
            if item["运输托-包装类型"]=="托盘":
                color_array=[255,randint(180),randint(180)]
                for n in range(int(item["num"])):
                    must_items.append(Item(item["零件名称"], item["x"], item["y"], item["z"], item["w"],kind="pallet",item_ID=item["序号"],color=color_array))   # 同样类型的还是在一起
            elif item["运输托-包装类型"]=="围板箱":
                color_array=[randint(180),255,randint(180)]
                for n in range(int(item["num"])):
                    must_items.append(Item(item["零件名称"], item["x"], item["y"], item["z"], item["w"],kind="collar",item_ID=item["序号"],color=color_array))
            else:
                color_array=[randint(180),randint(180),255]
                for n in range(int(item["num"])):
                    must_items.append(Item(item["零件名称"], item["x"], item["y"], item["z"], item["w"],kind="shelf",item_ID=item["序号"],color=color_array))

            # global_item_ID+=1
        return must_items
    
    # def separate_items(item_list): # 转化为一个优化问题，通过构建一个损失函数来让分车尽可能地均匀高效地分车（可能没有用，因为分车根本不需要）
    #     item_sep_list=[]

    #     return item_sep_list

    # 在更新后的版本当中，这个函数仅对某一日、某一城市发出的货物执行装车
    def excute(self,must_item_table,global_item_ID,socket,date,ori,ori_count,num_of_ori,stop_event):      
        must_items=self.get_item_list(must_item_table)  # 将pandas表格中的货物信息转化为装有很多item的列表
        must_items=blocker_items(must_items,3.5,global_item_ID)
        total_length=len(must_items)
        print("货物总数：",total_length)

        self.ori_packers=[]
        
        # ——————正式装箱开始——————
        while len(must_items)>0:
            # 开始进行初次装车
            batch,must_items=must_items[:self.first_batch_size],must_items[self.first_batch_size:]  # 从must_item中取出一个batch
            # qj_info=get_QJinfo(must_items)
            # batch,must_items,qj_info=Batch_Generator(must_items,min(self.first_batch_size,len(must_items)),qj_info)
            if stop_event.is_set():  # 用于协助终止
                break
            
            batch_packer = Packer()
            batch_packer.add_bin(Bin("17.5m默认", 17.5,3,3.5,33))
            for item in batch:
                batch_packer.add_item(item)

            batch_packer.pack()
            bin=batch_packer.bins[0]
            print("初次装箱：放入",len(bin.items),"，未放入",len(bin.unfitted_items),end=" ")  # 只有这俩变量是靠谱的：装进去的，没装进去的
            if len(bin.items)==0:  # 如果一个货物都没装进去，说明这个货物太大或者太重了，放入unplacable_items中记录一下
                for item in bin.unfitted_items:
                    print("不可能放入的item：",item.scale,item.weight,item.item_ID)
                    self.unplacable_items.append(item)
                break

            if bin.unfitted_items:   # 如果没装进去把剩下的送回去
                self.unplacable_v=min([item.v for item in bin.unfitted_items])  # 获取最小不可放置物体的体积
                must_items+=bin.unfitted_items
                batch_packer.unplaced_items=[]  # 送回去之后把剩余空间清空，unplaced_items会在下一次装箱的时候被装进去，所以必须清空
                # 这段代码实现了对初次装箱过程中packer内item的转移，能装进去的转移到bin里面，装不进去的送回must_items当中
                

            # 开始进行迭代装车
            temp_must_items=must_items[:]  # 拷贝一份不会更改的must_item
            length_of_must_items=len(temp_must_items)
            # 如果需要进行迭代装车：
            i=0
            
            while (bin.get_filling_ratio()<self.satisfying_v_ratio) and (bin.get_weight_ratio()<self.satisfying_w_ratio) and i<length_of_must_items and i<=(self.first_batch_size*10):
                
                small_item=temp_must_items[i]
                # if (self.unplacable_v*pack3d.item.set_to_decimal(1.125,number_of_decimals=3))>small_item.v:
                if self.unplacable_v>=small_item.v:
                    # 找到一个更小的货物
                    packed_items_len=len(bin.items)
                    small_item.format_numbers(number_of_decimals=3)
                        # response=batch_packer.pack_to_bin(batch_packer.bins[0], temp_item)  # response 似乎不太准
                    batch_packer.pack_to_bin(bin, small_item)
                    if packed_items_len!=len(bin.items):
                        must_items.remove(small_item)
                            # print("small item fitted")
                    else:
                        self.unplacable_v=small_item.v

                i+=1
            
            V_ratio=round(batch_packer.bins[0].get_filling_ratio(),4)
            W_ratio=round(batch_packer.bins[0].get_weight_ratio(),4)
            msg=f"迭代装箱后,   V_ratio: {V_ratio},  W_ratio: {W_ratio}"
            print(msg,end=" ")
            socket.emit('update', {'task_date':date,'ori_percent':str(ori_count)+"/"+num_of_ori,'ori':ori,'progress': str(round((1-len(must_items)/total_length)*100,1))+"%", 'message': msg})  # 向socket专属进度情况
            print("装入货物总数：",len(batch_packer.bins[0].items),"剩余货物总数：",len(must_items),end="\n")
            self.ori_packers.append(batch_packer)
        
        # ——————正式装箱结束——————
        # 把最后一个车/利用率不高的车里面的箱子改用别的装

        last_packer=self.ori_packers.pop()  # 把最后一个拿出来重新装
        self.smaller_packer=Packer()
        for i,truck in easy_trucks.iterrows():
            self.smaller_packer.add_bin(Bin(truck["车型"], truck["规格-长\n（米）"], truck["规格-宽\n（米）"],truck["规格-高\n（米）"],truck["载重（吨）"]))
        
        num_of_items=0
        for item in last_packer.bins[0].items:
            # item.position=0
            # if type(item)==pack3d.item.Block:  # 如果是block的话要拆解回收
            for parent in item.disassembly():
                self.smaller_packer.add_item(parent)
                num_of_items+=1  # 记录一下一共拆分为多少个
            # else:
            #     self.smaller_packer.add_item(item)
            #     num_of_items+=1
        self.smaller_packer.pack()
        
        bin=self.smaller_packer.best_bin
        print("最终装箱：放入",len(bin.items),"，未放入",len(bin.unfitted_items),end=" ")  # 只有这俩变量是靠谱的：装进去的，没装进去的
        print("最终装箱后   V_ratio: ",round(bin.get_filling_ratio(),4)," W_ratio: ",round(bin.get_weight_ratio(),4))
        # print("装入货物总数：",len(bin.items),"剩余货物总数：",len(bin.unfitted_items),end="\n")
        
        # print(self.smaller_packer.max_items_got, num_of_items)
        if self.smaller_packer.max_items_got == num_of_items:  # 如果全装进去了
            self.ori_packers.append(self.smaller_packer)
            # print("using smaller packer")
        else:
            self.ori_packers.append(last_packer)
            # print("using last packer")
        return self.ori_packers