import base64
import requests
import ybc_config
import sys
from io import BytesIO
from PIL import Image
from ybc_exception import *
import imghdr

__FONT = 'NotoSansCJK-Bold.ttc'
__PREFIX = ybc_config.config['prefix']
__CUT_URL = __PREFIX + ybc_config.uri + '/jieba'
__WC_URL = __PREFIX + ybc_config.uri + '/wordCloud'


def cut(text):
    """
    功能：返回分词之后的列表

    参数：text: 用于进行分词的文本

    返回：
        success: list 划分的分词后文本
        failed: -1 包括传入空串的情况
    """
    err_msg = "'text'"
    if not isinstance(text, str):
        raise ParameterTypeError(function_name=sys._getframe().f_code.co_name, error_msg=err_msg)
    if text == "":
        raise ParameterValueError(function_name=sys._getframe().f_code.co_name, error_msg=err_msg)

    try:
        data = {'text': text}
        url = __CUT_URL

        for i in range(3):
            r = requests.post(url, data=data)
            if r.status_code == 200:
                res = r.text.split('/')
                return res
        raise ConnectionError('分词服务连接失败')
    except Exception as e:
        raise InternalError(e, 'ybc_wordcloud')


def cut2str(text):
    """
    功能：返回切分之后的字符串

    参数：text: 用于进行分词的文本

    返回：
        success: string，分词使用空格划分
        failed: -1 包括传入空串的情况
    """
    err_msg = "'text'"
    if not isinstance(text, str):
        raise ParameterTypeError(function_name=sys._getframe().f_code.co_name, error_msg=err_msg)
    if text == "":
        raise ParameterValueError(function_name=sys._getframe().f_code.co_name, error_msg=err_msg)

    try:
        res = cut(text)
        return ' '.join(res)
    except Exception as e:
        raise InternalError(e, 'ybc_wordcloud')


def wordcloud(text, bgfile='', bgcolor='white'):
    """
    功能：生成词云，返回词云图片对象

    参数：
        text: 用与进行分词的文本，要求之前使用 cut 或者 cut2str 预处理
        bgfile: 指定词云图片的mask模板
        bgcolor: 指定词云图片的背景颜色

    返回：
        success: PIL.image 类型的图片对象
        failed: -1 包括传入空串的情况
    """
    err_msg = str()
    err_flag = 1
    if not (isinstance(text, str) or isinstance(text, list)):
        err_msg = "'text'"
        err_flag = -1
    if not isinstance(bgfile, str):
        if err_flag == -1:
            err_msg += "、'bgfile'"
        else:
            err_flag = -1
            err_msg = "'bgfile'"
    if not isinstance(bgcolor, str):
        if err_flag == -1:
            err_msg += "、'bgcolor'"
        else:
            err_flag = -1
            err_msg = "'bgcolor'"
    if err_flag == -1:
        raise ParameterTypeError(function_name=sys._getframe().f_code.co_name, error_msg=err_msg)

    if isinstance(text, list):
        text = ' '.join(text)

    if text == '':
        err_flag = -1
        err_msg = "'text'"
    if bgfile == '':
        if err_flag == -1:
            err_msg += "、'bgfile'"
        else:
            err_flag = -1
            err_msg = "'bgfile'"
    if err_flag == -1:
        raise ParameterValueError(function_name=sys._getframe().f_code.co_name, error_msg=err_msg)

    bg_image_type = imghdr.what(bgfile)
    if bg_image_type is None:
        raise ParameterValueError(function_name=sys._getframe().f_code.co_name, error_msg="'bgfile'")

    try:
        font = __FONT
        if bgfile:
            with open(bgfile, 'rb') as f:
                bg_mask = base64.b64encode(f.read()).rstrip().decode('utf-8')
        else:
            bg_mask = 'None'

        data = {
            'text': text,
            'font': font,
            'mask': bg_mask,
            'color': bgcolor
        }
        url = __WC_URL

        headers = {'content-type': 'application/json'}
        for i in range(3):
            r = requests.post(url, json=data, headers=headers)
            if r.status_code == 200:
                if r.text != '':
                    base64_data = bytes(r.text, encoding='utf8')
                    byte_data = base64.urlsafe_b64decode(base64_data)
                    img = Image.open(BytesIO(byte_data))
                    return img
        raise ConnectionError('词云服务连接失败')
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_wordcloud')


def main():
    f = open('text.txt', 'r', encoding='utf-8')
    text = f.read()
    f.close()

    print(cut(text))
    print(cut2str(text))

    wordcloud(cut(text), bgfile='test.jpg').show()
    # wordcloud(cut(text)).show()


if __name__ == '__main__':
    main()
