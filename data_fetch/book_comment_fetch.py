import requests
from bs4 import BeautifulSoup
import sys
import json
import re
from datetime import datetime
headers_book={"user-agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0"}
headers_movie={"User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0"}
cookies={"utma":"81379588.410494284.1743421111.1747482902.1747489493.12"}
comment_data=[]
new_urls=[]
comment_count=int(sys.argv[3])
status=sys.argv[4]
choose=sys.argv[1]
page=0
final=comment_count//20
leav=comment_count%20

def turnToStamp(time):
    dt=datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
    timestamp=int(dt.timestamp())
    return timestamp

def search_url_from_name(headers):
    word_name=sys.argv[2]
    if sys.argv[1]=='-b':    
        url="https://www.douban.com/search?cat=1001&q="+word_name
    elif sys.argv[1]=='-m':
        url="https://www.douban.com/search?cat=1002&q="+word_name
    resp=requests.get(url,headers=headers)
    bs=BeautifulSoup(resp.text,"html.parser")
    print(resp.status_code)
    #print(resp.text)
    result_list=bs.find("div",{"class":'result-list'})
    if result_list:
        first_list=result_list.find("div",{"class":"result"})
        if(first_list):
            #print(first_list.text)
            a_tap=first_list.find("a",{"class":"nbg"})
            onclick=a_tap.get("onclick")
            startt_index=onclick.find('sid: ')+len("sid: ")
            end_index=onclick.find(",",startt_index)
            sid=onclick[startt_index:end_index]
            return sid
        return "no"
    return "no"
sid=search_url_from_name(headers_movie)
if choose=='-b':
    url="https://book.douban.com/subject/"+sid+"/comments/"
elif choose=='-m':
    url="https://movie.douban.com/subject/"+sid+"/comments/"
#获取url
while comment_count-20>-20:
    new_start="?start="+str(page)
    new_url=url+new_start+"&limit=20&status="+status+"&sort=new_score"
    new_urls.append(new_url)
    page+=20
    comment_count-=20
print(new_urls)

#遍历获得的url
for new_url in new_urls:
    #书籍
    if choose=='-b':
        resp=requests.get(new_url,headers=headers_movie,cookies=cookies)
        bs=BeautifulSoup(resp.text,"html.parser")
        comment_items=bs.find_all("li",{"class":"comment-item"})
        print(new_url)
        print(resp.status_code)
    #print(bs)
    #print(comment_items)
        if(new_url==new_urls[-1]  and leav!=0):
            for item in comment_items[0:leav]:
                comment_id=item["data-cid"]
                comment_time=item.find("a",{"class":"comment-time"}).get_text()
                comment_username=item.find("div",{"class":"avatar"}).find("a")["title"] 
                #注意：豆瓣评论有时不会有星级          
                comment_info=item.find("span",{"class":"comment-info"}).find("span")
                try:
                    comment_rating=comment_info['title']
                except KeyError:
                    comment_rating=None
                comment_content=item.find("span",{"class":"short"}).get_text()
                comment_useful=item.find("span",{"class":"vote-count"}).get_text()

                comment={
                        "comment_id":comment_id,
                        "comment_username":comment_username,
                        "comment_time":turnToStamp(comment_time),
                        "comment_rating":comment_rating,
                        "comment_content":comment_content,
                        "comment_useful":int(comment_useful),


                        }
                comment_data.append(comment)
                print("ok")
        else:
            for item in comment_items:

                comment_id=item["data-cid"]
                comment_time=item.find("a",{"class":"comment-time"}).get_text()
                comment_username=item.find("div",{"class":"avatar"}).find("a")["title"]
                comment_content=item.find("span",{"class":"short"}).get_text()
                comment_info=item.find("span",{"class":"comment-info"}).find("span")
                try:
                    comment_rating=comment_info['title']
                except KeyError:
                    comment_rating=None
                comment_useful=item.find("span",{"class":"vote-count"}).get_text()
                comment={
                        "comment_id":comment_id,
                        "comment_username":comment_username,
                        "comment_time":turnToStamp(comment_time),
                        
                        "comment_rating":comment_rating,
                        "comment_content":comment_content,
                        "comment_useful":int(comment_useful),


                        }
                comment_data.append(comment)
                print("ok")
        page+=20
        comment_count-=20
    elif choose=='-m':
        resp=requests.get(new_url,headers=headers_movie,cookies=cookies)
        bs=BeautifulSoup(resp.text,"html.parser")
        comment_items=bs.find_all("div",{"class":"comment-item"})
        print(new_url)
        print(resp.status_code)
    #print(bs)
    #print(comment_items)
        if(new_url==new_urls[-1]  and leav!=0):
            for item in comment_items[0:leav]:
                comment_id=item["data-cid"]
                comment_time=item.find("span",{"class":"comment-time"})['title']
                comment_username=item.find("div",{"class":"avatar"}).find("a")["title"] 
                #注意：豆瓣评论有时不会有星级          
                comment_info=item.find("span",{"class":"comment-info"}).find_all("span")
                try:
                    comment_rating=comment_info[1]['title']
                    if len(comment_rating)>2:
                        comment_rating=None
                except KeyError:
                    comment_rating=None
                comment_content=item.find("span",{"class":"short"}).get_text()
                comment_useful=item.find("span",{"class":"vote-count"}).get_text()

                comment={
                        "comment_id":comment_id,
                        "comment_username":comment_username,
                        "comment_time":comment_time,
                        "comment_rating":comment_rating,
                        "comment_content":comment_content,
                        "comment_useful":int(comment_useful),


                        }
                comment_data.append(comment)
                print("ok")
        else:
            for item in comment_items:

                comment_id=item["data-cid"]
                comment_time=item.find("span",{"class":"comment-time"})['title']
                comment_username=item.find("div",{"class":"avatar"}).find("a")["title"]
                comment_content=item.find("span",{"class":"short"}).get_text()
                comment_info=item.find("span",{"class":"comment-info"}).find_all("span")
                try:
                    comment_rating=comment_info[1]['title']
                    if len(comment_rating)>2:
                        comment_rating=None
                    
                except KeyError:
                    comment_rating=None
                comment_useful=item.find("span",{"class":"vote-count"}).get_text()
                comment={
                        "comment_id":comment_id,
                        "comment_username":comment_username,
                        "comment_time":comment_time,
                        
                        "comment_rating":comment_rating,
                        "comment_content":comment_content,
                        "comment_useful":int(comment_useful),


                        }
                comment_data.append(comment)
                print("ok")
        page+=20
        comment_count-=20

if choose=='-b':
    file='book_'+sys.argv[2]+'_'+sid+'.json'
else:
    file='movie_'+sys.argv[2]+'_'+sid+'.json'
with open(file,"w",encoding="utf-8") as f:
    json.dump(comment_data,f,indent=4,ensure_ascii=False)
