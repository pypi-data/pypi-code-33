

class GenerateScript:
    """
    类名以接口方法名进行生成，最前面加Test，将首字母大写，其余小写
    如方法名为：/services/dealerFactorySerise/get
    文件名为：test_services_dealerfactoryserise_get.py
    测试类名为：TestServicesDealerfactorySeriesGet
    """

    def __init__(self, scriptname, classname, description):
        self.scriptname = scriptname
        self.classname = classname
        self.description = description

    def generate_script(self):
        """
        生成测试脚本方法
        :return:
        """
        # script_name = "test" + "_".join([name.lower() for name in self.path.split("/")]) + ".py"
        # class_name = "Test" + "".join([name.title() for name in self.path.split("/")])
        # class_description = "这里是类描述"
        script_data = """# coding=utf-8
import unittest
import requests
from base import *

class %(classname)s(InterFaceBaseTest):
    \"\"\"
    %(class_description)s
    \"\"\"

    @classmethod
    def setUpClass(cls, ids=%(ids)d):
        \"\"\"
        向超类传参，如无必要请勿修改
        :param ids: 获取数据的id
        :return:
        \"\"\"
        transfer = {
            "ids": sys.argv[1],
            "env": sys.argv[2]
        }

        super(%(classname)s, cls).setUpClass(ids)
        # do your something
        
    # def setUp(self):
    #     \"\"\"
    #     覆写超类setup
    #     :return:
    #     \"\"\"
    #     super(TestImage, self).setUp()
    #     # do your something

    # ============testcase begin==============
    
    # # write yourself testcase
    # def test_yourself_interface_testcase(self):
    #     \"\"\"
    #     你的接口测试用例描述
    #     :return: 
    #     \"\"\"
    #     pass
    
    
    # ============testcase end==============

    # def tearDown(self):
    #     \"\"\"
    #     覆写超类teardown
    #     :return:
    #     \"\"\"
    #     super(TestImage, self).tearDown()
    #     # do your something

    # @classmethod
    # def tearDownClass(cls):
    #     \"\"\"
    #     向超类传参，如无必要请勿修改
    #     :return:
    #     \"\"\"
    #     # do your something
    #     super(TestImage, cls).tearDownClass()

with BaseRunSuite(%(classname)s): pass

""" % dict(classname=self.classname, class_description=self.description, ids=12)

        print("script_name is : %s " % self.scriptname)
        print("class name is : %s " % self.classname)
        print(script_data)

        with open(self.scriptname, "w", encoding="utf-8") as fp:
            fp.writelines(script_data)


if __name__ == '__main__':
    g = GenerateScript("test_script_name.py", "Test_name", "this is autocreate")
    g.generate_script()
