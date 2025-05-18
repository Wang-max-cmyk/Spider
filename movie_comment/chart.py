import matplotlib.pyplot as plt
import numpy as np
import os
import json

book_path=os.getcwd()+"/json/"+"book.json"
comment_path=os.getcwd()+"/json/"+"book_comment.json"
emotion_path=os.getcwd()+"/json/"+"comment_emotion.json"

is_positive="is_positive"
book_id = "book_id"
book_name = "book_name"
comment_content = "comment_content"

book_names=[]
comments=[]
positives=[]
negatives=[]

with open(book_path, 'r', encoding="UTF-8") as book_file, \
        open(comment_path, 'r', encoding="UTF-8") as comment_file, \
        open(emotion_path, 'r', encoding='UTF-8') as emotion_file:
    book_json = json.load(book_file)
    comment_json = json.load(comment_file)
    emotion_json = json.load(emotion_file)
                             
    # 获取评论个数、积极评论数、消极评论数​
    for i in range(0, len(book_json)):
        book_names.append(book_json[i][book_name])
        comment_num = 0
        positive_num = 0
        negative_num = 0
        for j in range(0, len(comment_json)):
            if book_json[i][book_id] == comment_json[j][book_id]:
                comment_num += 1
                if emotion_json[j][is_positive] == 1:
                    positive_num += 1
                else:
                    negative_num += 1
        comments.append(comment_num)
        positives.append(positive_num)
        negatives.append(negative_num)

def plot_book_comment_histogram():
    x = np.arange(len(book_names))  # x轴刻度标签位置​
    width = 0.1  # 柱子的宽度​
# 计算每个柱子在x轴上的位置，保证x轴刻度标签居中​
    plt.bar(x - width, comments, width, label='评论个数')
    plt.bar(x, positives, width, label='正向评论')
    plt.bar(x + width, negatives, width, label='负向评论')
    plt.ylabel('个数')
    plt.title('书籍评论详情')
# x轴刻度标签位置不进行计算​
    plt.xticks(x, labels=book_names)
    plt.legend()
    plt.show()

import jieba
from wordcloud import WordCloud
def plot_book_comment_wordcloud(id):
    # 图书评论字符串之和​
    comment = ""
    with open(book_path, 'r', encoding="UTF-8") as book_file, \
            open(comment_path, 'r', encoding="UTF-8") as comment_file:
        book_json = json.load(book_file)
        comment_json = json.load(comment_file)
        for i in range(0, len(book_json)):
            if book_json[i][book_id] != id:
                continue
            for j in range(0, len(comment_json)):
                if comment_json[j][book_id] == id:
                    comment += comment_json[j][comment_content]
              
    if comment == "":
        print({"code": -1, "message": "无对应ID的图书或该图书无评论信息"})
        return
    cut_text = " ".join(jieba.lcut(comment))
    mycloudword = WordCloud(width=400, height=300, scale=1, margin=2, font_path='/Library/Fonts/Hiragino Sans GB.ttc'  # 示例字体路径
,
                            background_color='white', max_words=200,
                            random_state=100).generate(cut_text)
    with open('userless.txt', 'r', encoding='utf-8') as f:
        stopWords = f.read()
    stopWords = ['\n', '', ' '] + stopWords.split()  # 前后列表拼接​
    mycloudword = WordCloud(width=400, height=300, scale=1, margin=2, font_path='/Library/Fonts/Hiragino Sans GB.ttc',  # 示例字体路径
                            background_color='white', max_words=200,
                            random_state=100,stopwords=stopWords).generate(cut_text)
    plt.imshow(mycloudword)
    plt.axis("off")   # 关闭坐标轴，必须​
    plt.show()


if __name__ == '__main__':
    plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB"]  # 设置字体​
    plt.rcParams["axes.unicode_minus"] = False    # 该语句解决图像中的“-”负号的乱码问题​
    plt.rcParams["font.size"] = 14                # 设置字体大小​
    plt.figure(figsize=(16, 9))                   # 设置画布为长16英寸，高9英寸​
    plot_book_comment_histogram()
    plot_book_comment_wordcloud(book_json[1][book_id])

    