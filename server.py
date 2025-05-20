from sanic import Sanic, response
from sanic.response import text, json
import os
import uuid
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import zipfile
import json as json_lib
from aliyunsdkcore.client import AcsClient  # 示例，需安装阿里云SDK
from aliyunsdkalinlp.request.v20200629 import GetSentimentRequest  

app = Sanic("mySanic")


#影评数据文件上传接口
@app.route("/v1/movie/crawled/upload", methods=['POST'])
async def upload_movie_comments(request):
    # 获取上传的文件
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return json({"code": 0, "msg": "No file uploaded", "data": None})
    
    # 生成唯一文件名
    filename = f"{int(time.time())}_{uploaded_file.name}"
    save_path = os.path.join("upload", filename)
    
    # 保存文件到本地
    try:
        with open(save_path, 'wb') as f:
            f.write(uploaded_file.body)
        return json({
            "code": 1,
            "msg": "File uploaded successfully",
            "data": {"filename": filename}
        })
    except Exception as e:
        return json({"code": 0, "msg": f"Error saving file: {str(e)}", "data": None})

#影评数据情感分析接口（选做）
@app.route("/v1/movie/comment/sentiment-analysis", methods=['GET'])
async def analyze_sentiment(request):
    # 参数获取
    filename = request.args.get("filename")
    movie_id = request.args.get("movie_id")
    
    # 参数校验
    if not filename:
        return json({"code": 0, "msg": "Filename is required", "data": None})
    
    file_path = os.path.join("upload", filename)
    if not os.path.exists(file_path):
        return json({"code": 0, "msg": "File not found", "data": None})
    
    try:
        # 读取并解析JSON文件
        with open(file_path, 'r', encoding='UTF-8') as f:
            movie_data = json_lib.load(f)
        
        # 过滤指定电影（如果提供movie_id）
        if movie_id:
            target_movie = next(
                (m for m in movie_data if str(m.get("movie_id")) == str(movie_id)),
                None
            )
            if not target_movie:
                return json({"code": 1, "msg": "Movie not found", "data": []})
            comments = target_movie.get("comment_list", [])
        else:
            comments = [c for m in movie_data for c in m.get("comment_list", [])]
        
        # 调用阿里云情感分析API
        sentiment_results = []
        client = AcsClient("<your-access-key>", "<your-access-secret>", "cn-hangzhou")
        for comment in comments:
            req = GetSentimentRequest()
            req.set_Text(comment.get("comment_content"))
            resp = client.do_action_with_exception(req)
            sentiment = json_lib.loads(resp)
            sentiment_results.append({
                "comment_id": comment.get("comment_id"),
                "positive": sentiment.get("PositiveScore", 0),
                "negative": sentiment.get("NegativeScore", 0)
            })
        
        return json({
            "code": 1,
            "msg": "Analysis completed",
            "data": sentiment_results
        })
    
    except Exception as e:
        return json({"code": 0, "msg": f"Error: {str(e)}", "data": None})


#影评数据可视化与下载接口
@app.route("/v1/movie/comment/sentiment-analysis/package", methods=['GET'])
async def generate_visualization_package(request):
    filename = request.args.get("filename")
    if not filename:
        return json({"code": 0, "msg": "Filename is required", "data": None})
    
    file_path = os.path.join("upload", filename)
    if not os.path.exists(file_path):
        return json({"code": 0, "msg": "File not found", "data": None})
    
    try:
        # 读取数据并生成图表
        with open(file_path, 'r', encoding='UTF-8') as f:
            movie_data = json_lib.load(f)
        
        zip_filename = f"visualization_{uuid.uuid4().hex}.zip"
        zip_path = os.path.join("download", zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for movie in movie_data:
                movie_name = movie.get("movie_name")
                
                # 生成饼状图（情感分析）
                sentiments = [c.get("sentiment", 0.5) for c in movie.get("comment_list", [])]  # 假设已有情感值
                plt.figure()
                plt.pie([sum(s > 0.5 for s in sentiments), sum(s <= 0.5 for s in sentiments)],
                        labels=['Positive', 'Negative'],
                        autopct='%1.1f%%')
                plt.title(f"{movie_name} Sentiment Analysis")
                chart_path = f"{movie_name}_sentiment.png"
                plt.savefig(chart_path)
                zipf.write(chart_path)
                plt.close()
                
                # 生成词云
                text = ' '.join([c.get("comment_content", "") for c in movie.get("comment_list", [])])
                wordcloud = WordCloud(width=800, height=400).generate(text)
                plt.figure()
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis("off")
                wordcloud_path = f"{movie_name}_wordcloud.png"
                plt.savefig(wordcloud_path)
                zipf.write(wordcloud_path)
                plt.close()
        
        # 返回下载链接
        return response.file(
            zip_path,
            headers={
                "Content-Disposition": f"attachment; filename={zip_filename}"
            }
        )
    
    except Exception as e:
        return json({"code": 0, "msg": f"Error: {str(e)}", "data": None})


if __name__ == '__main__':
    # 确保上传和下载目录存在
    os.makedirs("upload", exist_ok=True)
    os.makedirs("download", exist_ok=True)
    app.run(host='0.0.0.0', port=8000, debug=True)
