# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
from collections import defaultdict
import re


class LabelTool(object):

    def __init__(self,
                 uri='mongodb://scrapy:scrapy123$@192.168.1.253:27017/?authSource=admin&authMechanism=MONGODB-CR',
                 database='TBT_SPS',
                 collection='tbt_sps_information'):

        client = MongoClient(uri)
        db = client[database]
        self.collection = db[collection]

    def label_ner(self,
                  cols=None,
                  skip=0,
                  tags=None,
                  sep='\t',
                  output='./train.txt'):
        col_filter = defaultdict(int)
        if cols is None:
            cols = ['title', 'main_body']
        for col in cols:
            col_filter[col] = 1

        if tags is None:
            tags = ['PRO']

        count = skip
        for item in self.collection.find({}, col_filter)[skip:]:
            text = ""
            for col in cols:
                text += item[col] + '\n'
            print("Doc " + str(count) + "：\n")
            print(text)

            offsets = []
            for tag in tags:
                entity_str = input("输入你从文中发现的" + tag + "实体，以逗号分隔：")
                entities = str(entity_str).split(',')
                for entity in entities:
                    for occur in re.finditer(entity, text):
                        offsets.append([tag, occur.span()])
            training_set = ""
            pos = 0
            for char in text:
                if char != ' ':
                    flag = 0
                    for span in offsets:
                        if span[1][1] > pos >= span[1][0]:
                            if pos == span[1][0]:
                                training_set += char + sep + 'B-' + span[0] + '\n'
                                flag = 1
                            else:
                                training_set += char + sep + 'I-' + span[0] + '\n'
                                flag = 1
                            break
                        else:
                            continue
                    if flag == 0:
                        training_set += char + sep + 'O' + '\n'
                    pos += 1
            with open(output, "a", encoding="utf-8") as training_file:
                training_file.write(training_set + "\n")
            count += 1
            print("\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")


