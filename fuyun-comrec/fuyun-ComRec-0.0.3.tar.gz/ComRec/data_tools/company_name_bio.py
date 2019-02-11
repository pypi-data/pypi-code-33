# -*- coding:utf-8 -*-
import argparse
import os,json,pickle
from string import punctuation
from pymongo import MongoClient

parser = argparse.ArgumentParser()
parser.add_argument('--test_data', type=str, default='data_path', help='test data source')
args = parser.parse_args()
## tags, BIO
tag2label = {"O": 0,
             "B-REGION": 1, "I-REGION": 2,
             "B-NAME": 3, "I-NAME": 4,
             "B-DOMAIN": 5, "I-DOMAIN": 6,
             "B-COM_TYPE": 7, "I-COM_TYPE": 8,
             "B-SUB_REGION":9, "I-SUB_REGION":10
             }
add_punc = '，。、【 】 “”：；《》‘’{}？！⑦()、%^>℃：.”“^-——=&#@￥'
all_punc = punctuation + add_punc

def company_name_bio():
    connect=MongoClient("172.19.79.10",27701)
    db2=connect['markingPlatform']
    db2.authenticate("dig","Fh9l15O45m")
    collect=db2.company_name
    j=0
    word2id={}
    number=0
    with open(os.path.join('.', args.train_data, 'train_data_1'), 'w', encoding="utf-8") as wf:
        with open(os.path.join('.', args.test_data, 'word2id_list'), 'w', encoding="utf-8") as wb:
            for item in collect.find():
            #for item in collect.find({"origText":{'$regex':'公司'}}):
                number += 1
                if "9ab505187f34434db93c8b990df21726" in item :
                    data=item["9ab505187f34434db93c8b990df21726"]["annoResults"]
                    context=data["content"]
                    label=data["labels"]
                    tag = []
                    num=[]
                    word2={}
                    for word in context:
                        if word not in word2id:
                            j+=1
                            word2[word]=j
                            word2id[word]=j
                    wb.write((json.dumps(word2, ensure_ascii=False)).replace('{','').replace('}',''))
                    for line in label :
                            if (line["categoryId"]==0):
                                tag.append([context[line["startIndex"]],"B-REGION"])
                                num.append(line["startIndex"])
                                for i in range(line["endIndex"]-line["startIndex"]-1):
                                    num.append(line["startIndex"]+i+1)
                                    tag.append([context[line["startIndex"]+i+1], "I-REGION"])
                            if (line["categoryId"] ==1):
                                tag.append([context[line["startIndex"]],"B-NAME"])
                                num.append(line["startIndex"])
                                for i in range(line["endIndex"]-line["startIndex"]-1):
                                    num.append(line["startIndex"] + i+1)
                                    tag.append([context[line["startIndex"]+i+1], "I-NAME"])
                            if (line["categoryId"] ==2):
                                tag.append([context[line["startIndex"]], "B-DOMAIN"])
                                num.append(line["startIndex"])
                                for i in range(line["endIndex"] - line["startIndex"]-1):
                                    num.append(line["startIndex"] + i+1)
                                    tag.append([context[line["startIndex"] + i+1], "I-DOMAIN"])
                            if (line["categoryId"] ==3):
                                tag.append([context[line["startIndex"]], "B-COM_TYPE"])
                                num.append(line["startIndex"])
                                for i in range(line["endIndex"] - line["startIndex"]-1):
                                    num.append(line["startIndex"] + i+1)
                                    tag.append([context[line["startIndex"] + i+1], "I-COM_TYPE"])
                            if (line["categoryId"] ==4):
                                tag.append([context[line["startIndex"]], "B-SUB_REGION"])
                                num.append(line["startIndex"])
                                for i in range(line["endIndex"] - line["startIndex"]-1):
                                    num.append(line["startIndex"] + i+1)
                                    tag.append([context[line["startIndex"] + i+1], "I-SUB_REGION"])
                            else:
                                continue
                    for a in range(len(context)):
                        if a not in num:
                            print([context[a],"O"])
                            tag.append([context[a], "O"])
                    for i in range(len(tag)):
                        wf.write(tag[i][0])
                        wf.write(" ")
                        wf.write(tag[i][1])
                        wf.write('\n')

if __name__=="__main__":
    company_name_bio()