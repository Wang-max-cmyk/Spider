import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import asyncio
from config import HEADERS, COOKIES, INPUT_DIR, REQUEST_DELAY

def turnToStamp(time_str):
    """将时间字符串转换为时间戳"""
    dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    timestamp = int(dt.timestamp())
    return timestamp

def search_url_from_name(word_name, item_type):
    """根据名称搜索豆瓣ID"""
    if item_type == 'book':    
        url = f"https://www.douban.com/search?cat=1001&q={word_name}"
    elif item_type == 'movie':
        url = f"https://www.douban.com/search?cat=1002&q={word_name}"
    
    resp = requests.get(url, headers=HEADERS)
    bs = BeautifulSoup(resp.text, "html.parser")
    
    result_list = bs.find("div", {"class": 'result-list'})
    if result_list:
        first_list = result_list.find("div", {"class": "result"})
        if first_list:
            a_tap = first_list.find("a", {"class": "nbg"})
            onclick = a_tap.get("onclick")
            startt_index = onclick.find('sid: ') + len("sid: ")
            end_index = onclick.find(",", startt_index)
            sid = onclick[startt_index:end_index]
            return sid
    return "no"

async def crawl_comments(item_type, word_name, comment_count, status):
    """爬取豆瓣评论"""
    # 搜索ID
    sid = search_url_from_name(word_name, item_type)
    
    # 构建URL
    if item_type == 'book':
        url = f"https://book.douban.com/subject/{sid}/comments/"
    elif item_type == 'movie':
        url = f"https://movie.douban.com/subject/{sid}/comments/"
    
    # 计算分页
    page = 0
    final = comment_count // 20
    leav = comment_count % 20
    
    # 构建URL列表
    new_urls = []
    remaining = comment_count
    while remaining > 0:
        new_start = f"?start={page}"
        new_url = f"{url}{new_start}&limit=20&status={status}&sort=new_score"
        new_urls.append(new_url)
        page += 20
        remaining -= 20
    
    # 爬取评论
    comment_data = []
    
    for i, new_url in enumerate(new_urls):
        # 添加延迟，避免被封
        if i > 0:
            await asyncio.sleep(REQUEST_DELAY)
        
        # 发送请求
        resp = requests.get(new_url, headers=HEADERS, cookies=COOKIES)
        
        bs = BeautifulSoup(resp.text, "html.parser")
        
        # 根据类型解析评论
        if item_type == 'book':
            comment_items = bs.find_all("li", {"class": "comment-item"})
            
            # 处理最后一页不足20条的情况
            if i == len(new_urls) - 1 and leav != 0:
                items_to_process = comment_items[:leav]
            else:
                items_to_process = comment_items
            
            for item in items_to_process:
                comment_id = item["data-cid"]
                comment_time = item.find("a", {"class": "comment-time"}).get_text()
                comment_username = item.find("div", {"class": "avatar"}).find("a")["title"]
                
                # 评分可能不存在
                comment_info = item.find("span", {"class": "comment-info"}).find("span")
                try:
                    comment_rating = comment_info['title']
                except (KeyError, TypeError):
                    comment_rating = None
                
                comment_content = item.find("span", {"class": "short"}).get_text()
                comment_useful = item.find("span", {"class": "vote-count"}).get_text()
                
                comment = {
                    "comment_id": comment_id,
                    "comment_username": comment_username,
                    "comment_time": turnToStamp(comment_time),
                    "comment_rating": comment_rating,
                    "comment_content": comment_content,
                    "comment_useful": int(comment_useful)
                }
                comment_data.append(comment)
        
        elif item_type == 'movie':
            comment_items = bs.find_all("div", {"class": "comment-item"})
            
            # 处理最后一页不足20条的情况
            if i == len(new_urls) - 1 and leav != 0:
                items_to_process = comment_items[:leav]
            else:
                items_to_process = comment_items
            
            for item in items_to_process:
                comment_id = item["data-cid"]
                comment_time = item.find("span", {"class": "comment-time"})['title']
                comment_username = item.find("div", {"class": "avatar"}).find("a")["title"]
                
                # 评分可能不存在
                comment_info = item.find("span", {"class": "comment-info"}).find_all("span")
                try:
                    comment_rating = comment_info[1]['title']
                    if len(comment_rating) > 2:
                        comment_rating = None
                except (KeyError, IndexError):
                    comment_rating = None
                
                comment_content = item.find("span", {"class": "short"}).get_text()
                comment_useful = item.find("span", {"class": "vote-count"}).get_text()
                
                comment = {
                    "comment_id": comment_id,
                    "comment_username": comment_username,
                    "comment_time": comment_time,
                    "comment_rating": comment_rating,
                    "comment_content": comment_content,
                    "comment_useful": int(comment_useful)
                }
                comment_data.append(comment)
    
    # 保存到JSON文件
    json_file = os.path.join(INPUT_DIR, "1.json")
    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(comment_data, f, indent=4, ensure_ascii=False)
    
    return comment_data