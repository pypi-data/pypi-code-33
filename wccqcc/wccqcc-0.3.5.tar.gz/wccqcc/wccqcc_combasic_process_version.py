"""
企查查的爬虫
"""
import os
import re
import time
import json
import requests
from lxml import etree
from tqdm import tqdm
import pymongo
import wcc
import random
import jsonfiler
import pmt
from bs4 import BeautifulSoup
import traceback
import comcom
from .getpage import getpage
import multiprocessing
def get_gsinfo(url,resp_text):
    if not resp_text: return None
    """
    如果url是gs_，则在这个方法中处理
    页面元素参考 https://www.qichacha.com/gs_1473977081543754269
    """
    try:
        html = etree.HTML(resp_text)
        item = {}
        # 公司名
        if html.xpath('//span[@class="clear"]/span[1]//text()'):
            item['name'] = html.xpath('//span[@class="clear"]/span[1]//text()')[0]
        else:
            item['name'] = ""
        # 统一社会信用代码 
        # 用code代表信用代码
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "统一社会信用代码")]/..//text()'):
            item['code'] = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "统一社会信用代码")]/..//text()')[1]
        else:
            item['code'] = ""
        # 注册号
        # 有的公司,"统一社会信用代码"和"注册号"可以同时存在.参考 https://www.qichacha.com/gs_1478515181544192110
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "注册号")]/..//text()'):
            item['code_reg'] = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "注册号")]/..//text()')[1]
        else:
            item['code_reg'] = ""

        # 经营状态
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "经营状态")]/..//text()'):
            item['status'] = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "经营状态")]/..//text()')[1]
        else:
            item['status'] = ""
        # 公司类型
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "公司类型")]/..//text()'):
            item['type'] = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "公司类型")]/..//text()')[1]
        else:
            item['type'] = ""
        # 成立日期
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "成立日期")]/..//text()'):
            item['date_est'] = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "成立日期")]/..//text()')[1]
        else:
            item['date_est'] = ""
        # 法定代表人, 需要修改字段名
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "法定代表")]/..//text()'):
            legalp = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "法定代表")]/..//text()')[2]
        else:
            legalp = ""
        item['legalp'] = legalp.strip() if legalp else ""
        # 注册资本
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "注册资本")]/..//text()'):
            item['capital_reg'] = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "注册资本")]/..//text()')[1]
        else:
            item['capital_reg'] = ""
        # 营业期限
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "营业期限")]/..//text()'):
            item['validity'] = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "营业期限")]/..//text()')[1]
        else:
            item['validity'] = ""
        # 登记机关
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "登记机关")]/..//text()'):
            item['issuer'] = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "登记机关")]/..//text()')[1]
        else:
            item['issuer'] = ""
        # 发照日期
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "发照日期")]/..//text()'):
            item['date_aprv'] = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "发照日期")]/..//text()')[1]
        else:
            item['date_aprv'] = ""
        # 企业地址
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "企业地址")]/..//text()'):
            item['addr'] = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "企业地址")]/..//text()')[2]
        else:
            item['addr'] = ""
        # 经营范围
        if html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "经营范围")]/..//text()'):
            scope = html.xpath('//ul[@class="company-base"]//li/label[contains(text(), "经营范围")]/..//text()')[2]
        else:
            scope = ""
        item['tel'] = ""
        item['bank'] = ""
        item['account'] = ""
        item['scope'] = scope.strip() if scope else ""
        # 信息来源
        item['from'] = '企查查gs'
        # 获取信息的时间
        item['ctime'] = int(time.time())
        # 信源的url
        item['url'] = url
        # 信源页面快照
        url_part = url.replace("https://www.qichacha.com/","").replace(".html","")
        item['html'] = wcc.uploadHtml(resp_text,url=url_part)
        return item
    except Exception as err:
        print(traceback.format_exc())
        print(url+" err bs "+str(err))
        return None

def get_firminfo(url,resp_text):
    if not resp_text: return None
    soup = None
    try:
        html = etree.HTML(resp_text)
        soup = BeautifulSoup(resp_text,"html.parser")
        item = {}
        # 公司名,firm页面的公司名确实不同的网页有不同的写法
        """
        https://www.qichacha.com/firm_d5a788511649fbf2e472c05d48d5be5f.html#base
        便是 <div class="row title jk-tip">
                <h1>固原地震台招待所</h1> 
        """

        """
        https://www.qichacha.com/firm_44a28adbedaf8245d0d3043fcf295ee9.html#base
        <div class="content"> 
            <div class="row title" style="margin-top: -2px;margin-bottom: 10px;">贺兰县富兴南街风格秀服装店
        """
        com_name_xpath1 = '//div[@class="content"]/div[@class="row title jk-tip"]/h1/text()'
        com_name_xpath2 = '//div[@class="content"]/div[@class="row title"]/h1/text()'
        com_name_xpath3 = '//div[@class="content"]/div[@class="row title"]//text()'
        if html.xpath(com_name_xpath1):
            com_name = html.xpath(com_name_xpath1)[0]
        elif html.xpath(com_name_xpath2):
            com_name = html.xpath(com_name_xpath2)[0]
        elif html.xpath(com_name_xpath3):
            com_name = html.xpath(com_name_xpath3)[0]
        else:
            com_name = ""
        if com_name == "":
            print(html)
            raise Exception(url+" html match no com name")
        item["name"] = com_name
        legalp_name = ""
        # 法人名
        # 有些个体户根本没有seo,例如:https://www.qichacha.com/cbase_4d8b7f1d12b71a8b6008bc1a3cf505b8.html
        try:
            legalp_name = soup.select(".seo")[0].text.strip()
        except Exception as err:
            try:
                legalp_name = soup.select(".boss-td")[0].text.strip()
            except Exception as err:
                raise Exception(url+" 找不到法人")
        item["legalp"] = legalp_name 
        #######################     上面部分信息      ##############################
        # 官网
        if html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "官网")]/following-sibling::*[1]//a/@href'):
            item['site'] = html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "官网")]/following-sibling::*[1]//a/@href')[0].strip()
        elif html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "官网")]/following-sibling::*[1]//text()'):
            item['site'] = html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "官网")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['site'] = ''
        # 邮箱
        if html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "邮箱")]/following-sibling::*[1]//a//text()'):
            item['email'] = html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "邮箱")]/following-sibling::*[1]//a//text()')[0].strip()
        else:
            item['email'] = ''
        # 简介
        if html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "简介")]/following-sibling::*[1]//text()'):
            item['intro'] = html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "简介")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['intro'] = ""
        #######################     上面部分信息      ##############################

        #######################     下面部分信息      ##############################
        # 注册资本
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "注册资本")]/following-sibling::*[1]//text()'):
            item['capital_reg'] = html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "注册资本")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['capital_reg'] = ""
        # 实缴资本
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "实缴资本")]/following-sibling::*[1]//text()'):
            item['capital_paid'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "实缴资本")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['capital_paid'] = ""
        # 经营状态
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "经营状态")]/following-sibling::*[1]//text()'):
            item['status'] = html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "经营状态")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['status'] = ""
        # 成立日期
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "成立日期")]/following-sibling::*[1]//text()'):
            item['date_est'] = html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "成立日期")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['date_est'] = ""
        # 统一社会信用代码
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "统一社会信用代码")]/following-sibling::*[1]//text()'):
            item['code'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "统一社会信用代码")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['code'] = ""
        # 纳税人识别号
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "纳税人识别号")]/following-sibling::*[1]//text()'):
            item['code_tax'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "纳税人识别号")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['code_tax'] = ""
        # 注册号
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "注册号")]/following-sibling::*[1]//text()'):
            item['code_reg'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "注册号")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['code_reg'] = ""
        # 组织机构代码
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "组织机构代码")]/following-sibling::*[1]//text()'):
            item['code_org'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "组织机构代码")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['code_org'] = ""
        # 公司类型
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "公司类型")]/following-sibling::*[1]//text()'):
            item['type'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "公司类型")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['type'] = ""
        # 所属行业
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "所属行业")]/following-sibling::*[1]//text()'):
            item['industry'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "所属行业")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['industry'] = ""
        # 核准日期
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "核准日期")]/following-sibling::*[1]//text()'):
            item['date_aprv'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "核准日期")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['date_aprv'] = ""
        # 登记机关
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "登记机关")]/following-sibling::*[1]//text()'):
            item['issuer'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "登记机关")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['issuer'] = ""
        # 所属地区
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "所属地区")]/following-sibling::*[1]//text()'):
            item['district'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "所属地区")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['district'] = ""
        # 英文名
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "英文名")]/following-sibling::*[1]//text()'):
            item['name_en'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "英文名")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['name_en'] = ""
        # 曾用名
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "曾用名")]/following-sibling::*[1]//span/text()'):
            name_used = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "曾用名")]/following-sibling::*[1]//span/text()')
        else:
            name_used = ""
        item['name_used'] = ""
        for i in name_used:
            item['name_used'] += i.strip()
        # 参保人数
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "参保人数")]/following-sibling::*[1]//text()'):
            item['cbrs'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "参保人数")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['cbrs'] = ""
        # 人员规模
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "人员规模")]/following-sibling::*[1]//text()'):
            item['staff'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "人员规模")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['staff'] = ""
        # 营业期限
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "营业期限")]/following-sibling::*[1]//text()'):
            item['validity'] = html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "营业期限")]/following-sibling::*[1]//text()')[0].strip().replace(" ", "")
        else:
            item['validity'] = ""
        # 企业地址
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "企业地址")]/following-sibling::*[1]//text()'):
            item['addr'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "企业地址")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['addr'] = ""
        # 经营范围
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "经营范围")]/following-sibling::*[1]//text()'):
            item['scope'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "经营范围")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['scope'] = ""

        #######################     右下角的信息      ##############################
        if not url.endswith(".html"):
            print(url + " not ends with .html")
            return None
        firm = str(re.findall("cbase_(.*?).html", url)[0])
        api_url = 'https://www.qichacha.com/tax_view?keyno=' + firm + '&ajaxflag=1'
        data = None
        """
        #为加快爬取速度,我们不从这个接口获取信息了
        try:
            data_text = getpage(api_url,max_try=50,timeout=30)
            data_json = json.loads(data_text)
            data = data_json['data']
        except Exception as err:
            print(traceback.format_exc())
            print(err)
            data = None
        """
        if data:
            # 电话
            if 'PhoneNumber' in data:
                item['tel'] = data['PhoneNumber']
            else:
                item['tel'] = ""
            # 开户银行
            if 'Bank' in data:
                item['bank'] = data['Bank']
            else:
                item['bank'] = ""
            # 银行账户
            if 'Bankaccount' in data:
                item['account'] = data['Bankaccount']
            else:
                item['account'] = ""
        else:
            item['tel'] = ""
            item['bank'] = ""
            item['account'] = ""
        if 'tel' not in item:
            item['tel'] = ""
        elif not item['tel']:
            item['tel'] = ""
        if 'bank' not in item:
            item['bank'] = ""
        elif not item['bank']:
            item['bank'] = ""
        if 'account' not in item:
            item['account'] = ""
        elif not item['account']:
            item['account'] = ""
        # 信息来源
        item['from'] = '企查查cbase'
        # 获取信息的时间
        item['ctime'] = int(time.time())
        # 信源的url
        item['url'] = url
        # 信源页面快照
        url_part = url.replace("https://www.qichacha.com/","").replace(".html","").replace(".shtml","")
        item['html'] = wcc.uploadHtml(resp_text,url=url_part)
        return item
    except Exception as err:
        print(traceback.format_exc())
        print(url+" err firm sec345 "+str(err))
        #有些firm 是社会组织，结构和企业不一样，社会组织读取法人就读取不到
        #https://www.qichacha.com/firm_s27c65101960060e65d0a975ca503e19.html
        return None
#获取社会组织的信息
def get_orginfo(url,resp_text):
    if not resp_text: return None
    soup = None
    try:
        html = etree.HTML(resp_text)
        soup = BeautifulSoup(resp_text,"html.parser")
        item = {}
        # 公司名,firm页面的公司名确实不同的网页有不同的写法
        """
        https://www.qichacha.com/firm_d5a788511649fbf2e472c05d48d5be5f.html#base
        便是 <div class="row title jk-tip">
                <h1>固原地震台招待所</h1> 
        """

        """
        https://www.qichacha.com/firm_44a28adbedaf8245d0d3043fcf295ee9.html#base
        <div class="content"> 
            <div class="row title" style="margin-top: -2px;margin-bottom: 10px;">贺兰县富兴南街风格秀服装店
        """
        com_name_xpath1 = '//div[@class="content"]/div[@class="row title jk-tip"]/h1/text()'
        com_name_xpath2 = '//div[@class="content"]/div[@class="row title"]/h1/text()'
        com_name_xpath3 = '//div[@class="content"]/div[@class="row title"]//text()'
        com_name = ""
        if html.xpath(com_name_xpath1):
            com_name = html.xpath(com_name_xpath1)[0]
        elif html.xpath(com_name_xpath2):
            com_name = html.xpath(com_name_xpath2)[0]
        elif html.xpath(com_name_xpath3):
            com_name = html.xpath(com_name_xpath3)[0]
        else:
            com_name = ""
        if com_name == "":
            raise Exception(url+" html match no com name")
        item["name"] = com_name
       
        # 法人名
        legalp_xpath = '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "法人/负责人")]/following-sibling::*[1]//text()'
        if html.xpath(legalp_xpath):
            item['legalp'] = html.xpath(legalp_xpath)[0].strip()
        else:
            item['legalp'] = ""
 
        #######################     上面部分信息      ##############################
        # 官网
        if html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "官网")]/following-sibling::*[1]//a/@href'):
            item['site'] = html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "官网")]/following-sibling::*[1]//a/@href')[0].strip()
        elif html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "官网")]/following-sibling::*[1]//text()'):
            item['site'] = html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "官网")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['site'] = ''
        # 邮箱
        if html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "邮箱")]/following-sibling::*[1]//a//text()'):
            item['email'] = html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "邮箱")]/following-sibling::*[1]//a//text()')[0].strip()
        else:
            item['email'] = ''
        # 简介
        if html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "简介")]/following-sibling::*[1]//text()'):
            item['intro'] = html.xpath('//div[@class="content"]/div[@class="row"]//span[contains(text(), "简介")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['intro'] = ""
        #######################     上面部分信息      ##############################

        #######################     下面部分信息      ##############################
        # 注册资本
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "注册资本")]/following-sibling::*[1]//text()'):
            item['capital_reg'] = html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "注册资本")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['capital_reg'] = ""
        # 实缴资本（社会组织好像没有,这里写着）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "实缴资本")]/following-sibling::*[1]//text()'):
            item['capital_paid'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "实缴资本")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['capital_paid'] = ""
        # 登记状态
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "登记状态")]/following-sibling::*[1]//text()'):
            item['status'] = html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "登记状态")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['status'] = ""
        # 成立日期
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "成立日期")]/following-sibling::*[1]//text()'):
            item['date_est'] = html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "成立日期")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['date_est'] = ""
        # 统一社会信用代码
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "统一社会信用代码")]/following-sibling::*[1]//text()'):
            item['code'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "统一社会信用代码")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['code'] = ""
        # 纳税人识别号（社会组织没有，此地保留）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "纳税人识别号")]/following-sibling::*[1]//text()'):
            item['code_tax'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "纳税人识别号")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['code_tax'] = ""
        # 注册号（社会组织没有，此地保留）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "注册号")]/following-sibling::*[1]//text()'):
            item['code_reg'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "注册号")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['code_reg'] = ""
        # 组织机构代码（社会组织没有，此地保留）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "组织机构代码")]/following-sibling::*[1]//text()'):
            item['code_org'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "组织机构代码")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['code_org'] = ""
        # 组织类型()
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "社会组织类型")]/following-sibling::*[1]//text()'):
            item['type'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "社会组织类型")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['type'] = ""
        # 所属行业（社会组织没有，此地保留）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "所属行业")]/following-sibling::*[1]//text()'):
            item['industry'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "所属行业")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['industry'] = ""
        # 核准日期（社会组织没有，此地保留）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "核准日期")]/following-sibling::*[1]//text()'):
            item['date_aprv'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "核准日期")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['date_aprv'] = ""
        # 登记机关
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "登记机关")]/following-sibling::*[1]//text()'):
            item['issuer'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "登记机关")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['issuer'] = ""
        # 所属地区（社会组织没有，此地保留）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "所属地区")]/following-sibling::*[1]//text()'):
            item['district'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "所属地区")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['district'] = ""
        # 英文名（社会组织没有，此地保留）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "英文名")]/following-sibling::*[1]//text()'):
            item['name_en'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "英文名")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['name_en'] = ""
        # 曾用名（社会组织没有，此地保留）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "曾用名")]/following-sibling::*[1]//span/text()'):
            name_used = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "曾用名")]/following-sibling::*[1]//span/text()')
        else:
            name_used = ""
        item['name_used'] = ""
        for i in name_used:
            item['name_used'] += i.strip()
        # 参保人数（社会组织没有，此地保留）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "参保人数")]/following-sibling::*[1]//text()'):
            item['cbrs'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "参保人数")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['cbrs'] = ""
        # 人员规模（社会组织没有，此地保留）
        if html.xpath('//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "人员规模")]/following-sibling::*[1]//text()'):
            item['staff'] = html.xpath(
                '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "人员规模")]/following-sibling::*[1]//text()')[0].strip()
        else:
            item['staff'] = ""
        # 证书有效期
        validity_xpath = '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "证书有效期")]/following-sibling::*[1]//text()'
        if html.xpath(validity_xpath):
            item['validity'] = html.xpath(validity_xpath)[0].strip().replace(" ", "")
        else:
            item['validity'] = ""
        # 企业地址
        addr_xpath = '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "住所")]/following-sibling::*[1]//text()'
        if html.xpath(addr_xpath):
            item['addr'] = html.xpath(addr_xpath)[0].strip()
        else:
            item['addr'] = ""
        # 经营范围
        scope_xpath =  '//section[@id="Cominfo"]//table[@class="ntable"]//td[contains(text(), "业务范围")]/following-sibling::*[1]//text()'
        if html.xpath(scope_xpath):
            item['scope'] = html.xpath(scope_xpath)[0].strip()
        else:
            item['scope'] = ""

        if 'tel' not in item:
            item['tel'] = ""
        elif not item['tel']:
            item['tel'] = ""
        if 'bank' not in item:
            item['bank'] = ""
        elif not item['bank']:
            item['bank'] = ""
        if 'account' not in item:
            item['account'] = ""
        elif not item['account']:
            item['account'] = ""
        # 信息来源
        item['from'] = '企查查cbase'
        # 获取信息的时间
        item['ctime'] = int(time.time())
        # 信源的url
        item['url'] = url
        # 信源页面快照
        url_part = url.replace("https://www.qichacha.com/","").replace(".html","").replace(".shtml","")
        item['html'] = wcc.uploadHtml(resp_text,url=url_part)
        return item
    except Exception as err:
        print(traceback.format_exc())
        print(url+" err org "+str(err))
        #有些firm 是社会组织，结构和企业不一样，社会组织读取法人就读取不到
        #https://www.qichacha.com/firm_s27c65101960060e65d0a975ca503e19.html
        return None



def combasic_thread_func(url, addinfo):
    try:
        cur_time = int(time.time())
        resp_text = getpage(url,max_try=30)
        if not resp_text:
            print(url+" none")
            addinfo["except"]+=1
            return None
        item = None
        if "gs_" in url:
            item = get_gsinfo(url,resp_text)
        elif "cbase_" in url:
            if "社会组织类型" in resp_text and "法人/负责人" in resp_text:
                item = get_orginfo(url,resp_text)
            else:
                item = get_firminfo(url,resp_text)
        if not item: return None
        if comcom.is_combasic(item):
            addinfo_done = comcom.add_combasic([item])
            try:
                addinfo["insert"]+=addinfo_done[0]
                addinfo["update"]+=addinfo_done[1]
                addinfo["ignore"]+=addinfo_done[2]
                addinfo["except"]+=addinfo_done[3]
            except Exception as err:
                print(err)
            print(url+" ok "+str(addinfo_done))
        else:
            addinfo["except"]+=1
            print(url+" error")
    except Exception as err:
        addinfo["except"]+=1
        print(traceback.format_exc())
        print(err)
    return None

def decide_best_threads():
    return 50
def decide_best_threads2():
    #初始化是10个线程
    #经验发现,入股每个进程的初始化线程太多,会导致异常的获取数大大增加.所以设为20
    #设为50时有一般的例外概率
    INIT_THREAD_N = 20
    random_thread_count_modify = 1 if random.random()*10 > 5 else -1
    if addinfo_list == [] or len(addinfo_list) < 2 :
        return INIT_THREAD_N + random_thread_count_modify
    #如果大于10，需要重新计算要不要提高线程数,每次增加1
    k0 = addinfo_list.pop()
    k1 = addinfo_list.pop()
    try:
        if k0["tps"] > k1["tps"] and k0["threads"] > k1["threads"]:return k0["threads"] + 5
        if k0["tps"] > k1["tps"] and k0["threads"] < k1["threads"]:return k0["threads"] - 1
        if k0["tps"] > k1["tps"] and k0["threads"] ==k1["threads"]:return k0["threads"] + random_thread_count_modify
        if k0["tps"] < k1["tps"] and k0["threads"] > k1["threads"]:return k0["threads"] - 1
        if k0["tps"] < k1["tps"] and k0["threads"] < k1["threads"]:return k0["threads"] + 5
        if k0["tps"] < k1["tps"] and k0["threads"] ==k1["threads"]:return k0["threads"] + random_thread_count_modify
    except Exception as err:
        return INIT_THREAD_N + random_thread_count_modify
    return k0["threads"] + random_thread_count_modify 

def wccqcc_combasic(life=300):
    try:
        pmc_file_name = "wccqcc_combasic_pmc.json"
        start_time = int(time.time())
        addinfo = {"total":0,"insert":0,"update":0,"ignore":0,"except":0,"threads":0}
        """
        获取数据库连接
        """
        env_dict = os.environ
        mongo_data_uri = env_dict["MONGO_DAT_URI"]
        client = pymongo.MongoClient(mongo_data_uri)
        db = client["comdb"]
        col_combasic = db["combasic"]
        col_firmkeys = db["firmkeys"]
       
        THREAD_N = decide_best_threads()
        insert_count = 0
        update_count = 0
        ignore_count = 0
        except_count = 0

        pool = multiprocessing.Pool(processes=THREAD_N)    # set the processes max number 3
        for k in range(THREAD_N):
            cur_time = int(time.time())
            if cur_time - start_time > life:break
            dbrow = col_firmkeys.find_one_and_update({"basic":0}, {"$set":{"basic":cur_time}})
            if not dbrow:
                print("found none urls")
                break
            url = dbrow["url"]
            url = "https://www.qichacha.com/cbase_"+url+".html"           
            if col_combasic.find_one({"url":url}):
                addinfo["ignore"]+=1
                continue
            addinfo["total"]+=1
            pool.apply_async(combasic_thread_func, (url,addinfo))
        print("pool close")
        pool.close()
        pool.join()
        
        start_time = int(time.time())
        timestr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        addinfo["lot"] = int(time.time()) - start_time
        addinfo["threads"] = THREAD_N
        addinfo["time"] = int(time.time())
        addinfo["cnt"] = 1
        addinfo["tps"] = addinfo["total"]/addinfo["lot"]
        thread_result_print = {
            "time":timestr,
            "lot":int(time.time()) - start_time,
            "threads":str(addinfo["err_threads"])+"/"+str(addinfo["threads"])+"/"+str(THREAD_N),
            "insert":str(addinfo["total"])+"="+str(addinfo["insert"])+"|"+str(addinfo["update"])+"|"+str(addinfo["ignore"])+"|"+str(addinfo["except"]),
        }
        print(thread_result_print)
        try:
            addinfo_list = jsonfiler.load(pmc_file_name)
            if not addinfo_list:
                addinfo_list = []
            #pop() 接收的是索引，无参的情况下删除的是最后一个元素（典型的栈的特性）
            if addinfo_list ==[]:
                addinfo_list.append(addinfo)
            else:
                addinfo_old = addinfo_list.pop()
                if addinfo["time"] - addinfo_old["time"]  < 600:
                    addinfo_old["total"] +=addinfo["total"]
                    addinfo_old["insert"] +=addinfo["insert"]
                    addinfo_old["update"] +=addinfo["update"]
                    addinfo_old["ignore"] +=addinfo["ignore"]
                    addinfo_old["except"] +=addinfo["except"]
                    addinfo_old["lot"]    = int ((addinfo_old["cnt"] * addinfo_old["lot"] +addinfo["lot"])/(addinfo_old["cnt"]+1))
                    addinfo_old["cnt"]    +=1
                    addinfo_old["tps"]    = addinfo_old["total"]/addinfo_old["lot"]
                    addinfo_list.append(addinfo_old)
                else:
                    addinfo_list.append(addinfo)
            jsonfiler.dump(addinfo_list,pmc_file_name,indent=4)
        except Exception as err:
            print(err)
    except Exception as err:
        print(traceback.format_exc())
        print("thread exception:"+str(err))
        return None
 
 
if __name__ == "__main__":
    url = "https://www.qichacha.com/cbase_s27c65101960060e65d0a975ca503e19.html"
    url = "https://www.qichacha.com/cbase_5695f448fa15f5571fcc8203544ffdd5.html"
    url = "https://www.qichacha.com/cbase_0d5e802ee19800d981c01dc204a77fba.html"
    resp_text = getpage(url,max_try=30)
    print(resp_text)
    com = get_firminfo(url,resp_text)
    print(com)
