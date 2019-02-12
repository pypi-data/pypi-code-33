import turtle
from random import choice
import pypinyin
import ybc_browser
import ybc_speech
import ybc_tuya
from ybc_exception import *

tuyas = {
    'jiqimao': 'jiqimao',
    'dingdangmao': 'jiqimao',
    'duolaameng': 'jiqimao',
    'dingdang': 'jiqimao',
    'xiaodingdang': 'jiqimao',
    'zuanshi': 'diamond',
    'zuanjie': 'diamond',
    'jiezhi': 'diamond',
    'luoxuan': 'screw',
    'quxian': 'screw',
    'zhu': 'xzpq',
    'xiaozhu': 'xzpq',
    'xiaozhupeiqi': 'xzpq',
    'peiqi': 'xzpq',
    'meiguoduizhang': 'shield',
    'meidui': 'shield',
    'dun': 'shield',
    'dunpai': 'shield',
    'caihong': 'rainbow',
    'tianhong': 'rainbow',
    'renzhe': 'robot',
    'jiqiren': 'robot',
    'renzhejiqiren': 'robot',
    'xiaohua': 'flower',
    'huaduo': 'flower',
    'xiaohonghua': 'flower',
    'honghua': 'flower',
    'xiaoqiche': 'car',
    'biaobai': 'love',
    'woaini': 'love',
    'pikaqiu': 'pikachu',
    'pikachu': 'pikachu',
    'piqiaqiu': 'pikachu',
    'piqiachu': 'pikachu',
    'shizi': 'lion',
    'taiji': 'taiji',
    'bagua': 'taiji',
    'xiaohuangren': 'xiaohuangren',
    'huangren': 'xiaohuangren',
    'yiquanchaoren': 'yqcr',
    'dongganzhengfangxing': 'lxzfx',
    'luoxuanzhengfangxing': 'lxzfx',
    'duzui': 'pout',
    'juezui': 'pout',
    'haimianbaobao': 'hmbb',
    'huaji': 'funny',
    'huajilian': 'funny',
    'chong': 'ladybug',
    'chongzi': 'ladybug',
    'piaochong': 'ladybug',
    'fengche': 'fengche',
    'xiong': ['bear', 'xiongbenxiong', 'whitebear'],
    'baixiong': 'whitebear',
    'qingsongxiong': 'bear',
    'xiongbenxiong': 'xiongbenxiong',
    'heixiong': 'xiongbenxiong',
    'chengxuyuan': 'programmer',
    'che': 'car',
    'qiche': 'car'
}


def todo():
    """
    功能：录制一段语音，打开语音指定的网址，默认打开百度首页。

    参数：无

    返回：若正常打开网页则无返回，否则返回-1
    """
    try:
        filename = ybc_speech.record("tmp.wav", 4)
        if not filename:
            print("没有接收到指令")
            return -1
        print("正在识别，请稍等..")
        try:
            text = ybc_speech.voice2text(filename)
            url_name = text
        except:
            url_name = "百度"

        res = ''.join(pypinyin.lazy_pinyin(text))
        method = []
        for key in tuyas.keys():
            if res in key:
                # 若关键词为 "熊"，则随机调用 白熊、轻松熊、熊本熊中的一个
                if type(tuyas[key]) is list:
                    for inner in tuyas[key]:
                        method.append(inner)
                else:
                    method.append(tuyas[key])

        if method:
            f = getattr(ybc_tuya, choice(method))
            f()
            turtle.done()
            return 0

        # 二次校验避免产生歧义，例如输入 轻松熊 和 熊 时候的判别
        for key in tuyas.keys():
            if key in res:
                if type(tuyas[key]) is list:
                    for inner in tuyas[key]:
                        method.append(inner)
                else:
                    method.append(tuyas[key])

        if method:
            f = getattr(ybc_tuya, choice(method))
            f()
            turtle.done()
            return 0

        if ybc_browser.open_browser(url_name) != -1:
            return 0
        else:
            return -1

    except Exception as e:
        raise InternalError(e, 'ybc_todo')


def main():
    todo()


if __name__ == '__main__':
    main()
