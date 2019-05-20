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
import mongo_datasave
import itertools
from wav2pcm import removes_silence

path = "audio_file/"    # 录音得到的音频文件夹
audio_vad_file = "audio_vad_file/"      # 切割后的音频文件夹


def audio_vad():
    flag = [x for x in range(1, 200)]    #当200次检测没有语音时，结束检测,结束线程t1,t2和主线程.此参数需保证：确实没人说话；线程t2(语音识别和录入数据库)也结束
    record = moni_record.AudioRecorder(flag)

    while True:
        record.start()
        tmp = record.monitor()
        (frames, flag) = record.record(tmp)
        if frames != [] and len(flag) > 0:
            record.stop()
            nowtime = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
            record_path = path + nowtime + r".wav"  # 以时间命名
            record.write_audio_to_wave(record_path)  # 将声音写入音频文件
            record_file = removes_silence(record_path)  # 音频文件消除时间 >1s 的静音部分
            record_vad.main(record_file)  # 分割生成的音频文件
            # print('语音切割完成时间：%s!' % time.ctime())
        elif frames == [] and len(flag) == 0:
            break


def vadfile_creat():
    import stat
    #初始化切割后的语音存放文件夹（清除文件夹下所有文件）
    def remove_readonly(func, path, _):  # 定义回调函数
        os.chmod(path, stat.S_IWRITE)    #删除文件的只读属性
        func(path)
    if os.path.exists(audio_vad_file):
        shutil.rmtree("/audio_vad_file",onerror=remove_readonly)  #将整个文件夹删除
        os.makedirs(audio_vad_file)  # 创建一个文件夹
    else:
        os.makedirs(audio_vad_file) # 没有文件夹就新建一个

#event = threading.Event()   #创建事件

def vad_asr_store():
    vadfile_creat()
    deal_type_dict = {}
    len_dict_list = []

    while True:
        #try:
        # 更新文件夹，将新生成的（新被切割的）音频文件标记，然后进行语音听写等操作
        getFileListType(audio_vad_file, deal_type_dict)
        # print(deal_type_dict)
        time.sleep(5)
        for deal_file in deal_type_dict:
            if deal_type_dict[deal_file] == 0:
                '''deal_next_function(deal_file)  # 对新文件处理：删除杂音，silent/空音频文件等（后续要加）'''
                file_path = audio_vad_file + deal_file
                filetimestamp = deal_file.split('-')[0]
                res = sound2wordBD.asr_main(file_path)  # 百度语音听写
                #res = sound2wordXF.wordfromS(file_path)  # 讯飞语音听写
                #mu = threading.Lock()  # 1、创建一个锁
                #if mu.acquire():    # 2、获取锁状态，一个线程有锁时，别的线程只能在外面等着
                '''#存入txt文档
                vad_text_file = "vad_test.txt"
                with open(vad_text_file, 'a') as f:
                    if res != None:
                        # text_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
                        f.write(res + '\n')  # 不加锁多线程读写文件会出现错误
                    else:
                        f.write('')'''
                if res!=None:
                    md = mongo_datasave.MongoDBHelper()
                    md.SaveData(filetimestamp,res)  #将生成vad文件的时间戳、得到的语音识别内容，导入数据库
                #mu.release()  # 3、释放锁

                # print("新文件经过处理")
                deal_type_dict[deal_file] = 1  # 并标识处理过的文件
                continue

        print(deal_type_dict)
        len_dict = len(deal_type_dict)
        len_dict_list.append(len_dict)
        len_max_list = max([len(list(v)) for k, v in itertools.groupby(len_dict_list)])
        print(len_max_list)
        if len_max_list > 200:  # 当检测次数达到200仍没有新文件进来，就结束进程
            break
        continue
        #print("标记及处理完毕")
        #event.wait()       #等待set()，后面代码不会立即执行，等set()触发后才继续执行。控制线程有序执行

        #except:
            #print("语音听写写入文件出错")
            #break

threads = []
t1 = threading.Thread(target=audio_vad)
threads.append(t1)
t2 = threading.Thread(target=vad_asr_store)
threads.append(t2)

if __name__ == '__main__':
    t1.start()
    t2.setDaemon(True)
    t2.start()

    for t in threads:
        t.join()

    print("all over %s" % time.ctime())









