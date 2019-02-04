# -*- coding:utf-8 -*-
"""
FileName: serverinfo.py
Version: 0.1
Company: cninfo
Author: ruitian.chen
Create Date: 2019-01-25
Description: API服务端信息配置.
History: /*
 create 2019-01-25
 */
"""

"""测试环境,使用该环境需要在调用客户端hosts文件添加该行：  59.40.185.19 pi1.before.com
#测试环境'http://api1.before.com:9091'
#正式环境'http://webapi.cninfo.com.cn'"""
API_SERVER_URL = 'http://api1.before.com:9091'
API_TOKEN_PATH = '/api-cloud-platform/oauth2/token'
API_INFO_PATH = '/api/sysapi/sysapi'  #API元数据信息获取路径




"""******公共参数
序号	参数	描述
1	@column	结果列选择 选择结果集中所需要的字段，多列用逗号分隔，如@column=a,b
2	@limit	结果条数限制 设置结果返回的条数 如@limit=10
3	@orderby	结果集排序 设置结果集的排序规则，示例：@orderby A desc或者 @orderby A asc 或者 @orderby A,B desc
4	Format	Format 返回格式,共返回四种格式，JSON，XML，CSV，DBF；默认为JSON，如：format=xml

返回示例说明
序号	返回字段	字段含义
1	total	总条数
2	count	本次请求返回条数
3	resultmsg	成功标识 success：成功
4	resultcode	返回状态码，具体参照下面错误码表格
5	records	数据内容

错误码参考
序号	错误码	描述
1	-1	系统繁忙，此时请开发者稍候再试
2	200	success
3	401	未经授权的访问
4	402	不合法的参数
5	403	脚本服务器异常
6	404	token 无效
7	405	token过期
8	406	用户已被禁用
9	407	免费试用次数已用完
10	408	用户没有余额
11	409	验证权限错误
12	410	验证权限异常
13	411	获取用户信息失败
14	412	包时长已超期
"""