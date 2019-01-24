import re
import os
import random
from json import loads
from .models import *


class exam(object):
    def __init__(self, __session):
        self.__session = __session

    def getStudentId(self, name):
        """
        获取指定名称的学生的id
        Ps. 只能获得本班学生的id
        :param name:
            当name为int时,返回它本身
        :return:
        """
        try:
            return int(name)
        except:
            pass
        from .man import man
        man = man(self.__session)
        classmates = man.getClassManage()[0]
        for classmate in classmates:
            if classmate["name"] == name:
                return classmate['id']
        return ""

    def getExamId(self, name=None):
        """
        把考试名字转换为考试id
        :param name:
            当name本身就是id，直接返回它本身
            name为空则返回最新考试id
        :return:
        """
        if name and "-" in name: return name
        examNames = self.getExamNames()
        if name is None:
            return list(examNames.values())[0]
        elif name in examNames:
            return examNames[name]

    def getExamNames(self):
        """
        获取所有考试信息
        :return:
        """
        examNames = {}
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/main/viewAll/?scope=report")
        temp = re.findall(r'examMap = ({.+?}})', r.text.strip())[0]
        for one in loads(temp)["examList"]:
            examId = one["examId"]
            examName = one["examName"]
            examNames[examName] = examId
        return examNames

    def getSelfGrade(self, data=None):
        """
        获取成绩
        :param data:
            考试id或名称,为空则取最新考试id
        :return:
        """
        grades = dict()
        examId = self.getExamId(data)
        data = self.__session.get(
            "http://www.zhixue.com/zhixuebao/zhixuebao/feesReport/getStuSingleReportDataForPK/",
            params={
                "examId": examId,
                "random": random.random()
            }
        ).json()["singleData"]

        grades["examName"] = data[0]["examName"]
        u = len(data)
        for i in range(u):
            subjectName = data[i]["subjectName"]
            grades[subjectName] = subjectDataModel(**{
                "score": data[i]["score"],
                "classRank": classDataModel(**{
                    "avgScore": data[i]['classRank']['avgScore'],
                    "highScore": data[i]['classRank']['highScore'],
                    "rank": data[i]['classRank']['rank']
                }),
                "gradeRank": gradeDataModel(**{
                    "avgScore": data[i]['gradeRank']['avgScore'],
                    "highScore": data[i]['gradeRank']['highScore']
                })
            })
        return grades

    """
    def getGrade(self, examdata, name):
        examId = self.id_name(examdata, "exam")
        userId = self.getStudentId(name)
        self._setUserPkcount(examId)
        if not userId:
            return "你输入的名字不存在"
        json = {
            "examId": examId,
            "random": random.random(),
            "pkId": userId
        }
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/personal/studentPkData/", params=json,
                               data=json, json=json)
        return r.json()[1]
    """

    def getallOriginal(self, data):
        """
        获得所有学科原卷
        :param data:考试id或名称
        :return: {"学科":[...],...}
        """
        imageurls = {}
        examid = self.getExamId(data)

        def getoneimg(paperid, subject):
            imageurls[subject] = []
            data = {
                "paperId": paperid,
                "examId": examid
            }
            r = self.__session.get("http://www.zhixue.com/zhixuebao/checksheet/", params=data)
            image = loads(re.findall(r"sheetImages = (\[.+?\])", r.text)[0])
            imageurls[subject] = image

        data = {
            "examId": examid,
            "isHomework": "false",
            "random": random.random()
        }
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/main/getUserExamDataList/", params=data)
        json = r.json()
        r.close()
        paperids = []
        subjects = []
        for one in json["userExamDataList"][1:]:
            paperid = one["paperId"]
            subject = one["subjectName"]
            paperids.append(paperid[:])
            subjects.append(subject[:])
        for paperid, subject in zip(paperids, subjects):
            getoneimg(paperid, subject)
        return imageurls

    def __getpaperid(self, examid, subject):
        """
        获得指定考试id和学科的paperid
        :param subject:学科
        :param data:考试id或名称
        :return:
         """
        paperid = False
        data = {
            "examId": examid,
            "isHomework": "false",
            "random": random.random()
        }
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/main/getUserExamDataList/", params=data)
        json = r.json()
        r.close()
        for one in json["userExamDataList"]:
            if one["subjectName"] == subject:
                paperid = one["paperId"]
                break
        return paperid

    def getOriginal(self, subject, data=None, file_dir=None):
        """
        获得指定考试id或名称和学科的原卷地址
        :param subject:学科
        :param data:考试id或名称
        :param file_dir:
            如果 file_dir 为真或目录名, 则保存原卷至指定目录下
            当 file_dir 为真时, 则保存到当前目录下
        :return:
        """
        examid = self.getExamId(data)
        paperid = self.__getpaperid(examid, subject)
        if not paperid:
            return False
        data = {
            "paperId": paperid,
            "examId": examid
        }
        r = self.__session.get("http://www.zhixue.com/zhixuebao/checksheet/", params=data)
        imageurls = loads(re.findall(r"sheetImages = (\[.+?\])", r.text)[0])
        if file_dir is True: file_dir = "./"
        if file_dir:
            for imageurl in imageurls:
                with open(os.path.join(file_dir, imageurl.split("/")[-1]), "wb") as f:
                    f.write(self.__session.get(imageurl).content)
        return imageurls

    def _setUserPkcount(self, examId):
        data = {
            "examId": examId,
            "random": random.random()
        }
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/main/getUserPKCount/", params=data)
        data["pkCount"] = int(r.text) - 1
        data["random"] = random.random()
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/main/updateUserPKCount/", params=data)
        print(r.text)
