from pandas import read_excel
from datetime import datetime

def get_excel(dir):
    pfep=read_excel(dir,sheet_name="PFEP")
    column_1=list(pfep.columns)
    column_2=pfep[0:1].values[0]
    for i in range(len(column_2)):
        temp_name=column_2[i]
        if type(temp_name)==str:
            column_1[i]=temp_name
    
    
    
    name_reset=["运输托","SNP"]
    for i in range(len(column_1)):
        if column_1[i]=="包装类型":
            column_1[i]=name_reset.pop()+"-包装类型"
            
    pfep.columns=column_1
    pfep=pfep.drop(0)
    for i in ["单托-长","单托-宽","单托-高"]:
        pfep[i]=pfep[i].astype(int)
    
    pfep["x"]=pfep["单托-长"]/1000
    pfep["y"]=pfep["单托-宽"]/1000
    pfep["z"]=pfep["单托-高"]/1000
    pfep["v"]=pfep["x"]*pfep["y"]*pfep["z"]
    pfep["num"]=pfep["单日需求托数"]
    pfep["w"]=pfep["单托重量\n（kg）"]/1000
    pfep["rou"]=pfep["w"]/pfep["v"]
    
    # 日期格式统一化
    dates_array=pfep["装车日期"].values
    dates_list=[]
    for date in dates_array:
        if type(date)==datetime:
            dates_list.append(date.strftime("%Y/%m/%d"))
        elif type(date)==str:
            dates_list.append(date)
        else:
            raise ValueError
    pfep["装车日期"]=dates_list
    
    return pfep