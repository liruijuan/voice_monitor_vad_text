import os
import time
import shutil

'''将文件夹中新生成的文件标记，从而进行识别'''

def getFileListType(path, deal_type_dict):
    '定时每分钟调用此函数'
    file_list = os.listdir(path)
    for file in file_list:
        # 判断是否是新进来的文件
        if file not in deal_type_dict:
            deal_type_dict[file] = 0  # 0表示文件未下一步操作,1表示已处理
            continue
    print("结束标记")

'''if __name__ == '__main__':

    # 初始化切割文件夹
    vad_filepath = ".\\audio_vad_file\\"
    #os.makedirs(vad_filepath)  # 创建一个文件夹
    shutil.rmtree("audio_vad_file")  # 将整个文件夹删除
    os.mkdir(vad_filepath)  # 重新创建文件夹

    deal_type_dict = {}

    while True:
        try:
            audio_vad_file = ".\\audio_vad_file\\"
            getFileListType(audio_vad_file, deal_type_dict)
            print(deal_type_dict)
            time.sleep(10)
            for deal_file in deal_type_dict:
                if deal_type_dict[deal_file] == 0:
                    # deal_next_function(deal_file)  # 新文件处理操作
                    print(deal_file)
                    print("新文件经过处理")
                    deal_type_dict[deal_file] = 1  # 并标识处理过的文件
                    continue

            print(deal_type_dict)
            print("标记及处理完毕")

        except:
            print("出错了")
            break'''
