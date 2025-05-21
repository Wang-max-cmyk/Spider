import os
import asyncio
import json
import matplotlib.pyplot as plt
import numpy as np
import jieba
from wordcloud import WordCloud
import platform
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from config import JSON_DIR, IMAGE_DIR

async def analyze_sentiment(comments):
    """
    使用ModelScope进行情感分析
    
    Args:
        comments: 评论数据列表
        
    Returns:
        list: 情感分析结果
    """
    # 提取评论内容
    comment_contents = [item.get("comment_content", "") for item in comments]
    
    # 加载情感分析模型
    semantic_cls = pipeline(Tasks.text_classification, 'iic/nlp_structbert_sentiment-classification_chinese-tiny')
    result = semantic_cls(input=comment_contents)
    
    # 生成输出结果
    output_data = []
    for item in result:
        # 识别正负面标签
        sorted_labels_scores = sorted(zip(item['labels'], item['scores']), key=lambda x: x[0] == '正面', reverse=True)
        positive_label, positive_probs = sorted_labels_scores[0]
        negative_label, negative_probs = sorted_labels_scores[1]
        is_positive = 1 if positive_probs >= negative_probs else 0
        entry = {
            "is_positive": is_positive,
            "positive_probs": round(positive_probs, 4),
            "negative_probs": round(negative_probs, 4)
        }
        output_data.append(entry)
    
    # 保存到JSON文件
    output_path = os.path.join(JSON_DIR, "1.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return output_data

async def generate_charts(comments, emotions):
    """
    生成情感分析柱状图和词云图
    
    Args:
        comments: 评论数据列表
        emotions: 情感分析结果列表
        
    Returns:
        dict: 包含图表文件路径的字典
    """
    # 生成固定输出文件名
    sentiment_chart = "1_sentiment.png"
    wordcloud_chart = "1_wordcloud.png"
    
    sentiment_path = os.path.join(IMAGE_DIR, sentiment_chart)
    wordcloud_path = os.path.join(IMAGE_DIR, wordcloud_chart)
    
    # 统计数量
    total_comments = len(comments)
    positive_comments = sum(1 for e in emotions if e["is_positive"] == 1)
    negative_comments = total_comments - positive_comments
    
    # 设置字体
    if platform.system() == 'Darwin':  # macOS
        font_path = '/Library/Fonts/Hiragino Sans GB.ttc'
    elif platform.system() == 'Windows':
        font_path = 'C:/Windows/Fonts/simhei.ttf'
    else:
        font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'  # Linux
    
    plt.rcParams["axes.unicode_minus"] = False     # 解决负号显示问题
    
    # 绘制情感分析柱状图
    plt.figure(figsize=(10, 6))
    categories = ['All Comments', 'Positive Comments', 'Negatives Comments']
    counts = [total_comments, positive_comments, negative_comments]
    colors = ['#4A90E2', '#50C878', '#FF6B6B']  # 更现代的颜色
    
    bars = plt.bar(categories, counts, color=colors, width=0.6)
    
    # 添加数据标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'{height}', ha='center', va='bottom', fontsize=12)
    
    plt.ylabel('Quantity', fontsize=14)
    plt.title('Sentiment Analysis Statistical Chart', fontsize=16, fontweight='bold')
    plt.ylim(0, max(counts) * 1.15)  # 为数据标签留出空间
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.tight_layout()
    plt.savefig(sentiment_path, dpi=300)
    plt.close()
    
    # 生成词云图
    comment_text = " ".join(comment["comment_content"] for comment in comments if comment["comment_content"].strip())
    
    # 分词
    cut_text = " ".join(jieba.lcut(comment_text))
    
    # 加载停用词
    with open('userless.txt', 'r', encoding='utf-8') as f:
        stopwords = set(f.read().split())
    
    stopwords.update(['\n', '', ' '])
    
    # 创建词云
    wordcloud = WordCloud(
        width=1000, 
        height=600, 
        font_path=font_path,
        background_color='white', 
        max_words=200,
        stopwords=stopwords, 
        random_state=42,
        colormap='viridis',  # 更好看的颜色映射
        contour_width=1,
        contour_color='#4A90E2'
    ).generate(cut_text)
    
    # 保存词云图
    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(wordcloud_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return {
        'sentiment': sentiment_path,
        'wordcloud': wordcloud_path
    }