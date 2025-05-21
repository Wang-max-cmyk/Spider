from sanic import Sanic
from sanic.response import json, text
import os
import logging
import time
import json as json_lib
from sanic.response import file as sanic_file
import jieba
import zipfile
import matplotlib.pyplot as plt
from wordcloud import WordCloud

app = Sanic("mySanic")

# 日志设置
logger = logging.getLogger('sanic.app')
logger.setLevel(logging.DEBUG)

# 确保目录存在
UPLOAD_DIR = "./upload"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 上传图书数据文件接口
@app.route("/v1/book/crawled/upload", methods=['POST'])
async def upload(request):
    allow_type = ['.json']
    file = request.files.get('file')

    if not file:
        return json({"code": 0, "msg": "No file uploaded"})

    file_type = os.path.splitext(file.name)
    if len(file_type) == 1 or file_type[1] not in allow_type:
        return json({"code": 0, "msg": "File format error!"})

    now_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
    filename = f"{now_time}_{file_type[0]}.json"
    save_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(save_path, 'wb') as f:
            f.write(file.body)
        return json({"code": 1, "msg": "Upload successful!", "data": {"name": filename}})
    except Exception as e:
        return json({"code": 0, "msg": f"Error saving file: {str(e)}"})

# 获取图书信息
@app.route("/v1/book/info", methods=['GET'])
async def get_books_info(request):
    filename = request.args.get("filename")
    book_id = request.args.get("book_id")

    if not filename:
        return json({"code": 0, "msg": "Filename is required", "data": None})

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return json({"code": 0, "msg": "File not found", "data": None, "filename": filename})

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            books = json_lib.load(file)

        if not isinstance(books, list):
            books = [books]

        if book_id:
            filtered_books = [book for book in books if str(book.get("book_id", "")) == str(book_id)]
            data = filtered_books
            msg = f"Found {len(filtered_books)} book(s)"
        else:
            data = books
            msg = "All books returned"

        return json({"code": 1, "msg": msg, "data": data})

    except json_lib.JSONDecodeError:
        return json({"code": 0, "msg": "Invalid JSON format", "data": None})
    except Exception as e:
        return json({"code": 0, "msg": f"Error reading file: {str(e)}", "data": None})

# 获取书评信息（支持按文件名和图书ID过滤）
@app.route("/v1/book/comment", methods=['GET'])
async def get_book_comments(request):
    filename = request.args.get("filename")
    book_id = request.args.get("book_id")

    if not filename:
        return json({"code": 0, "msg": "Filename is required", "data": None})

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return json({"code": 0, "msg": "File not found", "data": None})

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            raw_comments = json_lib.load(file)
    except Exception as e:
        return json({"code": 0, "msg": f"Failed to parse file: {str(e)}", "data": None})

    # 聚合为 book_id => comment_list 的结构
    book_comments = {}
    for comment in raw_comments:
        bid = comment.get("book_id")
        if not bid:
            continue
        book_comments.setdefault(bid, []).append(comment)

    if book_id:
        data = {
            "book_id": book_id,
            "comment_list": book_comments.get(book_id, [])
        }
    else:
        data = [{"book_id": bid, "comment_list": comments} for bid, comments in book_comments.items()]

    return text(
        json_lib.dumps({
            "code": 1,
            "msg": "Query successful!",
            "data": data
        }, ensure_ascii=False, indent=2),
        content_type="application/json"
    )



@app.route("/v1/book/comment/visualize", methods=["GET"])
async def visualize_comments(request):
    comment_file = request.args.get("comment_file")
    emotion_file = request.args.get("emotion_file")

    if not comment_file or not emotion_file:
        return json({"code": 0, "msg": "comment_file and emotion_file are required", "data": None})

    comment_path = os.path.join("upload", comment_file)
    emotion_path = os.path.join("upload", emotion_file)

    if not os.path.exists(comment_path) or not os.path.exists(emotion_path):
        return json({"code": 0, "msg": "One or both files not found", "data": None})

    try:
        with open(comment_path, "r", encoding="utf-8") as f1, open(emotion_path, "r", encoding="utf-8") as f2:
            comment_data = json_lib.load(f1)
            emotion_data = json_lib.load(f2)
    except Exception as e:
        return json({"code": 0, "msg": f"Failed to load JSON files: {e}", "data": None})

    if not isinstance(comment_data, list) or not isinstance(emotion_data, list):
        return json({"code": 0, "msg": "Expected both files to contain list of items", "data": None})

    # 构建 comment_id 到情绪的映射
    emotion_dict = {e["comment_id"]: e for e in emotion_data if "comment_id" in e and "is_positive" in e}
    
    merged = []
    for c in comment_data:
        cid = c.get("comment_id")
        emotion = emotion_dict.get(cid)
        if cid and "comment_content" in c and emotion:
            merged.append({
                "comment_content": c["comment_content"],
                "is_positive": emotion["is_positive"]
            })

    if not merged:
        return json({"code": 0, "msg": "No matched comments with emotion data", "data": None})

    # 数据统计
    total_comments = len(merged)
    positive_comments = sum(1 for c in merged if c["is_positive"] == 1)
    negative_comments = total_comments - positive_comments

    # 输出图像目录
    output_dir = "output_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"] = 14

    def plot_histogram():
        plt.figure(figsize=(8, 6))
        categories = ['全部评论', '正向评论', '负向评论']
        counts = [total_comments, positive_comments, negative_comments]
        plt.bar(categories, counts, color=['blue', 'green', 'red'])
        plt.ylabel('数量')
        plt.title('评论情感分析统计图')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "emotion_bar_chart.png"))
        plt.close()

    def plot_wordcloud():
        comment_text = " ".join(c["comment_content"] for c in merged if c["comment_content"].strip())
        cut_text = " ".join(jieba.lcut(comment_text))
        stopword_path = "userless.txt"
        with open(stopword_path, 'r', encoding='utf-8') as f:
            stopwords = set(f.read().split())
        stopwords.update(['\n', '', ' '])
        wordcloud = WordCloud(width=800, height=400, font_path='/Library/Fonts/Hiragino Sans GB.ttc',
                              background_color='white', max_words=200,
                              stopwords=stopwords, random_state=42).generate(cut_text)
        plt.figure(figsize=(12, 6))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title('评论词云图')
        plt.savefig(os.path.join(output_dir, "comment_wordcloud.png"))
        plt.close()

    def create_zip(zip_path):
        with zipfile.ZipFile(zip_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            for fname in os.listdir(output_dir):
                fpath = os.path.join(output_dir, fname)
                if os.path.isfile(fpath):
                    zf.write(fpath, arcname=fname)

    try:
        plot_histogram()
        plot_wordcloud()
        zip_path = "comment_visuals.zip"
        create_zip(zip_path)
        return await sanic_file(zip_path, filename="comment_visuals.zip")
    except Exception as e:
        return json({"code": 0, "msg": f"Visualization failed: {e}", "data": None})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
