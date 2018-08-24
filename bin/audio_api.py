#!/usr/bin/python3.6
#-*- coding: UTF-8 -*-

import threading
import time
import sound2wordXF
import sound2wordBD
import record_vad
import moni_record
import os
import shutil
from mark_new_file import getFileListType

path = "D:\\pycharm_project\\voice_monitor_vad_text\\audio_file\\"    # 录音得到的音频文件夹
audio_vad_file = "D:\\pycharm_project\\voice_monitor_vad_text\\audio_vad_file\\"      # 切割后的音频文件夹

def audio_vad():
    while True:
        nowtime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        record_path = path + nowtime + r".wav"  # 以时间命名
        #print(' Writing %s' % (record_path,))
        moni_record.monitor(record_path)
        record_vad.main(record_path)
        #print('语音切割完成时间：%s!' % time.ctime())

mu = threading.Lock()   # 1、创建一个锁

def file_asr():
    # 初始化切割后的语音存放文件夹（清除文件夹下所有文件）
    if os.path.exists(audio_vad_file):
        shutil.rmtree("D:\\pycharm_project\\voice_monitor_vad_text\\audio_vad_file")  # 将整个文件夹删除
        os.makedirs(audio_vad_file)  # 创建一个文件夹
    else:
        os.makedirs(audio_vad_file) # 没有文件夹就新建一个

    deal_type_dict = {}

    while True:
        try:
            # 更新文件夹，将新生成的（新被切割的）音频文件标记，然后进行语音听写操作
            getFileListType(audio_vad_file, deal_type_dict)
            # print(deal_type_dict)
            time.sleep(10)
            for deal_file in deal_type_dict:
                if deal_type_dict[deal_file] == 0:
                    '''deal_next_function(deal_file)  # 对新文件处理操作：删除杂音，空的的音频文件等（后续要加）'''
                    file_path = audio_vad_file + deal_file
                    res = sound2wordBD.asr_main(file_path)  # 百度语音听写
                    # res = sound2wordXF.wordfromS(file_path)  # 讯飞语音听写
                    if mu.acquire():    # 2、获取锁状态，一个线程有锁时，别的线程只能在外面等着
                        vad_text_file = "D:\\pycharm_project\\voice_monitor_vad_text\\vad_test.txt"
                        with open(vad_text_file, 'a') as f:
                            if res != None:
                                #text_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                                f.write(res + '\n')     # 不加锁多线程读写文件会出现错误
                            else:
                                f.write('')
                        mu.release()  # 3、释放锁

                    #print("新文件经过处理")
                    deal_type_dict[deal_file] = 1  # 并标识处理过的文件
                    continue
            print(deal_type_dict)
            #print("标记及处理完毕")

        except:
            print("语音听写写入文件出错")
            break


if __name__ == '__main__':
    t1 = threading.Thread(target=audio_vad)
    t2 = threading.Thread(target=file_asr)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print('end:%s' % time.ctime())








