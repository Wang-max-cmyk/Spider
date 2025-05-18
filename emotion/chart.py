import matplotlib.pyplot as plt
import numpy as np
import json
import os
import jieba
from wordcloud import WordCloud


comment_path = os.getcwd() + "/json/book_comment.json"
emotion_path = os.getcwd() + "/json/comment_emotion.json"

# 加载评论与情感分析结果
with open(comment_path, 'r', encoding="utf-8") as f1, open(emotion_path, 'r', encoding="utf-8") as f2:
    comments_data = json.load(f1)
    emotions_data = json.load(f2)

# 合法性校验
if len(comments_data) != len(emotions_data):
    print("评论和情绪文件长度不一致！")
    exit()

# 统计数量
total_comments = len(comments_data)
positive_comments = sum(1 for e in emotions_data if e["is_positive"] == 1)
negative_comments = total_comments - positive_comments

# ---------- 柱状图绘制 ----------
def plot_comment_histogram():
    plt.figure(figsize=(8, 6))
    categories = ['全部评论', '正向评论', '负向评论']
    counts = [total_comments, positive_comments, negative_comments]
    plt.bar(categories, counts, color=['blue', 'green', 'red'])
    plt.ylabel('数量')
    plt.title('评论情感分析统计图')
    plt.tight_layout()
    plt.show()

# ---------- 评论词云绘制 ----------
def plot_comment_wordcloud():
    comment_text = " ".join(comment["comment_content"] for comment in comments_data if comment["comment_content"].strip())
    if not comment_text:
        print("评论为空，无法生成词云")
        return

    cut_text = " ".join(jieba.lcut(comment_text))
    with open('userless.txt', 'r', encoding='utf-8') as f:
        stopwords = set(f.read().split())

    stopwords.update(['\n', '', ' '])
    wordcloud = WordCloud(width=800, height=400, font_path='/Library/Fonts/Hiragino Sans GB.ttc',
                          background_color='white', max_words=200,
                          stopwords=stopwords, random_state=42).generate(cut_text)

    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title('评论词云图')
    plt.show()

# ---------- 主程序 ----------
if __name__ == '__main__':
    plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB"]  # 解决中文显示问题
    plt.rcParams["axes.unicode_minus"] = False              # 解决负号显示问题
    plt.rcParams["font.size"] = 14

    plot_comment_histogram()
    plot_comment_wordcloud()
