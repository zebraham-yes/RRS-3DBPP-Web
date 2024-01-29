# 在 Flask 应用中导入 secure_filename
from flask import Flask, render_template, request, session
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS
from flask_socketio import SocketIO
# from werkzeug.utils import secure_filename  # 修改这一行
import pack3d
import os

app = Flask(__name__)


# 修改这里，确保配置的上传目录和实际创建的目录一致
UPLOADED_DEFUALT_DEST="uploads"
app.config["UPLOADED_DEFUALT_DEST"] = UPLOADED_DEFUALT_DEST

# 配置文件上传目录和允许的文件类型为DATA（任何数据文件）
datafiles = UploadSet(name="xlsx",extensions=DOCUMENTS,default_dest=lambda x:UPLOADED_DEFUALT_DEST)

# 修改这里，确保使用的是正确的上传集
configure_uploads(app, (datafiles,))
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

@app.route("/", methods=["GET", "POST"])
def upload_excel():
    # global filename
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if file:
            # 保存文件到指定目录
            session['filename'] = datafiles.save(file)
            return render_template("index.html",msg=f"文件上传成功，保存为 {session['filename']}")
            # return render_template("index.html")
        
    return render_template("index.html",msg="")

def read_excel_file(file_path):
    # 通过 pandas 读取 Excel 文件
    try:
        excel_data = pack3d.get_excel(os.path.join(UPLOADED_DEFUALT_DEST,file_path))
        
        return excel_data  # 返回数据，可以根据需要处理
    except Exception as e:
        return f"文件读取失败：{str(e)}"

# 每页显示的行数
rows_per_page = 5

@app.route("/table_show",methods=["GET","POST"])
def table_show():
    # global filename
    # 读取 Excel 文件内容
    excel_data = read_excel_file(session['filename'])
    if type(excel_data)==str:
        return "文件读取失败，请重新上传，尽可能不要刷新页面或使用后退键"
    else:
        page = int(request.args.get('page', 1))
        
        # 计算开始和结束的索引
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page

        # 切片获取需要显示的数据
        table_html = excel_data.iloc[start_idx:end_idx].to_html(classes='table table-striped', index=False)
        return render_template("table_show.html",table=table_html, page=page, total_pages=(len(excel_data) // rows_per_page) + 1)

@app.route("/run3DBPP",methods=["GET","POST"])
def run3DBPP():
    # global filename
    pfep=read_excel_file(session['filename'])
    if type(pfep)==str:
        return "文件读取失败，请重新上传，尽可能不要刷新页面或使用后退键"
    else:
        AG=pack3d.Agent()
        bill_store=pfep.copy()
        dates=pack3d.unique(pfep["装车日期"])  # 表格中一共有几天
        solution_dicts=[]
        global_item_ID=0
        for date in dates:
            print("day:", date)
            des_solution_dict,bill_store=AG.excute(bill_store,date,global_item_ID,socket=socketio)
            solution_dicts.append(des_solution_dict)
            
            print('***************************************************************')
            
        return "运算完成"
    


@socketio.on('connect')
def handle_connect():
    print('Client connected')


if __name__ == "__main__":
    app.run(debug=True)
