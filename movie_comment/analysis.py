import time
import json
import os
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

if __name__ == '__main__':
    input_path = "input/movie_comment.json"
    if not os.path.exists(input_path):
        print({"code": 0, "msg": "file is not exists"})
        exit(1)

    now_time = time.strftime('%Y%m%d%H%M%S', time.localtime())
    output_path = "json/" + now_time + "comment_emotion.json"

    # 读取评论内容
    with open(input_path, encoding='utf-8') as f:
        data = json.load(f)
        comment_contents = [item.get("comment_content", "") for item in data]

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

    # 写入到 JSON 文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print({"code": 1, "msg": "success", "output_file": output_path})
