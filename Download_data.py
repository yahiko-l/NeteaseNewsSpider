import json
import os

import requests
from bs4 import BeautifulSoup
from lxml import etree
import re
import hashlib



headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/\
            537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}


def image_saving(base_path, image_name, image_content):
    image_path = base_path + '/image/'
    if not os.path.exists(image_path):
        os.mkdir(image_path)
    with open(os.path.join(image_path, image_name), mode='wb') as f:
        f.write(image_content)


def request_comment_data(url, param):
    response  = requests.get(url, params=param,headers=headers)
    response.close()
    return response.text


def request_data(url):
    response  = requests.get(url, headers)
    response.close()
    return response.text


def request_image_data(url):
    response  = requests.get(url, headers)
    response.close()
    return response.content



def get_hotList(comment_url_hotList):
    hotList_params={
    'ibc': 'newspc',
    'limit': 40,    # 热评根据点赞热度对帖子排名，最大支持40层的评论
    'showLevelThreshold': 72,
    'headLimit': 1,
    'tailLimit': 2,
    'offset': 0,
    'callback': 'jsonp_1651923465510',  # 数据为时间戳
    '_': 1651923465511
    }

    """ 爬取热评评论数据 """
    response_hotList = request_comment_data(comment_url_hotList, hotList_params)
    response_hotList = response_hotList[20:-1]
    response_hotList = json.loads(response_hotList)

    return response_hotList



def get_newList(comment_base_url, comment_id):
    pass



def get_comments(url):
    comment_id = url.split('.')[-2].split('/')[-1]
    comment_base_url = 'https://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/'

    # 初始化评论保存字典
    comment_dict = {'hotList': {'commentIds': [], 'comments': {}},
                    'newList': {'commentIds': [], 'comments': {}}}

    hotList = '/comments/hotList'
    comment_url_hotList = comment_base_url + comment_id + hotList

    newList = '/comments/newList'
    newList_comment_url = comment_base_url + comment_id + newList

    try:
        """ 当不存在的评论返回内容为空 {"commentIds":[],"comments":{}} """
        # 热评数据
        response_hotList = get_hotList(comment_url_hotList)
        comment_dict['hotList']['commentIds'].extend(response_hotList['commentIds'])
        comment_dict['hotList']['comments'].update(response_hotList['comments'])


        """ 爬取最新评论数据 """
        # 页码偏置初始化
        offset = 0
        while True:
            newList_params={
                'ibc': 'newspc',
                'limit': 30,
                'showLevelThreshold': 72,
                'headLimit': 1,
                'tailLimit': 2,
                'offset': offset,
                'callback': 'jsonp_1651923465510',
                '_': 1651923465511
                }

            newList_response = request_comment_data(newList_comment_url, newList_params)
            newList_response = newList_response[20:-1]
            newList_response = json.loads(newList_response)

            offset += 30
            if newList_response['commentIds'] == []:
                break

            comment_dict['newList']['commentIds'].extend(newList_response['commentIds'])
            comment_dict['newList']['comments'].update(newList_response['comments'])
    except:
        """ 当遇到评论页面  文章已关闭跟贴 情况，需要单独处理 """
        try:
            print('热评-评论页面出错 ：', response_hotList['message'], comment_url_hotList)
        except:
            print('最新-评论页面出错 ：', newList_response['message'], comment_url_hotList)
    return comment_dict



def get_news(base_path, url):
    oir_news = request_data(url)
    bs = BeautifulSoup(oir_news, 'html.parser')
    post_body = bs.find('div', class_='post_body')

    news_dict = {}

    try:
        news_data = []
        ps = post_body.find_all('p')
        code = 200

        """ 获取新闻的文本数据 """
        for i in range(len(ps)):
            result = ps[i].text
            if result != '':
                news_data.append(result.strip())

        """ 获取新闻图像数据 """
        image_path = []
        img_urls = post_body.find_all('img')

        for img_url in img_urls:

            # 去掉logo图片
            if  img_url.get('alt') == None:
                # print(img_url)
                continue

            image_url = img_url.get('src')
            # 跳过gif图片链接
            if image_url[-4:] == '.gif':
                # print(image_url)
                continue

            image_content = request_image_data(image_url)

            # 根据img_url创建文件唯一文件名字
            image_url_encode = image_url.encode('utf-8')

            # 获取文件名后缀
            if '&' in image_url:
                file_postfix = image_url.split('=')[-1]
            else:
                # 处理image_url 没有指定 type 类型的情况
                file_postfix = image_url.split('.')[-1]
                # print(image_url)

            md5hash = hashlib.md5(image_url_encode)
            md5 = md5hash.hexdigest()
            image_name = md5 + '.' + file_postfix

            # 保存图片
            image_saving(base_path, image_name, image_content)

            # 图片路径用于json数据检索保存
            image_path.append(image_name)

        news_dict.update({'code': code, 'content': news_data, 'image_path': image_path})

    except:
        # 若请求页面为404, 则返回空字典
        news_dict.update({'code': 404, 'content': None, 'image_path': None})
        print('新闻页面 404： ', url)

    return news_dict



def read_json(path):
    with open(path,'r', encoding='utf-8') as f:
        load_dict = json.load(f)
    return load_dict


def save_data(path, data):
    path = path + '/' + 'data_total_all.json'
    json.dump(data, open(path , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


def get_url(base_path, data_dict):
    # 对 comment 和 news 增添到原有total_data_all.json文件中
    # 初始化
    total_data_all = {}

    # 当评论内容为空时，字典格式
    comment_None = {'hotList': {'commentIds': [], 'comments': {}},
                    'newList': {'commentIds': [], 'comments': {}}}

    for key, value in data_dict.items():
        # 判断 docurl 键值是否存在,处理 data_callback 的json格式数据
        if 'docurl' in value.keys():

            # 可以直接获取到 comment_url和 comment_count的参数
            news_url = value['docurl']
            news_dict = get_news(base_path, news_url)

            comment_count = value['tienum']
            if comment_count != 0:
                comment_url = value['commenturl']
                comment = get_comments(comment_url)
                comment_dict = {'comment': comment}
            else:
                comment_dict = {'comment': comment_None}

        elif value['comment_count'] != None:
            news_url = value['news_url']
            news_dict = get_news(base_path, news_url)

            comment_count = int(value['comment_count'])
            if comment_count != 0:
                comment_url = value['comment_url']
                comment = get_comments(comment_url)
                comment_dict = {'comment': comment}
            else:
                comment_dict = {'comment': comment_None}

        else:
            # 只有 news_url，无法直接获取 comment_url
            news_url = value['news_url']
            news_dict = get_news(base_path, news_url)

            # news_url 与 comment_url公用一个url
            comment = get_comments(news_url)
            comment_dict = {'comment': comment}

        # 更新 原字典的参数
        value.update(news_dict)
        value.update(comment_dict)

    save_data(base_path, data_dict)



def main():
    main_path = './Netease'

    main_filelists = os.listdir(main_path)
    for main_filename in main_filelists:
        sub_path = main_path + '/' + main_filename
        sub_filelists = os.listdir(sub_path)
        for sub_filename in sub_filelists:
            base_path = main_path + '/' + main_filename + '/' + sub_filename

            # 若 data_total_all.json 已经存在，则跳过对该 total_data.json 中url访问
            data_total_all_path = base_path + '/' + 'data_total_all.json'
            if os.path.exists(data_total_all_path):
                print(data_total_all_path, '已经存在！')
                continue

            """ 开始在这一级执行合并操作 """
            base_filelists = os.listdir(base_path)
            for low_filename in base_filelists:
                low_path = main_path + '/' + main_filename + '/' + sub_filename + '/' + low_filename

                if low_filename == 'total_data.json':
                    data_dict = read_json(low_path)
                    get_url(base_path, data_dict)

                """ 指定类别的 total_data.json 仅测试使用"""
                # if base_path == './Netease/ent/zongyijiemu':
                #     if low_filename == 'total_data.json':
                #         data_dict = read_json(low_path)
                #         get_url(base_path, data_dict)

if __name__ == '__main__':
    main()


