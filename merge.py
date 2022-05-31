import os
import json


main_path = './Netease'


def remove_filename(base_path, base_filelists):
    log_files = base_path + '/log.json'

    if  os.path.exists(log_files):
        with open(log_files, 'r', encoding='utf-8') as f:
            log_files_dict = json.load(f)
        log_list = log_files_dict['logged']
    else:
        log_list = []

    # (2) 去除非相关数据的文件和目录
    new_base_filelists = []
    for item in base_filelists:
        if item == 'total_data.json' or item == 'data_total_all.json' or item == 'image' or item == 'log.json':
            pass
        else:
            new_base_filelists.append(item)

    new_base_filelists = [i for i in new_base_filelists if i not in log_list]

    print("新增文件名字：", new_base_filelists)
    return new_base_filelists


def data_save(data, path):
    json.dump(data, open(path , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


def log_merged_files(base_path, base_filelists):
    log_files = base_path + '/log.json'

    new_base_filelists = []
    for item in base_filelists:
        if item == 'total_data.json' or item == 'data_total_all.json' or item == 'image' or item == 'log.json':
            pass
        else:
            new_base_filelists.append(item)

    # log_data = {'logged': new_base_filelists}
    log_data = {'logged': []}
    data_save(log_data, log_files)


""" 将不同日期的数据进行合并，数据去重，并单独在各个子类别中保存为total_data.json文件中  """
main_filelists = os.listdir(main_path)
for main_filename in main_filelists:
    sub_path = main_path + '/' + main_filename
    sub_filelists = os.listdir(sub_path)
    for sub_filename in sub_filelists:
        base_path = main_path + '/' + main_filename + '/' + sub_filename

        """ 开始在这一级执行合并操作 """
        total_data_path = base_path + '/total_data.json'
        if not os.path.exists(total_data_path):
            total_data_dict = {}
        else:
            with open(total_data_path, 'r', encoding='utf-8') as f:
                total_data_dict = json.load(f)

        base_filelists_ori = os.listdir(base_path)

        # 去除不需要的文件
        base_filelists = remove_filename(base_path, base_filelists_ori)

        # 记录已经合并的文件，下次合并时直接跳过该文件
        log_merged_files(base_path, base_filelists_ori)


        for low_filename in base_filelists:
            low_path = main_path + '/' + main_filename + '/' + sub_filename + '/' + low_filename

            print(base_path)

            # 获取json数据文件目录
            files = os.listdir(low_path)[0]
            file_path = low_path + '/' + files

            with open(file_path, 'r', encoding='utf-8') as load_f:
                load_dict = json.load(load_f)
                for i in range(len(load_dict)):

                    Title = load_dict[i]['title']

                    # 若新闻不在total_data_dict中，则该新闻被新增加
                    if Title  not in total_data_dict:
                        total_data_dict.update({Title: load_dict[i]})

                    else:
                        # 若该新闻存在，但comment_count为0，需要更新comment_count内容

                        # (1)tienum为评论的key
                        if 'tienum' in total_data_dict[Title]:
                            comment_count = int(total_data_dict[Title]['tienum'])

                            # comment_count为0才执行更新操作
                            if comment_count == 0:
                                # 更新评论数量的值
                                total_data_dict[Title]['tienum'] = load_dict[i]['tienum']

                        # (2) comment_count为评论的key
                        elif 'comment_count' in total_data_dict[Title]:
                            if total_data_dict[Title]['comment_count'] != None:
                                comment_count =  int(total_data_dict[Title]['comment_count'])
                                if comment_count == 0:
                                    total_data_dict[Title]['comment_count'] = load_dict[i]['comment_count']

            data_save(total_data_dict, base_path + '/total_data.json')



