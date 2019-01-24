import time


class man(object):
    def __init__(self, __session):
        self.__session = __session

    def getUserId(self, username):
        """
        转换名字为id
        :param username:
        :return:
        """
        classmates = self.getClassManage()[0]
        for classmate in classmates:
            if classmate["name"] == username:
                return classmate["id"]
        return False

    def getClassManage(self):
        """
        返回班级里学生列表和朋友列表
        :param self:
        :return:
        """
        classmates = []
        friends = []
        data = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/friendmanage/?d=%d" % int(time.time()))
        data = data.json()
        # 学生列表
        for i in data["studentList"]:
            classmates.append({"userName": i["name"], "userId": i["id"]})
        # 朋友列表
        for i in data["friendList"]:
            friends.append({"userName": i["friendName"], "userId": i["friendId"]})
        return [classmates, friends]

    def inviteFriend(self, userid):
        """
        邀请朋友
        :param userid:用户id
        :return:
        """
        p = {
            "friendId": userid,
            "isTwoWay": "true"
        }
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/addFriend/?d=%d" % int(time.time()), params=p)
        json = r.json()
        print(json)
        if json["result"] == "success":
            return True
        elif json["message"] == "已发送过邀请，等待对方答复":
            return "Yes"
        else:
            return False

    def removeFriend(self, userid):
        """
        删除朋友
        :param userid:用户id可以通过getUserId获取
        :return:
        """
        p = {"friendId": userid}
        r = self.__session.get("http://www.zhixue.com/zhixuebao/zhixuebao/delFriend/?d=%d" % int(time.time()), params=p)
        if r.json()["result"] != "success":
            return False
        else:
            return True
