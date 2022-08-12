import os
import json


main_path = './Netease'


def data_save(data, path):
    json.dump(data, open(path , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


main_filelists = os.listdir(main_path)
for main_filename in main_filelists:
    sub_path = main_path + '/' + main_filename

    type_path = sub_path + '/' + main_filename +'.json'
    print(type_path)
    if not os.path.exists(type_path):
        type_data_dict = {}
    else:
        with open(type_path, 'r', encoding='utf-8') as f:
            type_data_dict = json.load(f)

    sub_filelists = os.listdir(sub_path)
    for sub_filename in sub_filelists:
        base_path = main_path + '/' + main_filename + '/' + sub_filename
        subtype_path = base_path + '/data_total_all.json'
        print(subtype_path)

        with open(subtype_path, 'r', encoding='utf-8') as load_f:
            load_dict = json.load(load_f)
            for title,value in load_dict.items():
                # 若新闻不在total_data_dict中，则该新闻被新增加
                if title  not in type_data_dict:
                    type_data_dict.update({title: value})

    print(f'\n {sub_path} total data is {len(type_data_dict)} \n')

    data_save(type_data_dict, type_path)