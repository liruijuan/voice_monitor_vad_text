import pymongo
from pymongo import MongoClient
import csv
import datetime, time
import sound2wordBD

class MongoDBHelper(object):
    def __init__(self):
        self.InitMongoDBConnect()

    def InitMongoDBConnect(self):
        connection = MongoClient('localhost',27017)
        db = connection['speakerID']
        self.collection =db['customers']

    def CheckData(self,CID):
        datas = self.collection.find({'CID':CID})   #查询是否存在相同的数据
        if datas.count() > 0:
            return True,datas[0]
        else:
            return False,0

    def SaveData(self,filetimestamp,res):

        CID = filetimestamp,
        words_content = res,
        words_feature = "普通话"  # 文言文，诗词，歌曲等

        words_data = {"CID": CID, "content": words_content, "feature": words_feature}
        self.collection.insert(words_data)


if __name__ == '__main__':
    res = sound2wordBD.asr_main("16k.wav")  # 百度语音听写

    if res != None:
         md = MongoDBHelper()
         md.SaveData(res)








