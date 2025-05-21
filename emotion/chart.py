import os
import json
import jieba
import zipfile
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# 配置路径 
comment_path = os.getcwd() + "/json/book_comment.json"
emotion_path = os.getcwd() + "/json/comment_emotion.json"
stopword_path = "userless.txt"
output_dir = "output_images"
zip_filename = "comment_visuals.zip"

# 加载数据 
with open(comment_path, 'r', encoding="utf-8") as f1, open(emotion_path, 'r', encoding="utf-8") as f2:
    comments_data = json.load(f1)
    emotions_data = json.load(f2)

if len(comments_data) != len(emotions_data):
    print("评论和情绪文件长度不一致！")
    exit()

total_comments = len(comments_data)
positive_comments = sum(1 for e in emotions_data if e["is_positive"] == 1)
negative_comments = total_comments - positive_comments

#  图像保存目录 
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

#  柱状图绘制并保存 
def plot_comment_histogram():
    plt.figure(figsize=(8, 6))
    categories = ['全部评论', '正向评论', '负向评论']
    counts = [total_comments, positive_comments, negative_comments]
    plt.bar(categories, counts, color=['blue', 'green', 'red'])
    plt.ylabel('数量')
    plt.title('评论情感分析统计图')
    plt.tight_layout()
    save_path = os.path.join(output_dir, "emotion_bar_chart.png")
    plt.savefig(save_path)
    plt.close()
    print("柱状图保存为", save_path)

#  评论词云绘制并保存 
def plot_comment_wordcloud():
    comment_text = " ".join(comment["comment_content"] for comment in comments_data if comment["comment_content"].strip())
    if not comment_text:
        print("评论为空，无法生成词云")
        return

    cut_text = " ".join(jieba.lcut(comment_text))
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
    save_path = os.path.join(output_dir, "comment_wordcloud.png")
    plt.savefig(save_path)
    plt.close()
    #print("词云图保存为", save_path)

#  将图像打包为 zip 
def files_to_zip(zip_file_name: str, file_dir: str):
    with zipfile.ZipFile(zip_file_name, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for file_name in os.listdir(file_dir):
            full_path = os.path.join(file_dir, file_name)
            if os.path.isfile(full_path):
                zf.write(full_path, arcname=file_name)
    #print("图像已打包为", zip_file_name)


if __name__ == '__main__':
    plt.rcParams["font.sans-serif"] = ["Hiragino Sans GB"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"] = 14

    plot_comment_histogram()
    plot_comment_wordcloud()
    files_to_zip(zip_filename, output_dir)
