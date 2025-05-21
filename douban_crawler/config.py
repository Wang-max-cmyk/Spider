import os

# 基础目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 文件目录
DATA_DIR = os.path.join(BASE_DIR, 'data')
INPUT_DIR = os.path.join(DATA_DIR, 'input')
CSV_DIR = os.path.join(DATA_DIR, 'csv')
JSON_DIR = os.path.join(DATA_DIR, 'json')

# 图片目录
IMAGE_DIR = os.path.join(BASE_DIR, 'static', 'images')

# 豆瓣请求配置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0"
}

COOKIES = {
    "utma": "81379588.410494284.1743421111.1747482902.1747489493.12"
}

# 请求延迟（秒）
REQUEST_DELAY = 1
