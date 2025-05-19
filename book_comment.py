from sanic import Sanic
from sanic.response import text,json
import os
import logging
import time

app = Sanic("mySanic")

logger = logging.getLogger('sanic.app')
logger.setLevel(logging.DEBUG)

# 上传书评数据文件接口
@app.route("/v1/book/crawled/upload", methods=['POST'])
async def upload(request):
# 处理相关逻辑
    allow_type = ['.json'] #允许上传的类型
    file = request.files.get('file') #解析前端传来的文件
    type = os.path.splitext(file.name) #分割文件名
    if len(type) == 1 or type[1] not in allow_type:
        return json({"code":0,"message":"file's format is error!"})

    path = "./upload" #存储的文件夹
    if not os.path.exists(path):
        os.makedirs(path)

    
    now_time = time.strftime('%Y%m%d%H%M%S',time.localtime()) #获取当前时间
    #创建时间戳子目录（如：upload/20250519081929/）
    timestamp_dir=os.path.join(path,now_time)
    if not os.path.exists(timestamp_dir):
        os.makedirs(timestamp_dir)
    filename = now_time+"/"+type[0]+".json"
    with open(path + "/" + filename, 'wb' )as f:
        f.write(file.body)
    f.close()
    return json({"code":1,"msg":"upload successfully!", "data":{"name":filename}})
    #正常上传流程？？？
# convert_book(filename)
  

# 获取图书信息
@app.route("/v1/book/info", methods=['GET'])
async def get_books_info(request):
    import json as json_lib #避免命名冲突
   
    #从请求参数中获取文件名
    filename = request.args.get("filename")
    if not filename:
        return json({"code":0,"msg":"Filename is required","data":None})
    #检查文件是否存在
    file_path = os.path.json("upload",filename)
    if not os.path.exists(file_path):
        return json({"code":0,"msg":"File not Found","data":None})
    try:
        #读取并解析json文件
	with open(file_path,"r") as file:
	    book_data = json_lib.load(file)

        if not isinstance(book_data,list):
            book_data = [book_data]

        return json({
            "code":1,
 	    "msg":"query successfully!",
  	    "data":book_data    
        })

    except Exception as e:
        return json({
            "code":0,
            "msg":f"Error reading file: {str(e)}",
            "data":None
        })
    

# 获取书评信息
@app.route("/v1/book/comment", methods=['GET'])
async def get_book_comments(request):
# 处理相关逻辑
    return json({"code": 1, "msg": "query successfully!", "data": None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

