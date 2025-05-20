from sanic import Sanic
from sanic.response import text,json
import os
import logging
import time
import json as json_lib
from flask import Response

app = Sanic("mySanic")

logger = logging.getLogger('sanic.app')
logger.setLevel(logging.DEBUG)

# 上传图书数据文件接口
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
    filename = now_time+"_"+type[0]+".json"
    with open(path + "/" + filename, 'wb' )as f:
        f.write(file.body)
    f.close()
    return json({"code":1,"msg":"upload successfully!", "data":{"name":filename}})
    

# 获取图书信息
@app.route("/v1/book/info", methods=['GET'])
async def get_books_info(request):  
    #获取请求参数
    filename = request.args.get("filename")
    book_id = request.args.get("book_id")
    if not filename:
        return json({"code":0,"msg":"Filename is required","data":None})
    #检查文件是否存在
    file_path = os.path.join("upload",filename)
    if not os.path.exists(file_path):
        return json({"code":0,"msg":"File not Found","data":None,"filename":filename})
    try: #读取并解析json文件
        with open(file_path,"r",encoding="UTF-8") as file:
            books = json_lib.load(file)

        if not isinstance(books,list):
            books = [books]
        #按book_id过滤（如果提供了）
        if book_id:
            filtered_books = [
                book for book in books
                if str(book.get("book_id",""))==str(book_id)
            ]
            data = filtered_books
            msg = "Found{} book(s)".format(len(filtered_books))
        else:
            data = books
            msg = "All books returned"

        #统一返回列表模式(即使空列表)
        return json({
            "code":1,
            "msg":msg,
            "data":data    
        })
    except json_lib.JSONDecodeError:
        return json({"code":0,"msg":"Invalid JSON format","data":None})
    except Exception as e:
        return json({
            "code":0,
            "msg":f"Error reading file: {str(e)}",
            "data":None
        })
    

# 获取书评信息（支持按文件名和图书ID过滤）
# 获取书评信息（严格对齐示例格式）
@app.route("/v1/book/comment", methods=['GET'])
async def get_book_comments(request):
    # 获取请求参数
    filename = request.args.get("filename")
    book_id = request.args.get("book_id",None)

    # 参数校验（filename必填）
    if not filename:
        return json({"code": 0, "msg": "Filename is required", "data": None})

    # 检查文件是否存在
    file_path = os.path.join("upload", filename)
    if not os.path.exists(file_path):
        return json({"code": 0, "msg": "File not found", "data": None})

    try:
        # 读取并解析JSON文件
        with open(file_path, "r", encoding="utf-8") as file:
            raw_comments = json_lib.load(file)
    except Exception as e:
        return json({
            "code": 0,
            "msg": f"Failed to parse file: {str(e)}",
            "data": None
        })

    # 聚合为 book_id => comment_list 的结构
    book_comments = {}
    for comment in raw_comments:
        bid = comment.get("book_id")
        if not bid:
            continue
        book_comments.setdefault(bid, []).append(comment)

    # 如果指定了 book_id，返回对应的评论
    if book_id:
        data = {
            "book_id": book_id,
            "comment_list": book_comments.get(book_id, [])
        }
    else:
        # 否则返回所有评论信息，每本书一个 entry
        data = []
        for bid, comments in book_comments.items():
            data.append({
                "book_id": bid,
                "comment_list": comments
            })

    return Response( 
        json_lib.dumps({
            "code": 1,
            "msg": "query successfully!",
            "data": data
        },ensure_ascii=False,indent=2),
        mimetype='application/json'
    )
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

