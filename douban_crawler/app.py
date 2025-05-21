from sanic import Sanic, response
from sanic.response import json, file, html, text
import os
import uuid
import asyncio
import time
import pandas as pd
from config import DATA_DIR, IMAGE_DIR, CSV_DIR, JSON_DIR, INPUT_DIR
from crawler import crawl_comments
from analyzer import analyze_sentiment, generate_charts

# 创建Sanic应用
app = Sanic("douban_crawler")

# 配置静态文件目录
app.static('/static', './static')

# 存储任务状态
tasks = {}

# 主页路由
@app.route('/')
async def index(request):
    with open('./static/index.html', 'r', encoding='utf-8') as f:
        return html(f.read())

# 爬取API
@app.route('/api/crawl', methods=['POST'])
async def crawl(request):
    # 获取请求参数
    data = request.json
    item_type = data.get('type')
    name = data.get('name')
    count = data.get('count', 50)
    status = data.get('status', 'P')
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 创建任务
    tasks[task_id] = {
        'status': 'processing',
        'type': item_type,
        'name': name,
        'count': count,
        'status_code': status,
        'created_at': time.time()
    }
    
    # 异步执行爬取和分析任务
    asyncio.create_task(process_task(task_id, item_type, name, count, status))
    
    return json({
        'code': 1,
        'msg': '任务已创建',
        'task_id': task_id
    })

# 异步处理任务
async def process_task(task_id, item_type, name, count, status):
    # 爬取评论
    comments = await crawl_comments(item_type, name, count, status)
    
    # 保存JSON文件
    json_file = os.path.join(INPUT_DIR, "1.json")
    
    # 生成CSV文件
    csv_file = os.path.join(CSV_DIR, "1.csv")
    
    # 转换为DataFrame并保存为CSV
    df = pd.DataFrame(comments)
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')

    # 情感分析
    emotion_data = await analyze_sentiment(comments)
    
    # 保存情感分析结果
    emotion_file = os.path.join(JSON_DIR, "1.json")
    
    # 生成图表
    chart_files = await generate_charts(comments, emotion_data)

    # 更新任务状态
    tasks[task_id]['status'] = 'completed'
    tasks[task_id]['json_file'] = "1.json"
    tasks[task_id]['csv_file'] = "1.csv"
    tasks[task_id]['sentiment_chart'] = os.path.basename(chart_files['sentiment'])
    tasks[task_id]['wordcloud_chart'] = os.path.basename(chart_files['wordcloud'])

# 获取任务状态API
@app.route('/api/task/<task_id>')
async def get_task(request, task_id):
    if task_id not in tasks:
        return json({'code': 0, 'msg': '任务不存在'})
    
    task = tasks[task_id]
    
    return json({
        'code': 1,
        'status': task['status'],
        'msg': task.get('msg', ''),
        'json_file': task.get('json_file', ''),
        'csv_file': task.get('csv_file', ''),
        'sentiment_chart': task.get('sentiment_chart', ''),
        'wordcloud_chart': task.get('wordcloud_chart', '')
    })

# 获取图片API
@app.route('/api/image/<filename>')
async def get_image(request, filename):
    return await file(os.path.join(IMAGE_DIR, filename))

# 下载文件API
@app.route('/api/download/<filename>')
async def download_file(request, filename):
    # 根据文件扩展名确定文件位置
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.json':
        file_path = os.path.join(INPUT_DIR, filename)
    elif ext == '.csv':
        file_path = os.path.join(CSV_DIR, filename)
    elif ext in ['.png']:
        file_path = os.path.join(IMAGE_DIR, filename)
    
    return await file(
        file_path,
        filename=filename,
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)