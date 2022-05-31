from importlib.resources import path
from urllib import response
import requests
import json
import os
import time
import datetime
from lxml import etree
import re


"""
    该网易爬虫定在每日13:00执行
"""


headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/\
            537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}


today=str(datetime.datetime.now())[5:7]+str(datetime.datetime.now())[8:10]
print(today)


def format_time():
    """
    生成时间格式-作为文件名称
    """

    t = time.localtime()
    # Time = time.strftime("%Y-%m-%d-%H:%M:%S", t)
    Time = time.strftime("%Y-%m-%d-%H", t)
    return Time


def make_dir(key_p, key_c):
    """
    根据目录以及子目录创建文件夹
    如 Netease/ent/movie
        key_p = ent
        key_c = movie
     """

    root_path = os.path.abspath(os.path.dirname(__file__))

    root_path = root_path + '/Netease/'

    if not os.path.exists(root_path):
        os.mkdir(root_path)

    path = root_path + key_p
    if not os.path.exists(path):
        os.mkdir(path)

    path = root_path + key_p + '/' + key_c
    if not os.path.exists(path):
        os.mkdir(path)

    path = root_path + key_p + '/' + key_c + '/' + format_time()
    if not os.path.exists(path):
        os.mkdir(path)

    return path


def save_data_callback(path, data):
    """
    保存 callback 中数据组字典
    """
    path = path + '/' + today + '.json'
    json.dump(data, open(path , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


def request_data(url):
    """ 请求URL数据 """
    response  = requests.get(url, headers=headers).text
    return response


def get_external_dict(url, key_p, key_e):
    """
    针对 external类数据进行爬取进行数据解析
    """
    response = request_data(url)
    tree = etree.HTML(response)

    data = []
    # print(url)

    if key_p == 'money':
        news_flow_content = tree.xpath('//*[@id="money_wrap"]/div/div[3]/div[1]/div')
        for div in news_flow_content:
            if div.xpath('./@class') == ['list_item clearfix']:

                title = div.xpath('.//div/h2/a/text()')[0].strip()
                news_url = div.xpath('./div/h2/a/@href')[0].strip()
                release_time = div.xpath('./div/p/span/text()')[0].strip()

                data_dict = {
                    'title':title,
                    'news_url': news_url,
                    'label': key_e,
                    'time': release_time,
                    'comment_url': None,
                    'comment_count': None,
                }
                data.append(data_dict)

    else:
        news_flow_content = tree.xpath('//*[@id="news-flow-content"]/li')

        for li in news_flow_content:
            title = li.xpath('./div[1]/h3/a/text()')[0].strip()
            news_url = li.xpath('./div[1]/h3/a/@href')[0].strip()
            label = li.xpath('./div[3]/p[2]/span/text()')[0].strip()
            release_time = li.xpath('./div[3]/p[2]/text()')[0].strip()
            comment_url = li.xpath('./div[3]/p[1]/a/@href')[0].strip()
            comment_count = li.xpath('./div[3]/p[1]/a/text()')[0].strip()

            data_dict = {
                'title':title,
                'news_url': news_url,
                'label': label,
                'time': release_time,
                'comment_url': comment_url,
                'comment_count': comment_count,
            }
            data.append(data_dict)

    if data == []:
        state_code = '404'
    else:
        state_code = 'successful'

    outputs = {'state': state_code, 'responses': data}

    return outputs


def get_data_callback(url, key_c):
    """ 请求非 external 数据 """
    response = request_data(url)
    response = response[14:-1]
    # print(response)

    try:
        if key_c == 'digi':
            # digi https://digi.163.com 部分单独处理
            result = re.findall('"keywords":\[\\n(?P<name>.*?)\\n', response)
            response = response.replace(result[0], '')

        response = json.loads(response)
        state_code = 'successful'

    except:
        # print("404 访问的页面不存在！")
        response = []
        state_code = '404'

    outputs = {'state': state_code, 'responses': response}

    return outputs


def nums_format(nums):
    """
    将数据数字转成字符数字
    例如：1 -> 01
    """
    if nums < 10:
        str_nums = '0' + str(nums)
    else:
        str_nums = str(nums)
    return str_nums


def urls_datas(list_nums):
    news_urls = {
        'guonei': {
            'index': 'https://news.163.com/special/cm_guonei/?callback=data_callback',
            'post': f'https://news.163.com/special/cm_guonei_{list_nums}/?callback=data_callback'},

        'guoji': {
            'index':'https://news.163.com/special/cm_guoji/?callback=data_callback',
            'post': f'https://news.163.com/special/cm_guoji_{list_nums}/?callback=data_callback'},

        'yaowen': {
            'index': 'https://temp.163.com/special/00804KVA/cm_yaowen20200213.js?callback=data_callback',
            'post': f'https://temp.163.com/special/00804KVA/cm_yaowen20200213_{list_nums}.js?callback=data_callback'},
    }


    # 科技板块
    tech_urls = {
        'tech': {
            'index': 'https://tech.163.com/special/00097UHL/tech_datalist.js?callback=data_callback',
            'post': f'https://tech.163.com/special/00097UHL/tech_datalist_{list_nums}.js?callback=data_callback'},
        'smart': {
            'index': 'https://tech.163.com/special/00097UHL/smart_datalist.js?callback=data_callback',
            'post': f'https://tech.163.com/special/00097UHL/smart_datalist_{list_nums}.js?callback=data_callback'},
        'mobile': {
            'index': 'https://mobile.163.com/special/index_datalist/?callback=data_callback',
            'post': f'https://mobile.163.com/special/index_datalist_{list_nums}/?callback=data_callback'},
        'digi': {
            'index': 'https://digi.163.com/special/index_datalist/?callback=data_callback',
            'post': f'https://digi.163.com/special/index_datalist_{list_nums}/?callback=data_callback'},


         'external': {
             # 滚动新闻
            'gd': {
                'index': 'https://tech.163.com/gd/',
                'post': f'https://tech.163.com/special/gd2016_{list_nums}/'},
             # 互联网
            'internet': {
                'index': 'https://tech.163.com/internet/',
                'post': f'https://tech.163.com/special/internet_2016_{list_nums}/'},
            # 5G
            '5G': {
                'index': 'https://tech.163.com/5g/',
                'post': f'https://tech.163.com/special/5g_2019_{list_nums}/'},
            # 通讯
            'telecom': {
                'index': 'https://tech.163.com/telecom/',
                'post': f'https://tech.163.com/special/tele_2016_{list_nums}/'},
            # IT
            'it': {
                'index': 'https://tech.163.com/it/',
                'post': f'https://tech.163.com/special/it_2016_{list_nums}/'},
            # 科学
            'techscience': {
                'index': 'https://tech.163.com/special/techscience/',
                'post': f'https://tech.163.com/special/techscience_{list_nums}/'},
            # 区块链
            'blockchain': {
                'index': 'https://tech.163.com/blockchain/',
                'post': f'https://tech.163.com/special/blockchain_2018_{list_nums}/'},
        }
    }


    # 娱乐板块
    ent_urls = {
        'index': {
            'index': 'https://ent.163.com/special/000380VU/newsdata_index.js?callback=data_callback',
            'post': f'https://ent.163.com/special/000380VU/newsdata_index_{list_nums}.js?callback=data_callback'},
        'star': {
            'index': 'https://ent.163.com/special/000380VU/newsdata_star.js?callback=data_callback',
            'post': f'https://ent.163.com/special/000380VU/newsdata_star_{list_nums}.js?callback=data_callback'},
        'movie': {
            'index': 'https://ent.163.com/special/000380VU/newsdata_movie.js?callback=data_callback',
            'post': f'https://ent.163.com/special/000380VU/newsdata_movie_{list_nums}.js?callback=data_callback'},
        # 电视剧
        'tv': {
            'index': 'https://ent.163.com/special/000380VU/newsdata_tv.js?callback=data_callback',
            'post': f'https://ent.163.com/special/000380VU/newsdata_tv_{list_nums}.js?callback=data_callback'},
        # 综艺
        'show': {
            'index': 'https://ent.163.com/special/000380VU/newsdata_show.js?callback=data_callback',
            'post': f'https://ent.163.com/special/000380VU/newsdata_show_{list_nums}.js?callback=data_callback'},
        'music': {
            'index': 'https://ent.163.com/special/000380VU/newsdata_music.js?callback=data_callback',
            'post': f'https://ent.163.com/special/000380VU/newsdata_music_{list_nums}.js?callback=data_callback'},

        'external': {
            # 综艺节目
            'zongyijiemu': {
                'index': 'https://ent.163.com/special/00032VQS/zongyijiemu.html',
                'post': f'https://ent.163.com/special/00032VQS/zongyijiemu_{list_nums}.html'},
        }
    }


    # 体育板块
    sport_urls = {
        'NBA': {
            'index': 'https://sports.163.com/special/000587PR/newsdata_n_nba.js?callback=data_callback',
            'post': f'https://sports.163.com/special/000587PR/newsdata_n_nba_{list_nums}.js?callback=data_callback'},
        # 国际足球
        'world': {
            'index': 'https://sports.163.com/special/000587PR/newsdata_n_world.js?callback=data_callback',
            'post': f'https://sports.163.com/special/000587PR/newsdata_n_world_{list_nums}.js?callback=data_callback'},
        # 国内足球
        'china': {
            'index': 'https://sports.163.com/special/000587PR/newsdata_n_china.js?callback=data_callback',
            'post': f'https://sports.163.com/special/000587PR/newsdata_n_china_{list_nums}.js?callback=data_callback'},
        'CBA': {
            'index': 'https://sports.163.com/special/000587PR/newsdata_n_cba.js?callback=data_callback',
            'post': f'https://sports.163.com/special/000587PR/newsdata_n_cba_{list_nums}.js?callback=data_callback'},
        # 综合
        'allsports': {
            'index': 'https://sports.163.com/special/000587PR/newsdata_n_allsports.js?callback=data_callback',
            'post': f'https://sports.163.com/special/000587PR/newsdata_n_allsports_{list_nums}.js?callback=data_callback'},
    }


    # 财经
    money_urls = {
        # 首页
        'index': {
            'index': 'https://money.163.com/special/00259BVP/news_flow_index.js?callback=data_callback',
            'post': f'https://money.163.com/special/00259BVP/news_flow_index_{list_nums}.js?callback=data_callback'},
        # 股票
        'stock': {
            'index': 'https://money.163.com/special/00259BVP/news_flow_stock.js?callback=data_callback',
            'post': f'https://money.163.com/special/00259BVP/news_flow_stock_{list_nums}.js?callback=data_callback'},
        # 港股
        'hkstock': {
            'index': 'https://money.163.com/special/002557S6/newsdata_gp_hkstock.js?callback=data_callback',
            'post': f'https://money.163.com/special/002557S6/newsdata_gp_hkstock_{list_nums}.js?callback=data_callback'},
        # 美股
        'usstock': {
            'index': 'https://money.163.com/special/002557S6/newsdata_gp_usstock.js?callback=data_callback',
            'post': f'https://money.163.com/special/002557S6/newsdata_gp_usstock_{list_nums}.js?callback=data_callback'},
        # 新股
        'ipo': {
            'index': 'https://money.163.com/special/002557S6/newsdata_gp_ipo.js?callback=data_callback',
            'post': f'https://money.163.com/special/002557S6/newsdata_gp_ipo_{list_nums}.js?callback=data_callback'},
        # 期货
        'qhzx': {
            'index': 'https://money.163.com/special/002557S6/newsdata_gp_qhzx.js?callback=data_callback',
            'post': f'https://money.163.com/special/002557S6/newsdata_gp_qhzx_{list_nums}.js?callback=data_callback'},
        # 外汇
        'forex': {
            'index': 'https://money.163.com/special/002557S6/newsdata_gp_forex.js?callback=data_callback',
            'post': f'https://money.163.com/special/002557S6/newsdata_gp_forex_{list_nums}.js?callback=data_callback'},
        # 比特币
        'bitcoin': {
            'index': 'https://money.163.com/special/002557S6/newsdata_gp_bitcoin.js?callback=data_callback',
            'post': f'https://money.163.com/special/002557S6/newsdata_gp_bitcoin_{list_nums}.js?callback=data_callback'},

        # 商业
        'biz': {
            'index': 'https://money.163.com/special/00259BVP/news_flow_biz.js?callback=data_callback',
            'post': f'https://money.163.com/special/00259BVP/news_flow_biz_{list_nums}.js?callback=data_callback'},
        # 基金
        'fund': {
            'index': 'https://money.163.com/special/00259BVP/news_flow_fund.js?callback=data_callback',
            'post': f'https://money.163.com/special/00259BVP/news_flow_fund__{list_nums}.js?callback=data_callback'},
        # 房产
        'house': {
            'index': 'https://money.163.com/special/00259BVP/news_flow_house.js?callback=data_callback',
            'post': f'https://money.163.com/special/00259BVP/news_flow_house_{list_nums}.js?callback=data_callback'},
        # 汽车
        'car': {
            'index': 'https://money.163.com/special/00259BVP/news_flow_car.js?callback=data_callback',
            'post': f'https://money.163.com/special/00259BVP/news_flow_car_{list_nums}.js?callback=data_callback'},
        # 银行
        'bank': {
            'index': 'https://money.163.com/special/00259BVP/news_flow_bank.js?callback=data_callback',
            'post': f'https://money.163.com/special/00259BVP/news_flow_bank_{list_nums}.js?callback=data_callback'},
        # 理财
        'licai': {
            'index': 'https://money.163.com/special/00259BVP/news_flow_licai.js?callback=data_callback',
            'post': f'https://money.163.com/special/00259BVP/news_flow_licai_{list_nums}.js?callback=data_callback'},

        # 扩展非data_callback链接请求内容
        'external': {
            # 宏观
            'macro': {
                'index': 'https://money.163.com/special/00252G50/macro.html',
                'post': f'https://money.163.com/special/00252G50/macro_{list_nums}.html'},
            # 宏观国际新闻
            'gjcj': {
                'index': 'https://money.163.com/special/00252C1E/gjcj.html',
                'post': f'https://money.163.com/special/00252C1E/gjcj_{list_nums}.html'},
            # 原创
             'caijingyuanchuang': {
                'index': 'https://money.163.com/special/caijingyuanchuang/',
                'post': f'https://money.163.com/special/caijingyuanchuang_{list_nums}/'},
        },
    }


    # 时尚板块
    fashion_urls = {
        'fashion': {
            'index': 'https://fashion.163.com/special/002688FE/fashion_datalist.js?callback=data_callback',
            'post': f'https://fashion.163.com/special/002688FE/fashion_datalist_{list_nums}.js?callback=data_callback'},

    }


    # 旅游板块
    travel_urls = {
        'travel': {
            'index': 'https://travel.163.com/special/00067VEJ/newsdatas_travel.js?callback=data_callback',
            'post': f'https://travel.163.com/special/00067VEJ/newsdatas_travel_{list_nums}.js?callback=data_callback'},

    }


    all_urls = {
        'news': news_urls,
        'ent': ent_urls,
        'money': money_urls,
        'sport': sport_urls,
        'tech': tech_urls,
        'fashion': fashion_urls,
        'travel': travel_urls
    }

    return all_urls


def exe_external_url(news_urls, key_p, key_c, value_c):
    """ 执行external url 部分 """

    for key_e, value_e in value_c.items():
        external_datas = []
        # 首页数据
        external_data_index = get_external_dict(
                                news_urls[key_p][key_c][key_e]['index'],
                                key_p,
                                key_e,
                            )

        external_datas.extend(external_data_index['responses'])

        external_path = make_dir(key_p, key_e)

        for index in range(2, 30, 1):
            list_nums = nums_format(index)
            news_urls = urls_datas(list_nums)
            external_data_post = get_external_dict(
                                news_urls[key_p][key_c][key_e]['post'],
                                key_p,
                                key_e,
                                )

            # 若返回404页面则停止访问
            if external_data_post['state'] == '404':
                print(f'{key_p} | {key_c} | {key_e}    MAX index list:', index-1)
                break
            external_datas.extend(external_data_post['responses'])

        # 保存 external 数据
        save_data_callback(external_path, external_datas)


def main():
    # 获取请求列表
    news_urls = urls_datas(1)

    for key_p, value_p in news_urls.items():
        for key_c, value_c in value_p.items():

            # 若是额外的资源URL，执行这个exe_external_url函数门后面的内筒则不在执行
            if key_c == 'external':
                exe_external_url(news_urls, key_p, key_c, value_c)
                continue

            # 初始化保存数据列表，用于文件保存
            general_datas = []

            # 创建类别目录
            path = make_dir(key_p, key_c)


            """ 执行主体部分 """
            # 请求首页callback数据 --> index
            outputs = get_data_callback(news_urls[key_p][key_c]['index'], key_c)

            general_datas.extend(outputs['responses'])

            # 请求后续页面callback数据，设置最大新闻页面20
            for index in range(2, 20, 1):
                list_nums = nums_format(index)
                news_urls = urls_datas(list_nums)

                # 获取后续页面的数据 --> post
                outputs = get_data_callback(news_urls[key_p][key_c]['post'], key_c)

                # 若返回404页面则停止访问
                if outputs['state'] == '404':
                    print(f'{key_p} | {key_c} stop index list:', index-1)
                    break

                general_datas.extend(outputs['responses'])


            # # 保存数据
            save_data_callback(path, general_datas)


if __name__ == '__main__':
    main()


