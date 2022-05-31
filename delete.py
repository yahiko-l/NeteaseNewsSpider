import os
import shutil



main_path = './Netease'

main_filelists = os.listdir(main_path)
for main_filename in main_filelists:
    sub_path = main_path + '/' + main_filename
    sub_filelists = os.listdir(sub_path)
    for sub_filename in sub_filelists:
        base_path = main_path + '/' + main_filename + '/' + sub_filename

        # 删除指定目录文件
        # if sub_filename == 'external':
        #     print(base_path)
        #     # shutil.rmtree(base_path)

        base_filelists = os.listdir(base_path)
        for low_filename in base_filelists:
            low_path = main_path + '/' + main_filename + '/' + sub_filename + '/' + low_filename

            # if low_filename == '2022-05-28-11':
            #     print(low_path)
            #     # shutil.rmtree(low_path)
