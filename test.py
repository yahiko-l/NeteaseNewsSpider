from bs4 import BeautifulSoup
import requests
import json,datetime,os


""" 爬虫测试代码 """


today=str(datetime.datetime.now())[5:7]+str(datetime.datetime.now())[8:10]

headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/\
            537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
news_num=0
mulu=''

print('本程序自动爬取网易新闻（国内/国际/要闻版）首页的70条新闻评论。生成文件并保存。\n\n制作：云云\n完工：2021-6-3')

key0=input('\n输入1-国内新闻，2-国际新闻，3-要闻：')
duiying={'1':'guonei','2':'guoji','3':'yaowen20200213'}
key=duiying[key0]

foldername=today+key+'/'

try:
    os.makedirs(foldername)
except:
    pass


def getcomments(idd):
    comment_num=0
    content=''
    url1='https://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/'
    # 热评
    url2='/comments/hotList'
    url=url1+idd+url2
    params={'ibc': 'newspc',
            'limit': 40,
            'showLevelThreshold': 72,
            'headLimit': 1,
            'tailLimit': 2,
            'offset': 0,
            'callback': 'jsonp_1622619924685',
            '_': 1622619924686}
    res=requests.get(url,params=params,headers=headers)
    res=res.text[20:-1]
    res='['+res+']'
    jsoner=json.loads(res)

    try:
        comments=jsoner[0]["comments"]
        for i in comments:
            comment_num+=1
            content+=str(comment_num)+':'+comments[i]['content']+'\n'
    except:
        content='no comments'
    return content


urla='https://temp.163.com/special/00804KVA/cm_'
urlb='.js?callback=data_callback'

# https://temp.163.com/special/00804KVA/cm_guonei.js?callback=data_callback
# https://temp.163.com/special/00804KVA/cm_guoji.js?callback=data_callback
# https://temp.163.com/special/00804KVA/cm_yaowen20200213.js?callback=data_callback
url0=urla+key+urlb


res0=requests.get(url0,headers=headers).text
res0=res0[14:-1]
res0='['+res0+']'
js0=json.loads(res0)

items=js0[0]


for i in items:
    news_num+=1
    title=i['title']
    print(i['commenturl'])
    idd=i['commenturl'][-21:-5]
    txtname=foldername+str(news_num)+'.txt'
    muluname=foldername+'0-目录.txt'
    content=getcomments(idd)
    mulu+=(str(news_num)+':'+title+'\n')
    print(str(news_num)+':'+title)
    with open (txtname,'w',encoding='utf-8') as f:
        f.write(title+'\n'+content)


with open (muluname,'w',encoding='utf-8') as f2:
    f2.write(mulu)