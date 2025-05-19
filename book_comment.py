from sanic import Sanic
from sanic.response import text,json
import os
import logging
import time
import json as json_lib

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
    book_id = request.args.get("book_id")

    # 参数校验（filename必填）
    if not filename:
        return json({"code": 0, "msg": "Filename is required", "data": None})

    # 检查文件是否存在
    file_path = os.path.join("upload", filename)
    if not os.path.exists(file_path):
        return json({"code": 0, "msg": "File not found", "data": None})

    try:
        # 读取并解析JSON文件
        with open(file_path, "r", encoding="UTF-8") as file:
            raw_comments = json_lib.load(file)
        
        # 按book_id分组评论
        books = {}
        for comment in raw_comments:
            current_book_id = comment.get("book_id")
            if current_book_id not in books:
                books[current_book_id] = {
                    "book_id": current_book_id,
                    "comment_list": []
                }
            # 提取示例中的字段（严格对齐）
            formatted_comment = {
                "comment_id": comment.get("comment_id"),
                "comment_username": comment.get("comment_username"),
                "comment_timestamp": comment.get("comment_timestamp"),
                "comment_location": comment.get("comment_location"),
                "comment_rating": comment.get("comment_rating"),
                "comment_content": comment.get("comment_content"),
                "comment_isuseful": comment.get("comment_isuseful")
            }
            books[current_book_id]["comment_list"].append(formatted_comment)

        # 转换为列表格式
        book_list = list(books.values())

        # 按book_id过滤（如果提供）
        if book_id:
            filtered_books = [
                book for book in book_list 
                if str(book["book_id"]) == str(book_id)
            ]
            response_data = filtered_books
        else:
            response_data = book_list

        # 直接返回列表（不嵌套在 "data" 字段中）
        return json(response_data)

    except json_lib.JSONDecodeError:
        return json({"code": 0, "msg": "Invalid JSON format", "data": None})
    except Exception as e:
        return json({"code": 0, "msg": f"Error: {str(e)}", "data": None})
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

