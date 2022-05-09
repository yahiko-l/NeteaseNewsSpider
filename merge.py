import os
import json


main_path = './Netease'


""" 将不同日期的数据进行合并，数据去重，并单独在各个子类别中保存为total_data.json文件中  """
main_filelists = os.listdir(main_path)
for main_filename in main_filelists:
    sub_path = main_path + '/' + main_filename
    sub_filelists = os.listdir(sub_path)
    for sub_filename in sub_filelists:
        base_path = main_path + '/' + main_filename + '/' + sub_filename

        """ 开始在这一级执行合并操作 """
        total = {}
        print(base_path)

        base_filelists = os.listdir(base_path)
        for low_filename in base_filelists:
            low_path = main_path + '/' + main_filename + '/' + sub_filename + '/' + low_filename

            if low_filename == 'total_data.json':
                continue

            if low_filename == 'data_total_all.json':
                continue

            if low_filename == 'image':
                continue

            files = os.listdir(low_path)[0]
            file_path = low_path + '/' + files

            with open(file_path,'r') as load_f:
                load_dict = json.load(load_f)
                for i in range(len(load_dict)):
                    Title = load_dict[i]['title']

                    # 若键值不存在，那么将新增内容放入 total中
                    if Title  not in total:
                        temp_dict = {Title: load_dict[i]}
                        total.update(temp_dict)

                    json.dump(total, open(base_path + '/total_data.json' , 'w', encoding='utf-8'), indent=4, ensure_ascii=False)


