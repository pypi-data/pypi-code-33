# coding: utf-8
import turtle
import platform
import math
import sys
import time
import random
from ybc_exception import *

if platform.system() != 'Linux':
    from PIL import ImageGrab


# 通用函数
def rgb(r=255, g=255, b=255):
    error_flag = 1
    error_msg = ""
    # 参数类型错误检测
    if not isinstance(r, int):
        error_flag = -1
        error_msg = "'r'"
    if not isinstance(g, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'g'"
    if not isinstance(b, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'b'"
    if error_flag == -1:
        raise ParameterTypeError(sys._getframe().f_code.co_name, error_msg)

    # 参数值错误检测
    if not (0 <= r <= 255):
        error_flag = -1
        error_msg = "'r'"
    if not (0 <= g <= 255):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'g'"
    if not (0 <= b <= 255):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'b'"
    if error_flag == -1:
        raise ParameterValueError(sys._getframe().f_code.co_name, error_msg)

    try:
        list = [r, g, b]
        output = "#"
        for x in list:
            intx = int(x)
            if intx < 16:
                output = output + '0' + hex(intx)[2:]
            else:
                output = output + hex(intx)[2:]
        return output
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def canvas(bg=rgb(255, 255, 255)):
    try:
        turtle.screensize(400, 300, bg)
        turtle.setup(800, 600)
        __flush()
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def ruler(size=100, color='#F0F0F0'):
    error_flag = 1
    error_msg = ""
    # 参数类型错误检测
    if not isinstance(size, int):
        error_flag = -1
        error_msg = "'size'"
    if not isinstance(color, str):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'color'"
    if error_flag == -1:
        raise ParameterTypeError(sys._getframe().f_code.co_name, error_msg)

    if size < 0:
        raise ParameterValueError(sys._getframe().f_code.co_name, "'size'")

    try:
        turtle.pencolor(color)
        turtle.speed(0)
        x = -398
        y = 298
        turtle.right(90)
        while x < 400 + size:
            turtle.penup()
            turtle.goto(x, 298)
            turtle.pendown()
            turtle.forward(600)
            x = x + size
        turtle.left(90)
        while y > -300 - size:
            turtle.penup()
            turtle.goto(-398, y)
            turtle.pendown()
            turtle.forward(800)
            y = y - size
        turtle.speed(3)
        turtle.pencolor('black')
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def __flush():
    turtle.done()


def my_goto(x, y):
    error_flag = 1
    error_msg = ""
    # 参数类型错误检测
    if not isinstance(x, (int, float)):
        error_flag = -1
        error_msg = "'x'"
    if not isinstance(y, (int, float)):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'y'"
    if error_flag == -1:
        raise ParameterTypeError(sys._getframe().f_code.co_name, error_msg)

    try:
        if hasattr(turtle, 'reset_coordinate') and callable(getattr(turtle, 'reset_coordinate')):
            turtle.reset_coordinate()

        turtle.penup()
        turtle.goto(x, y)
        turtle.pendown()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except InternalError as e:
        raise InternalError(e, 'ybc_tuya')


def hide():
    turtle.hideturtle()


def clean():
    try:
        turtle.reset()
        __flush()
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# def show():
# 	showturtle()


def stop():
    try:
        hide()
        __flush()
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def pen_size(x=6):
    if not isinstance(x, int):
        raise ParameterTypeError(sys._getframe().f_code.co_name, "'x'")
    if x < 0:
        raise ParameterValueError(sys._getframe().f_code.co_name, "'x'")

    try:
        turtle.pensize(x)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def pen_color(color='black'):
    if not isinstance(color, str):
        raise ParameterTypeError(sys._getframe().f_code.co_name, "'color'")
    try:
        turtle.pencolor(color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, "'color'")


def pen_speed(x=3):
    if not isinstance(x, int):
        raise ParameterTypeError(sys._getframe().f_code.co_name, "'x'")
    if x < 0:
        raise ParameterValueError(sys._getframe().f_code.co_name, "'x'")

    try:
        turtle.speed(x)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, "'x'")


def draw_circle(x, y, size):
    """
    画一个圆形并, 使用浏览器坐标系

    :param x: 圆心 x 轴坐标
    :param y: 圆心 y 轴坐标
    :param size: 圆的半径
    """
    error_flag = 1
    error_msg = ""
    # 参数类型错误检测
    if not isinstance(x, int):
        error_flag = -1
        error_msg = "'x'"
    if not isinstance(y, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'y'"
    if not isinstance(size, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'size'"
    if error_flag == -1:
        raise ParameterTypeError(sys._getframe().f_code.co_name, error_msg)

    if size < 0:
        raise ParameterValueError(sys._getframe().f_code.co_name, "'size'")

    try:
        if hasattr(turtle, 'reset_coordinate') and callable(getattr(turtle, 'reset_coordinate')):
            turtle.reset_coordinate()

        size = abs(size)
        y = y - size
        my_goto(x, y)
        turtle.circle(size)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def fill_circle(x=0, y=0, size=40, bg='gray'):
    """
    画一个圆形并填充颜色, 使用浏览器坐标系

    :param x: 圆心 x 轴坐标
    :param y: 圆心 y 轴坐标
    :param size: 圆的半径
    :param bg: 填充色
    """
    error_flag = 1
    error_msg = ""
    # 参数类型错误检测
    if not isinstance(x, int):
        error_flag = -1
        error_msg = "'x'"
    if not isinstance(y, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'y'"
    if not isinstance(size, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'size'"
    if not isinstance(bg, str):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'bg'"
    if error_flag == -1:
        raise ParameterTypeError(sys._getframe().f_code.co_name, error_msg)

    if size < 0:
        raise ParameterValueError(sys._getframe().f_code.co_name, "'size'")

    try:
        if hasattr(turtle, 'reset_coordinate') and callable(getattr(turtle, 'reset_coordinate')):
            turtle.reset_coordinate()

        size = abs(size)
        turtle.fillcolor(bg)
        __begin_fill()
        y = y - size
        my_goto(x, y)
        turtle.circle(size)
        __end_fill()
        hide()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def draw_rect(x, y, width, height):
    """
    画一个矩形, 使用浏览器坐标系

    :param x: 矩形左上角 x 轴坐标
    :param y: 矩形左上角 y 轴坐标
    :param width: 矩形宽度
    :param height: 矩形高度
    """
    error_flag = 1
    error_msg = ""
    # 参数类型错误检测
    if not isinstance(x, int):
        error_flag = -1
        error_msg = "'x'"
    if not isinstance(y, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'y'"
    if not isinstance(width, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'width'"
    if not isinstance(height, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'height'"
    if error_flag == -1:
        raise ParameterTypeError(sys._getframe().f_code.co_name, error_msg)

    if width < 0:
        error_flag = -1
        error_msg = "'width'"
    if height < 0:
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'height'"
    if error_flag == -1:
        raise ParameterValueError(sys._getframe().f_code.co_name, error_msg)

    try:
        if hasattr(turtle, 'reset_coordinate') and callable(getattr(turtle, 'reset_coordinate')):
            turtle.reset_coordinate()

        my_goto(x, y)
        turtle.forward(width)
        turtle.lt(90)
        turtle.forward(height)
        turtle.lt(90)
        turtle.forward(width)
        turtle.lt(90)
        turtle.forward(height)
        turtle.lt(90)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def fill_rect(x=360, y=260, width=80, height=80, bg='gray'):
    """
    画一个矩形并填充颜色, 使用浏览器坐标系

    :param x: 矩形左上角 x 轴坐标
    :param y: 矩形左上角 y 轴坐标
    :param width: 矩形宽度
    :param height: 矩形高度
    :param bg: 填充色
    """
    error_flag = 1
    error_msg = ""
    # 参数类型错误检测
    if not isinstance(x, int):
        error_flag = -1
        error_msg = "'x'"
    if not isinstance(y, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'y'"
    if not isinstance(width, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'width'"
    if not isinstance(height, int):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'height'"
    if not isinstance(bg, str):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'bg'"
    if error_flag == -1:
        raise ParameterTypeError(sys._getframe().f_code.co_name, error_msg)

    if width < 0:
        error_flag = -1
        error_msg = "'width'"
    if height < 0:
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'height'"
    if error_flag == -1:
        raise ParameterValueError(sys._getframe().f_code.co_name, error_msg)

    try:
        if hasattr(turtle, 'reset_coordinate') and callable(getattr(turtle, 'reset_coordinate')):
            turtle.reset_coordinate()

        turtle.fillcolor(bg)
        __begin_fill()
        my_goto(x, y)
        turtle.forward(width)
        turtle.lt(90)
        turtle.forward(height)
        turtle.lt(90)
        turtle.forward(width)
        turtle.lt(90)
        turtle.forward(height)
        turtle.lt(90)
        __end_fill()
        hide()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def fill_color(color='white'):
    if not isinstance(color, str):
        raise ParameterTypeError(sys._getframe().f_code.co_name, "'color'")

    try:
        turtle.fillcolor(color)
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def __begin_fill():
    turtle.begin_fill()


def __end_fill():
    turtle.end_fill()


#####################################
###############截图#################
#####################################

def save(filename='1.png'):
    if not isinstance(filename, str):
        raise ParameterTypeError(sys._getframe().f_code.co_name, "'filename'")
    if not filename:
        raise ParameterValueError(sys._getframe().f_code.co_name, "'filename'")

    try:
        pic = ImageGrab.grab()
        pic.save(filename)
        __flush()
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############机器猫#################
#####################################

# 无轨迹跳跃
def mao_goto(x, y):
    error_flag = 1
    error_msg = ""
    # 参数类型错误检测
    if not isinstance(x, (int, float)):
        error_flag = -1
        error_msg = "'x'"
    if not isinstance(y, (int, float)):
        if error_flag == -1:
            error_msg += "、"
        error_flag = -1
        error_msg += "'y'"
    if error_flag == -1:
        raise ParameterTypeError(sys._getframe().f_code.co_name, error_msg)

    try:
        turtle.penup()
        turtle.goto(x, y)
        turtle.pendown()
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 眼睛
def eyes():
    try:
        turtle.fillcolor("#ffffff")
        turtle.begin_fill()

        turtle.tracer(False)
        a = 2.5
        for i in range(120):
            if 0 <= i < 30 or 60 <= i < 90:
                a -= 0.05
                turtle.lt(3)
                turtle.fd(a)
            else:
                a += 0.05
                turtle.lt(3)
                turtle.fd(a)
        turtle.tracer(True)
        turtle.end_fill()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 胡须
def beard():
    try:
        mao_goto(-32, 135)
        turtle.seth(165)
        turtle.fd(60)

        mao_goto(-32, 125)
        turtle.seth(180)
        turtle.fd(60)

        mao_goto(-32, 115)
        turtle.seth(193)
        turtle.fd(60)

        mao_goto(37, 135)
        turtle.seth(15)
        turtle.fd(60)

        mao_goto(37, 125)
        turtle.seth(0)
        turtle.fd(60)

        mao_goto(37, 115)
        turtle.seth(-13)
        turtle.fd(60)
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 嘴巴
def mouth():
    try:
        mao_goto(5, 148)
        turtle.seth(270)
        turtle.fd(100)
        turtle.seth(0)
        turtle.circle(120, 50)
        turtle.seth(230)
        turtle.circle(-120, 100)
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 围巾
def scarf():
    try:
        turtle.fillcolor('#e70010')
        turtle.begin_fill()
        turtle.seth(0)
        turtle.fd(200)
        turtle.circle(-5, 90)
        turtle.fd(10)
        turtle.circle(-5, 90)
        turtle.fd(207)
        turtle.circle(-5, 90)
        turtle.fd(10)
        turtle.circle(-5, 90)
        turtle.end_fill()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 鼻子
def nose():
    try:
        mao_goto(-10, 158)
        turtle.seth(315)
        turtle.fillcolor('#e70010')
        turtle.begin_fill()
        turtle.circle(20)
        turtle.end_fill()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 黑眼睛
def black_eyes():
    try:
        turtle.seth(0)
        mao_goto(-20, 195)
        turtle.fillcolor('#000000')
        turtle.begin_fill()
        turtle.circle(13)
        turtle.end_fill()

        turtle.pensize(6)
        mao_goto(20, 205)
        turtle.seth(75)
        turtle.circle(-10, 150)
        turtle.pensize(3)

        mao_goto(-17, 200)
        turtle.seth(0)
        turtle.fillcolor('#ffffff')
        turtle.begin_fill()
        turtle.circle(5)
        turtle.end_fill()
        mao_goto(0, 0)
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 脸
def face():
    try:
        turtle.fd(183)
        turtle.lt(45)
        turtle.fillcolor('#ffffff')
        turtle.begin_fill()
        turtle.circle(120, 100)
        turtle.seth(180)
        # print(pos())
        turtle.fd(121)
        turtle.pendown()
        turtle.seth(215)
        turtle.circle(120, 100)
        turtle.end_fill()
        mao_goto(63.56, 218.24)
        turtle.seth(90)
        eyes()
        turtle.seth(180)
        turtle.penup()
        turtle.fd(60)
        turtle.pendown()
        turtle.seth(90)
        eyes()
        turtle.penup()
        turtle.seth(180)
        turtle.fd(64)
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')

# 头型
def head():
    try:
        mao_goto(0, 0)
        turtle.penup()
        turtle.circle(150, 40)
        turtle.pendown()
        turtle.fillcolor('#00a0de')
        turtle.begin_fill()
        turtle.circle(150, 280)
        turtle.end_fill()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 画哆啦A梦
def Doraemon():
    try:
        # 头部
        head()

        # 围脖
        scarf()

        # 脸
        face()

        # 红鼻子
        nose()

        # 嘴巴
        mouth()

        # 胡须
        beard()

        # 身体
        mao_goto(0, 0)
        turtle.seth(0)
        turtle.penup()
        turtle.circle(150, 50)
        turtle.pendown()
        turtle.seth(30)
        turtle.fd(40)
        turtle.seth(70)
        turtle.circle(-30, 270)

        turtle.fillcolor('#00a0de')
        turtle.begin_fill()

        turtle.seth(230)
        turtle.fd(80)
        turtle.seth(90)
        turtle.circle(1000, 1)
        turtle.seth(-89)
        turtle.circle(-1000, 10)

        # print(pos())

        turtle.seth(180)
        turtle.fd(70)
        turtle.seth(90)
        turtle.circle(30, 180)
        turtle.seth(180)
        turtle.fd(70)

        # print(pos())
        turtle.seth(100)
        turtle.circle(-1000, 9)

        turtle.seth(-86)
        turtle.circle(1000, 2)
        turtle.seth(230)
        turtle.fd(40)

        # print(pos())

        turtle.circle(-30, 230)
        turtle.seth(45)
        turtle.fd(81)
        turtle.seth(0)
        turtle.fd(203)
        turtle.circle(5, 90)
        turtle.fd(10)
        turtle.circle(5, 90)
        turtle.fd(7)
        turtle.seth(40)
        turtle.circle(150, 10)
        turtle.seth(30)
        turtle.fd(40)
        turtle.end_fill()

        # 左手
        turtle.seth(70)
        turtle.fillcolor('#ffffff')
        turtle.begin_fill()
        turtle.circle(-30)
        turtle.end_fill()

        # 脚
        mao_goto(103.74, -182.59)
        turtle.seth(0)
        turtle.fillcolor('#ffffff')
        turtle.begin_fill()
        turtle.fd(15)
        turtle.circle(-15, 180)
        turtle.fd(90)
        turtle.circle(-15, 180)
        turtle.fd(10)
        turtle.end_fill()

        mao_goto(-96.26, -182.59)
        turtle.seth(180)
        turtle.fillcolor('#ffffff')
        turtle.begin_fill()
        turtle.fd(15)
        turtle.circle(15, 180)
        turtle.fd(90)
        turtle.circle(15, 180)
        turtle.fd(10)
        turtle.end_fill()

        # 右手
        mao_goto(-133.97, -91.81)
        turtle.seth(50)
        turtle.fillcolor('#ffffff')
        turtle.begin_fill()
        turtle.circle(30)
        turtle.end_fill()

        # 口袋
        mao_goto(-103.42, 15.09)
        turtle.seth(0)
        turtle.fd(38)
        turtle.seth(230)
        turtle.begin_fill()
        turtle.circle(90, 260)
        turtle.end_fill()

        mao_goto(5, -40)
        turtle.seth(0)
        turtle.fd(70)
        turtle.seth(-90)
        turtle.circle(-70, 180)
        turtle.seth(0)
        turtle.fd(70)

        # 铃铛
        mao_goto(-103.42, 15.09)
        turtle.fd(90)
        turtle.seth(70)
        turtle.fillcolor('#ffd200')
        # print(pos())
        turtle.begin_fill()
        turtle.circle(-20)
        turtle.end_fill()
        turtle.seth(170)
        turtle.fillcolor('#ffd200')
        turtle.begin_fill()
        turtle.circle(-2, 180)
        turtle.seth(10)
        turtle.circle(-100, 22)
        turtle.circle(-2, 180)
        turtle.seth(180 - 10)
        turtle.circle(100, 22)
        turtle.end_fill()
        turtle.goto(-13.42, 15.09)
        turtle.seth(250)
        turtle.circle(20, 110)
        turtle.seth(90)
        turtle.fd(15)
        turtle.dot(10)
        mao_goto(0, -150)

        # 画眼睛
        black_eyes()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def jiqimao():
    try:
        turtle.screensize(600, 800, "#f0f0f0")
        turtle.pensize(3)  # 画笔宽度
        turtle.speed(9)  # 画笔速度
        Doraemon()
        mao_goto(100, -260)
        turtle.write('BY YBC', font=("Bradley Hand ITC", 30, "bold"))
        # turtle.mainloop()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############小猪佩奇#################
#####################################


def _nose_xzpq(x=-100, y=100, pc='#FF9BC0', fc='#A0522D'):  # 鼻子
    turtle.pu()
    turtle.goto(x, y)
    turtle.pd()
    turtle.seth(-30)
    turtle.begin_fill()
    a = 0.4
    for i in range(120):
        if 0 <= i < 30 or 60 <= i < 90:
            a = a + 0.08
            turtle.lt(3)  # 向左转3度
            turtle.fd(a)  # 向前走a的步长
        else:
            a = a - 0.08
            turtle.lt(3)
            turtle.fd(a)
    turtle.end_fill()

    turtle.pu()
    turtle.seth(90)
    turtle.fd(25)
    turtle.seth(0)
    turtle.fd(10)
    turtle.pd()
    turtle.pencolor(pc)
    turtle.seth(10)
    turtle.circle(5)
    turtle.begin_fill()
    turtle.color(fc)
    turtle.end_fill()

    turtle.pu()
    turtle.seth(0)
    turtle.fd(20)
    turtle.pd()
    turtle.pencolor(pc)
    turtle.seth(10)
    turtle.circle(5)
    turtle.begin_fill()
    turtle.color(fc)
    turtle.end_fill()


def _head_xzpq(x=-69, y=167, pc='#FF9BC0', fc='pink'):  # 头
    turtle.color(pc, fc)
    turtle.pu()
    turtle.goto(x, y)
    turtle.seth(0)
    turtle.pd()
    turtle.begin_fill()
    turtle.seth(180)
    turtle.circle(300, -30)
    turtle.circle(100, -60)
    turtle.circle(80, -100)
    turtle.circle(150, -20)
    turtle.circle(60, -95)
    turtle.seth(161)
    turtle.circle(-300, 15)
    turtle.pu()
    turtle.goto(-100, 100)
    turtle.pd()
    turtle.seth(-30)
    a = 0.4
    for i in range(60):
        if 0 <= i < 30 or 60 <= i < 90:
            a = a + 0.08
            turtle.lt(3)  # 向左转3度
            turtle.fd(a)  # 向前走a的步长
        else:
            a = a - 0.08
            turtle.lt(3)
            turtle.fd(a)
    turtle.end_fill()


def _ears_xzpq(x=0, y=160, pc='#FF9BC0', fc='pink'):  # 耳朵
    turtle.color(pc, fc)
    turtle.pu()
    turtle.goto(x, y)
    turtle.pd()
    turtle.begin_fill()
    turtle.seth(100)
    turtle.circle(-50, 50)
    turtle.circle(-10, 120)
    turtle.circle(-50, 54)
    turtle.end_fill()

    turtle.pu()
    turtle.seth(90)
    turtle.fd(-12)
    turtle.seth(0)
    turtle.fd(30)
    turtle.pd()
    turtle.begin_fill()
    turtle.seth(100)
    turtle.circle(-50, 50)
    turtle.circle(-10, 120)
    turtle.circle(-50, 56)
    turtle.end_fill()


def _eyes_xzpq(x=0, y=140, pc='#FF9BC0', fc='white'):  # 眼睛
    turtle.color(pc, fc)
    turtle.pu()
    turtle.seth(90)
    turtle.fd(-20)
    turtle.seth(0)
    turtle.fd(-95)
    turtle.pd()
    turtle.begin_fill()
    turtle.circle(15)
    turtle.end_fill()

    turtle.color("black")
    turtle.pu()
    turtle.seth(90)
    turtle.fd(12)
    turtle.seth(0)
    turtle.fd(-3)
    turtle.pd()
    turtle.begin_fill()
    turtle.circle(3)
    turtle.end_fill()

    turtle.color(pc, fc)
    turtle.pu()
    turtle.seth(90)
    turtle.fd(-25)
    turtle.seth(0)
    turtle.fd(40)
    turtle.pd()
    turtle.begin_fill()
    turtle.circle(15)
    turtle.end_fill()

    turtle.color("black")
    turtle.pu()
    turtle.seth(90)
    turtle.fd(12)
    turtle.seth(0)
    turtle.fd(-3)
    turtle.pd()
    turtle.begin_fill()
    turtle.circle(3)
    turtle.end_fill()


def _cheek_xzpq(x=80, y=10, pc='#FF9BC0', fc='#FF9BC0'):  # 腮
    turtle.color(pc, fc)
    turtle.pu()
    turtle.goto(x, y)
    turtle.pd()
    turtle.seth(0)
    turtle.begin_fill()
    turtle.circle(30)
    turtle.end_fill()


def _mouth_xzpq(x=-20, y=30, pc='#EF4513'):  # 嘴
    turtle.color(pc)
    turtle.pu()
    turtle.goto(x, y)
    turtle.pd()
    turtle.seth(-80)
    turtle.circle(30, 40)
    turtle.circle(40, 80)


def _body_xzpq(x=-32, y=-8, pc='red', fc='#FF6347'):  # 身体
    turtle.color(pc, fc)
    turtle.pu()
    turtle.goto(x, y)
    turtle.pd()
    turtle.begin_fill()
    turtle.seth(-130)
    turtle.circle(100, 10)
    turtle.circle(300, 30)
    turtle.seth(0)
    turtle.fd(230)
    turtle.seth(90)
    turtle.circle(300, 30)
    turtle.circle(100, 3)
    turtle.seth(-135)
    turtle.circle(-80, 63)
    turtle.circle(-150, 24)
    turtle.end_fill()


def _hands_xzpq(x=-56, y=-45, pc='#FF9BC0', fc='#FF9BC0'):  # 手
    turtle.color(pc, fc)
    turtle.pu()
    turtle.goto(x, y)
    turtle.pd()
    turtle.seth(-160)
    turtle.circle(300, 15)
    turtle.pu()
    turtle.seth(90)
    turtle.fd(15)
    turtle.seth(0)
    turtle.fd(0)
    turtle.pd()
    turtle.seth(-10)
    turtle.circle(-20, 90)

    turtle.pu()
    turtle.seth(90)
    turtle.fd(30)
    turtle.seth(0)
    turtle.fd(237)
    turtle.pd()
    turtle.seth(-20)
    turtle.circle(-300, 15)
    turtle.pu()
    turtle.seth(90)
    turtle.fd(20)
    turtle.seth(0)
    turtle.fd(0)
    turtle.pd()
    turtle.seth(-170)
    turtle.circle(20, 90)


def _foot_xzpq(x=2, y=-177, pc='#F08080', fc='#black'):  # 脚
    turtle.pensize(10)
    turtle.color(pc)
    turtle.pu()
    turtle.goto(x, y)
    turtle.pd()
    turtle.seth(-90)
    turtle.fd(40)
    turtle.seth(-180)
    turtle.color(fc)
    turtle.pensize(15)
    turtle.fd(20)

    turtle.pensize(10)
    turtle.color(pc)
    turtle.pu()
    turtle.seth(90)
    turtle.fd(40)
    turtle.seth(0)
    turtle.fd(90)
    turtle.pd()
    turtle.seth(-90)
    turtle.fd(40)
    turtle.seth(-180)
    turtle.color(fc)
    turtle.pensize(15)
    turtle.fd(20)


def _tail_xzpq(x=148, y=-155, pc='#FF9BC0', fc='#FF9BC0'):  # 尾巴
    turtle.pensize(4)
    turtle.color(pc, fc)
    turtle.pu()
    turtle.goto(x, y)
    turtle.pd()
    turtle.seth(0)
    turtle.circle(70, 20)
    turtle.circle(10, 330)
    turtle.circle(70, 30)


def setting(fc='pink'):  # 参数设置
    turtle.pensize(4)
    turtle.hideturtle()
    turtle.colormode(255)
    turtle.color((255, 155, 192), fc)
    # turtle.setup(840,500)
    turtle.speed(6)


def xzpq_nose(color='pink'):
    __checkout_color(sys._getframe().f_code.co_name, color)
    try:
        setting(fc=color)
        _nose_xzpq(fc=color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def xzpq_head(color='pink'):
    __checkout_color(sys._getframe().f_code.co_name, color)
    try:
        _head_xzpq(fc=color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def xzpq_ears(color='pink'):
    __checkout_color(sys._getframe().f_code.co_name, color)
    try:
        _ears_xzpq(fc=color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def xzpq_eyes(color='white'):
    __checkout_color(sys._getframe().f_code.co_name, color)
    try:
        _eyes_xzpq(fc=color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def xzpq_cheek(color='#FF9BC0'):
    __checkout_color(sys._getframe().f_code.co_name, color)
    try:
        _cheek_xzpq(fc=color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def xzpq_mouth(color='#EF4513'):
    __checkout_color(sys._getframe().f_code.co_name, color)
    try:
        _mouth_xzpq(pc=color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def xzpq_body(color='#FF6347'):
    __checkout_color(sys._getframe().f_code.co_name, color)
    try:
        _body_xzpq(fc=color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def xzpq_hands(color='#FF9BC0'):
    __checkout_color(sys._getframe().f_code.co_name, color)
    try:
        _hands_xzpq(pc=color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def xzpq_foot(color='black'):
    __checkout_color(sys._getframe().f_code.co_name, color)
    try:
        _foot_xzpq(fc=color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def xzpq_tail(color='#FF9BC0'):
    __checkout_color(sys._getframe().f_code.co_name, color)
    try:
        _tail_xzpq(pc=color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 小猪佩奇
def xzpq():
    try:
        xzpq_nose()  # 鼻子
        xzpq_head()  # 头
        xzpq_ears()  # 耳朵
        xzpq_eyes()  # 眼睛
        xzpq_cheek()  # 腮
        xzpq_mouth()  # 嘴
        xzpq_body()  # 身体
        xzpq_hands()  # 手
        xzpq_foot()  # 脚
        xzpq_tail()  # 尾巴
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############美国队长盾牌############
#####################################

def shield_c1(c='red'):
    try:
        # 第一个圆
        turtle.color(c)
        turtle.begin_fill()
        r = 190
        turtle.penup()
        turtle.right(90)
        turtle.forward(r)
        turtle.pendown()
        turtle.left(90)
        turtle.circle(r)
        turtle.end_fill()
        turtle.penup()
        turtle.left(90)
        turtle.forward(r)
        turtle.right(90)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')



def shield_c2(c='white'):
    try:
        # 第二个圆
        turtle.color(c)
        turtle.begin_fill()
        r = 147
        turtle.penup()
        turtle.right(90)
        turtle.forward(r)
        turtle.pendown()
        turtle.left(90)
        turtle.circle(r)
        turtle.end_fill()
        turtle.penup()
        turtle.left(90)
        turtle.forward(r)
        turtle.right(90)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')



def shield_c3(c='red'):
    try:
        # 第三个圆
        turtle.color(c)
        turtle.begin_fill()
        r = 106.5
        turtle.penup()
        turtle.right(90)
        turtle.forward(r)
        turtle.pendown()
        turtle.left(90)
        turtle.circle(r)
        turtle.end_fill()
        turtle.penup()
        turtle.left(90)
        turtle.forward(r)
        turtle.right(90)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')



def shield_c4(c='blue'):
    try:
        # 第三个圆
        turtle.color(c)
        turtle.begin_fill()
        r = 62
        turtle.penup()
        turtle.right(90)
        turtle.forward(r)
        turtle.pendown()
        turtle.left(90)
        turtle.circle(r)
        turtle.end_fill()
        turtle.penup()
        turtle.left(90)
        turtle.forward(r)
        turtle.right(90)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')



def shield_star(c='white'):
    try:
        # 完成五角星
        r = 62
        turtle.penup()
        turtle.left(90)
        turtle.forward(r)
        turtle.right(90)
        turtle.left(288)
        turtle.pendown()
        long_side = 45.05
        turtle.color(c)
        turtle.begin_fill()
        for i in range(10):
            turtle.forward(long_side)
            if i % 2 == 0:
                turtle.left(72)
            else:
                turtle.right(144)
        turtle.end_fill()
        turtle.penup()
        turtle.hideturtle()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 美国队长盾牌
def shield():
    try:
        shield_c1()
        shield_c2()
        shield_c3()
        shield_c4()
        shield_star()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')



#####################################
###############彩虹###################
#####################################
def rainbow_c1(c='red'):
    try:
        turtle.penup()
        turtle.forward(300)
        turtle.pendown()

        turtle.color(c)
        turtle.left(90)
        turtle.begin_fill()
        turtle.circle(300,180)
        turtle.end_fill()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def rainbow_c2(c='orange'):
    try:
        turtle.left(90)
        turtle.forward(20)
        turtle.left(90)
        turtle.color(c)
        turtle.begin_fill()
        turtle.circle(-280,180)
        turtle.end_fill()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')

def rainbow_c3(c='yellow'):
    try:
        turtle.right(90)
        turtle.forward(20)
        turtle.right(90)
        turtle.color(c)
        turtle.begin_fill()
        turtle.circle(260,180)
        turtle.end_fill()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def rainbow_c4(c='green'):
    try:
        turtle.left(90)
        turtle.forward(20)
        turtle.left(90)
        turtle.color(c)
        turtle.begin_fill()
        turtle.circle(-240,180)
        turtle.end_fill()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def rainbow_c5(c='cyan'):
    try:
        turtle.right(90)
        turtle.forward(20)
        turtle.right(90)
        turtle.color(c)
        turtle.begin_fill()
        turtle.circle(220,180)
        turtle.end_fill()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def rainbow_c6(c='blue'):
    try:
        turtle.left(90)
        turtle.forward(20)
        turtle.left(90)
        turtle.color(c)
        turtle.begin_fill()
        turtle.circle(-200,180)
        turtle.end_fill()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def rainbow_c7(c='purple'):
    try:
        turtle.right(90)
        turtle.forward(20)
        turtle.right(90)
        turtle.color(c)
        turtle.begin_fill()
        turtle.circle(180,180)
        turtle.end_fill()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def rainbow_c8(c='white'):
    try:
        turtle.left(90)
        turtle.forward(20)
        turtle.left(90)
        turtle.color(c)
        turtle.begin_fill()
        turtle.circle(-160,180)
        turtle.end_fill()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')

# 彩虹
def rainbow():
    try:
        turtle.screensize(650, 800)
        rainbow_c1()
        rainbow_c2()
        rainbow_c3()
        rainbow_c4()
        rainbow_c5()
        rainbow_c6()
        rainbow_c7()
        rainbow_c8()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############机器人#################
#####################################

def robot_head(color='black'):
    try:
        turtle.screensize(600, 800)
        pen_color()
        _turtle_fill_circle(0, 0, 150, color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def robot_body(color='black'):
    try:
        turtle.screensize(600, 800)
        _turtle_fill_rect(-80, 0, 160, 180, color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def robot_hands(color='black'):
    try:
        turtle.screensize(600, 800)
        _turtle_fill_rect(-140, -20, 40, 80, color)
        _turtle_fill_rect(100, -20, 40, 80, color)
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def robot_foot(color='black'):
    try:
        turtle.screensize(600, 800)
        _turtle_fill_rect(-100, -200, 80, 80, color)
        _turtle_fill_rect(20, -200, 80, 80, color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def robot_face(color='gold'):
    try:
        turtle.screensize(600, 800)
        _turtle_fill_rect(-120, 200, 240, 100, color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def robot_eyes(color='white'):
    try:
        turtle.screensize(600, 800)
        _turtle_fill_rect(-100, 180, 60, 60, color)
        _turtle_fill_rect(40, 180, 60, 60, color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def robot_mouth(color='red'):
    try:
        turtle.screensize(600, 800)
        _turtle_fill_rect(-50, 50, 100, 5, color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def robot():
    turtle.screensize(600, 800)
    robot_head()
    robot_body()
    robot_hands()
    robot_foot()
    robot_face()
    robot_eyes()
    robot_mouth()


#####################################
###############钻石###################
#####################################

# 钻石
def diamond():
    try:
        turtle.pensize(30)
        turtle.penup()
        turtle.right(90)
        turtle.forward(50)
        turtle.pendown()
        turtle.color('#CFD0D1')
        turtle.right(90)
        turtle.circle(100)
        turtle.left(180)
        turtle.pensize(1)
        turtle.right(90)
        turtle.penup()
        turtle.forward(50)
        turtle.pendown()
        turtle.color('#D105DF')
        turtle.begin_fill()
        turtle.goto(170, 70)
        turtle.goto(130, 70)
        turtle.goto(0, -100)
        turtle.end_fill()
        turtle.color('#B100BE')
        turtle.begin_fill()
        turtle.goto(0, 70)
        turtle.goto(130, 70)
        turtle.end_fill()
        turtle.color('#E016F1')
        turtle.begin_fill()
        turtle.goto(170, 70)
        turtle.goto(130, 102)
        turtle.goto(130, 70)
        turtle.end_fill()
        turtle.color('#EC26F8')
        turtle.begin_fill()
        turtle.goto(65, 102)
        turtle.goto(0, 70)
        turtle.goto(130, 70)
        turtle.end_fill()
        turtle.color('#F865FF')
        turtle.begin_fill()
        turtle.goto(65, 102)
        turtle.goto(80, 130)
        turtle.goto(130, 102)
        turtle.end_fill()
        turtle.color('#EA27F7')
        turtle.begin_fill()
        turtle.goto(90, 130)
        turtle.goto(80, 130)
        turtle.end_fill()
        turtle.color('#FBA7FE')
        turtle.begin_fill()
        turtle.goto(0, 130)
        turtle.goto(65, 102)
        turtle.end_fill()
        turtle.color('#F641FF')
        turtle.begin_fill()
        turtle.goto(0, 70)
        turtle.goto(-65, 102)
        turtle.goto(0, 130)
        turtle.end_fill()
        turtle.color('#FBA7FE')
        turtle.begin_fill()
        turtle.goto(-80, 130)
        turtle.goto(-65, 102)
        turtle.end_fill()
        turtle.color('#F865FE')
        turtle.begin_fill()
        turtle.goto(-130, 70)
        turtle.goto(-130, 102)
        turtle.goto(-80, 130)
        turtle.end_fill()
        turtle.color('#FBC7FF')
        turtle.begin_fill()
        turtle.goto(-90, 130)
        turtle.goto(-130, 102)
        turtle.end_fill()
        turtle.color('#FBBBFF')
        turtle.begin_fill()
        turtle.goto(-170, 69)
        turtle.goto(-130, 69)
        turtle.end_fill()
        turtle.color('#EC26F8')
        turtle.begin_fill()
        turtle.goto(0, 70)
        turtle.goto(-65, 102)
        turtle.goto(-130, 69)
        turtle.end_fill()
        turtle.color('#EB95F2')
        turtle.begin_fill()
        turtle.goto(-170, 69)
        turtle.goto(0, -100)
        turtle.goto(-130, 69)
        turtle.end_fill()
        turtle.color('#D105DF')
        turtle.begin_fill()
        turtle.goto(0, 69)
        turtle.goto(0, -100)
        turtle.end_fill()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############花####################
#####################################
def rectangle(base, height):
    try:
        for i in range(2):
            turtle.forward(base)
            turtle.right(90)
            turtle.forward(height)
            turtle.right(90)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def leaf(scale):
    try:
        length = 0.6 * scale
        turtle.left(45)
        turtle.forward(length)
        turtle.right(45)
        turtle.forward(length)
        turtle.right(135)
        turtle.forward(length)
        turtle.right(45)
        turtle.forward(length)
        turtle.right(180)
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def moveAround(relX, relY, back):
    try:
        if back:
            relX = -1 * relX
            relY = -1 * relY
        turtle.forward(relX)
        turtle.right(90)
        turtle.forward(relY)
        turtle.left(90)
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def filledcircle(radius, col):
    try:
        turtle.color(col)
        turtle.pendown()
        turtle.begin_fill()
        turtle.circle(radius)
        turtle.end_fill()
        turtle.penup()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def petals(radius, bloomDiameter, noOfPetals, col):
    try:
        turtle.penup()
        turtle.color(col)
        petalFromEye = 1.5 * radius
        relY = (radius + petalFromEye) / 2
        relX = petalFromEye / 2
        angle = 360 / noOfPetals
        moveAround(relX, relY, False)
        for i in range(noOfPetals):
            turtle.pendown()
            turtle.begin_fill()
            turtle.circle(radius)
            turtle.end_fill()
            turtle.penup()
            turtle.left((i + 1) * angle)
            turtle.forward(petalFromEye)
            turtle.right((i + 1) * angle)
        moveAround(relX, relY, True)
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 茎
def stem(c='#61D836'):
    try:
        turtle.color(c)
        turtle.pendown()
        turtle.begin_fill()
        rectangle(10, 150)
        moveAround(10, 105, False)
        leaf(75)
        moveAround(10, 105, True)
        turtle.end_fill()
        turtle.penup()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')

# 花瓣
def petal(color='#FF1B5F'):
    try:
        turtle.penup()
        turtle.forward(5)
        petals(40, 200, 6, color)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


# 花蕊
def stamen(color='#F2D95F'):
    try:
        filledcircle(40, color)
        turtle.forward(-5)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')

# 花
def flower():
    try:
        turtle.speed(500)
        stem()
        petal()
        stamen()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
############flappybird###############
#####################################


# from time import time, sleep
# from random import randint
# from subprocess import Popen
# import sys
# import glob
# import os
# import os.path

# # data文件夹路径
# data_path = os.path.abspath(__file__)
# data_path = os.path.split(data_path)[0]+'/data/'

# def play_sound(name, vol=100):
#     file_name = data_path + name + ".mp3"
#     if sys.platform == "darwin":
#         cmds = ["afplay"]
#     else:
#         cmds = ["mplayer", "-softvol", "-really-quiet", "-volume", str(vol)]
#     try:
#         Popen(cmds + [file_name])
#     except:
#         pass

# turtle.TurtleScreen.screensize(216, 500)
# turtle.setup(288, 512)
# turtle.tracer(False, 0)
# turtle.hideturtle()
# for f in glob.glob(data_path + "*.gif"):
#     addshape(f)

# font_name = "Comic Sans MS"
# turtle.speed_x = 100
# ground_line = -200 + 56 + 12
# tube_dist = 230
# bg_width = 286


# def TextTurtle(x, y, color):
#     t = Turtle()
#     t.turtle.hideturtle()
#     t.up()
#     t.turtle.goto(x, y)
#     t.turtle.speed(0)
#     t.turtle.color(color)
#     return t


# def GIFTurtle(fname):
#     t = Turtle(data_path + fname + ".gif")
#     t.turtle.speed(0)
#     t.up()
#     return t

# score_txt = TextTurtle(0, 130, "white")
# best_txt = TextTurtle(90, 180, "white")
# pycon_apac_txt = TextTurtle(0, -270, "white")
# bgpic(data_path + "bg1.gif")
# tubes = [(GIFTurtle("tube1"), GIFTurtle("tube2")) for i in range(3)]
# grounds = [GIFTurtle("ground") for i in range(3)]
# bird = GIFTurtle("bird1")

# PYCON_APAC_AD = """\
#      More Fun at
# PyCon APAC 2014/TW
# """

# class Game:
#     state = "end"
#     score = best = 0
# game = Game()


# def start_game(game):
#     game.best = max(game.score, game.best)
#     game.tubes_y = [10000] * 3
#     game.hit_t, game.hit_y = 0, 0
#     game.state = "alive"
#     game.tube_base = 0
#     game.score = 0
#     game.start_time = time()
#     pycon_apac_txt.clear()
#     uturtle.pdate_game(game)


# def comturtle.pute_y(t, game):
#     return game.hit_y - 100 * (t - game.hit_t) * (t - game.hit_t - 1)


# def uturtle.pdate_game(game):
#     if game.state == "dead":
#         play_sound("clickclick")
#         pycon_apac_txt.turtle.write(
#             PYCON_APAC_AD,
#             align="center",
#             font=(font_name, 24, "bold")
#         )
#         sleep(2)
#         game.state = "end"
#         return
#     t = time() - game.start_time
#     bird_y = comturtle.pute_y(t, game)
#     if bird_y <= ground_line:
#         bird_y = ground_line
#         game.state = "dead"
#     x = int(t * turtle.speed_x)
#     tube_base = -(x % tube_dist) - 40
#     if game.tube_base < tube_base:
#         if game.tubes_y[2] < 1000:
#             game.score += 5
#             play_sound("bip")
#         game.tubes_y = game.tubes_y[1:] + [randint(-100, 50)]
#     game.tube_base = tube_base
#     for i in range(3):
#         tubes[i][0].turtle.goto(
#             tube_base + tube_dist * (i - 1), 250 + game.tubes_y[i])
#         tubes[i][1].turtle.goto(
#             tube_base + tube_dist * (i - 1), -150 + game.tubes_y[i])
#     if game.tubes_y[2] < 1000:
#         tube_turtle.left = tube_base + tube_dist - 28
#         tube_turtle.right = tube_base + tube_dist + 28
#         tube_upper = game.tubes_y[2] + 250 - 160
#         tube_lower = game.tubes_y[2] - 150 + 160
#         center = Vec2D(0, bird_y - 2)
#         lvec = Vec2D(tube_turtle.left, tube_upper) - center
#         rvec = Vec2D(tube_turtle.right, tube_upper) - center
#         if (tube_turtle.left < 18 and tube_turtle.right > -18) and bird_y - 12 <= tube_lower:
#             game.state = "dead"
#         if (tube_turtle.left <= 8 and tube_turtle.right >= -8) and bird_y + 12 >= tube_upper:
#             game.state = "dead"
#         if abs(lvec) < 14 or abs(rvec) < 14:
#             game.state = "dead"
#     bg_base = -(x % bg_width)
#     for i in range(3):
#         grounds[i].turtle.goto(bg_base + bg_width * (i - 1), -200)
#     bird.shape(data_path + "bird%d.gif" % abs(int(t * 4) % 4 - 1))
#     bird.turtle.goto(0, bird_y)
#     score_txt.clear()
#     score_txt.turtle.write(
#         "%s" % (game.score), align="center", font=(font_name, 80, "bold"))
#     if game.best:
#         best_txt.clear()
#         best_txt.turtle.write(
#             "BEST: %d" % (game.best), align="center", font=(font_name, 14, "bold"))
#     uturtle.pdate()
#     ontimer(lambda: uturtle.pdate_game(game), 10)


# def fly(game=game):
#     if game.state == "end":
#         start_game(game)
#         return
#     t = time() - game.start_time
#     bird_y = comturtle.pute_y(t, game)
#     if bird_y > ground_line:
#         game.hit_t, game.hit_y = t, bird_y
#         play_sound("tack", 20)

# def flappy():
#     onkey(fly, "space")
#     listen()
#     turtle.mainloop()
#     sys.exit(1)

#####################################
###############螺旋###################
#####################################

# 画螺旋线图形
def screw():
    try:
        turtle.bgcolor('white')
        turtle.speed(0)
        # turtle.color('white')
        # for i in range(10):
        #     size = 100
        #     for i in range(10):
        #         turtle.circle(size)
        #         size=size-4
        #     turtle.right(360/10)
        turtle.color('yellow')
        for i in range(10):
            size = 100
            for i in range(4):
                turtle.circle(size)
                size = size - 10
            turtle.right(360 / 10)
        turtle.color('blue')
        for i in range(10):
            size = 100
            for i in range(4):
                turtle.circle(size)
                size = size - 5
            turtle.right(360 / 10)
        turtle.color('orange')
        for i in range(10):
            size = 100
            for i in range(4):
                turtle.circle(size)
                size = size - 19
            turtle.right(360 / 10)
        turtle.color('pink')
        for i in range(10):
            size = 100
            for i in range(4):
                turtle.circle(size)
                size = size - 20
            turtle.right(360 / 10)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')



#####################################
#############通用辅助函数##############
#####################################
WIDTH = 600
HEIGHT = 600


# 辅助函数
def _turtle_fill_circle(x, y, size, color):
    turtle.penup()
    turtle.goto(x, y)
    turtle.pendown()
    turtle.fillcolor(color)
    turtle.begin_fill()
    turtle.circle(size)
    turtle.end_fill()


def _turtle_draw_rect(x, y, width, height):
    """
    使用 turtle 坐标系画一个矩形
    """
    turtle.penup()
    turtle.goto(x, y)
    turtle.pendown()
    turtle.forward(width)
    turtle.right(90)
    turtle.forward(height)
    turtle.right(90)
    turtle.forward(width)
    turtle.right(90)
    turtle.forward(height)
    turtle.right(90)


def _turtle_fill_rect(x=0, y=0, width=80, height=80, bg='gray'):
    """
    使用 turtle 坐标系填充一个矩形
    """
    turtle.fillcolor(bg)
    turtle.penup()
    turtle.goto(x, y)
    turtle.pendown()
    turtle.begin_fill()
    turtle.forward(width)
    turtle.right(90)
    turtle.forward(height)
    turtle.right(90)
    turtle.forward(width)
    turtle.right(90)
    turtle.forward(height)
    turtle.right(90)
    turtle.end_fill()
    hide()


def _linear_interp(p1, p2, t):
    return p1 * (1 - t) + p2 * t


def _bezier1(p1, p2, t):
    return (
        _linear_interp(p1[0], p2[0], t),
        _linear_interp(p1[1], p2[1], t)
    )


def _bezier2(p1, p2, p3, t):
    return _bezier1(
        _bezier1(p1, p2, t),
        _bezier1(p2, p3, t),
        t
    )


def _bezier3(p1, p2, p3, p4, t):
    return _bezier1(
        _bezier2(p1, p2, p3, t),
        _bezier2(p2, p3, p4, t),
        t
    )


def _bezier_3(p1, p2, p3, p4):
    for t in [x / 15 for x in range(0, 15 + 1)]:
        x, y = _bezier3(p1, p2, p3, p4, t)
        turtle.goto(x, y)


def _p(c):  # 将 SVG 坐标 c 转换为 tur 坐标
    return complex(
        + c.real - WIDTH / 2,
        - c.imag + HEIGHT / 2
    )


def _M(c):  # 移动到 SVG 坐标 c
    turtle.goto(_p(c).real, _p(c).imag)


def _L(start, end):
    _M(start)
    _M(end)


def _C(start, control1, control2, end):
    _M(start)
    _bezier_3(
        (_p(start).real, _p(start).imag),
        (_p(control1).real, _p(control1).imag),
        (_p(control2).real, _p(control2).imag),
        (_p(end).real, _p(end).imag))


def _f(sp=0j, rgb='red'):
    turtle.fillcolor(rgb)
    _M(sp)
    turtle.begin_fill()


def _pd(sp, rgb="#E4007F", bold=6):
    turtle.color(rgb)
    turtle.pensize(bold)
    _M(sp)
    turtle.pendown()


def _pu():
    turtle.penup()
    turtle.pensize(6)
    turtle.color("black")


def _Mv(c):  # 移动到 SVG 坐标 c
    turtle.penup()
    turtle.goto(_p(c).real, _p(c).imag)
    turtle.pendown()


#####################################
###############狮子###################
#####################################
def lion():
    try:
        turtle.screensize(600, 600)
        turtle.bgcolor("white")

        turtle.pensize(6)
        turtle.speed(0)
        turtle.penup()

        # 一笔画
        _pd(203.5 + 379.5j, rgb="black", bold=6)
        _C(203.5 + 379.5j, 197.24 + 399.34j, 194.05 + 416j, 193.5 + 427.5j)
        _C(193.5 + 427.5j, 192.5 + 448.5j, 191.5 + 495.5j, 200.5 + 519.5j)
        _C(200.5 + 519.5j, 205.81 + 533.66j, 206.54 + 549.22j, 211.5 + 563.5j)
        _C(211.5 + 563.5j, 212.52 + 566.44j, 214.72 + 572.08j, 212.5 + 577.5j)
        _C(212.5 + 577.5j, 211.49 + 579.96j, 210.22 + 580.81j, 210.5 + 582.5j)
        _C(210.5 + 582.5j, 211.12 + 586.23j, 218.46 + 589.01j, 224.5 + 588.5j)
        _C(224.5 + 588.5j, 231.72 + 587.89j, 238.68 + 583.5j, 239.5 + 579.5j)
        _C(239.5 + 579.5j, 247.5 + 540.5j, 248.71 + 520.13j, 270.5 + 516.5j)
        _C(270.5 + 516.5j, 281.5 + 514.67j, 293.72 + 528.93j, 295.5 + 540.5j)
        _C(295.5 + 540.5j, 297.5 + 553.5j, 298.07 + 560.37j, 300.5 + 572.5j)
        _C(300.5 + 572.5j, 302.5 + 582.5j, 313.5 + 588.5j, 327.5 + 586.5j)
        _C(327.5 + 586.5j, 329.79 + 586.17j, 333.5 + 582.5j, 330.5 + 578.5j)
        _C(330.5 + 578.5j, 330.5 + 578.5j, 330.5 + 566.5j, 331.5 + 562.5j)
        _C(331.5 + 562.5j, 333.94 + 552.75j, 340.5 + 520.5j, 341.5 + 507.5j)
        _C(341.5 + 507.5j, 340.84 + 507.27j, 339.5 + 506.85j, 339.5 + 507.5j)
        _C(339.5 + 507.5j, 339.5 + 511.5j, 348.5 + 529.5j, 360.5 + 545.5j)
        _C(360.5 + 545.5j, 367.5 + 555.5j, 374.8 + 561.03j, 387.5 + 569.5j)
        _C(387.5 + 569.5j, 388.27 + 571.57j, 388.51 + 577.5j, 392.5 + 577.5j)
        _C(392.5 + 577.5j, 398.5 + 577.5j, 405.05 + 586.39j, 406.5 + 583.5j)
        _C(406.5 + 583.5j, 408.5 + 579.5j, 404.5 + 576.5j, 404.5 + 573.5j)
        _C(404.5 + 573.5j, 404.5 + 570.5j, 394.5 + 566.5j, 390.5 + 565.5j)
        _C(390.5 + 565.5j, 386.5 + 565.5j, 374.86 + 554.97j, 363.5 + 539.5j)
        _C(363.5 + 539.5j, 355.62 + 528.77j, 346.34 + 510.53j, 344.5 + 499.5j)
        _C(344.5 + 499.5j, 343.5 + 493.5j, 345.45 + 486.98j, 347.5 + 466.5j)
        _C(347.5 + 466.5j, 349.5 + 446.5j, 346.5 + 394.5j, 341.5 + 386.5j)
        _C(341.5 + 386.5j, 339.74 + 383.68j, 337.8 + 380.37j, 331.5 + 377.5j)
        _C(331.5 + 377.5j, 324.5 + 377.5j, 308.5 + 378.5j, 289.5 + 380.5j)
        _C(289.5 + 380.5j, 267.26 + 382.84j, 249.69 + 380.73j, 238.5 + 378.5j)
        _C(238.5 + 378.5j, 235.42 + 377.89j, 210.03 + 372.03j, 205.5 + 367.5j)
        _C(205.5 + 367.5j, 203.5 + 365.5j, 196.5 + 365.5j, 196.5 + 360.5j)
        _C(196.5 + 360.5j, 196.5 + 357.5j, 202.5 + 359.24j, 202.5 + 357.5j)
        _C(202.5 + 357.5j, 202.5 + 354.5j, 193.26 + 356.45j, 194.5 + 351.5j)
        _C(194.5 + 351.5j, 195.5 + 347.5j, 200.7 + 351.3j, 202.5 + 349.5j)
        _C(202.5 + 349.5j, 204.5 + 347.5j, 198.5 + 343.5j, 200.5 + 340.5j)
        _C(200.5 + 340.5j, 201.49 + 339.01j, 205.77 + 342.1j, 214.5 + 343.5j)
        _C(214.5 + 343.5j, 218.34 + 344.12j, 220.48 + 344.01j, 222.5 + 343.5j)
        _C(222.5 + 343.5j, 223.72 + 343.19j, 229.03 + 341.84j, 229.5 + 338.5j)
        _C(229.5 + 338.5j, 229.76 + 336.68j, 228.56 + 334.5j, 227.5 + 334.5j)
        _C(227.5 + 334.5j, 222.5 + 334.5j, 225.84 + 339.18j, 222.5 + 345.5j)
        _C(222.5 + 345.5j, 220.67 + 348.96j, 216.68 + 355.19j, 214.5 + 354.5j)
        _C(214.5 + 354.5j, 212.98 + 354.02j, 212.59 + 350.41j, 213.5 + 349.5j)
        _C(213.5 + 349.5j, 215.5 + 347.5j, 217.85 + 353.29j, 223.5 + 353.5j)
        _C(223.5 + 353.5j, 224.64 + 353.54j, 226 + 353.01j, 226.5 + 351.5j)
        _C(226.5 + 351.5j, 227.5 + 348.5j, 227.5 + 348.5j, 229.5 + 346.5j)
        _C(229.5 + 346.5j, 230.5 + 345.5j, 233.34 + 346.13j, 234.5 + 347.5j)
        _C(234.5 + 347.5j, 235.63 + 348.85j, 235.01 + 351.29j, 233.5 + 352.5j)
        _C(233.5 + 352.5j, 231.99 + 353.71j, 229.8 + 353.52j, 228.5 + 352.5j)
        _C(228.5 + 352.5j, 226.02 + 350.55j, 228.2 + 346.87j, 229.5 + 346.5j)
        _C(229.5 + 346.5j, 230.72 + 346.16j, 230.48 + 348.79j, 233.5 + 349.5j)
        _C(233.5 + 349.5j, 236.82 + 350.28j, 241.5 + 346.5j, 240.5 + 346.5j)
        _C(240.5 + 346.5j, 240.5 + 346.5j, 235.5 + 354.5j, 236.5 + 355.5j)
        _C(236.5 + 355.5j, 237.5 + 356.5j, 241.75 + 354.13j, 243.5 + 351.5j)
        _C(243.5 + 351.5j, 245.5 + 348.5j, 245.5 + 347.5j, 245.5 + 347.5j)
        _C(245.5 + 347.5j, 245.5 + 345.5j, 244.38 + 351.5j, 248.5 + 351.5j)
        _C(248.5 + 351.5j, 253.5 + 351.5j, 255.5 + 351.5j, 256.5 + 350.5j)
        _C(256.5 + 350.5j, 257.66 + 349.34j, 254.79 + 346.39j, 251.5 + 347.5j)
        _C(251.5 + 347.5j, 248.5 + 348.51j, 248.55 + 353.71j, 250.5 + 355.5j)
        _C(250.5 + 355.5j, 252.29 + 357.15j, 255.46 + 356.16j, 257.5 + 355.5j)
        _C(257.5 + 355.5j, 266.27 + 352.65j, 271.5 + 345.5j, 271.5 + 345.5j)
        _C(271.5 + 345.5j, 272.5 + 342.5j, 265.97 + 354.24j, 268.5 + 355.5j)
        _C(268.5 + 355.5j, 272.5 + 357.5j, 276.5 + 345.5j, 275.5 + 347.5j)
        _C(275.5 + 347.5j, 275.5 + 347.5j, 272.5 + 359.5j, 270.5 + 363.5j)
        _C(270.5 + 363.5j, 269.24 + 366.03j, 266.12 + 363.63j, 266.5 + 362.5j)
        _C(266.5 + 362.5j, 267.4 + 359.79j, 276.5 + 357.05j, 276.5 + 353.5j)
        _C(276.5 + 353.5j, 276.5 + 352.5j, 276.5 + 351.5j, 277.5 + 349.5j)
        _C(277.5 + 349.5j, 277.5 + 349.5j, 278.2 + 347.9j, 279.5 + 347.5j)
        _C(279.5 + 347.5j, 280.97 + 347.05j, 282.83 + 347.92j, 283.5 + 349.5j)
        _C(283.5 + 349.5j, 284.13 + 350.98j, 283.51 + 352.64j, 282.5 + 353.5j)
        _C(282.5 + 353.5j, 280.79 + 354.97j, 278.5 + 354.5j, 277.5 + 353.5j)
        _C(277.5 + 353.5j, 276.5 + 352.5j, 276.5 + 350.5j, 277.5 + 349.5j)
        _C(277.5 + 349.5j, 278.5 + 350.5j, 278.5 + 350.5j, 280.5 + 350.5j)
        _C(280.5 + 350.5j, 284.5 + 350.5j, 286.5 + 346.5j, 286.5 + 346.5j)
        _C(286.5 + 346.5j, 285.5 + 345.5j, 284.5 + 354.5j, 286.5 + 354.5j)
        _C(286.5 + 354.5j, 291.5 + 354.5j, 290.5 + 347.5j, 290.5 + 346.5j)
        _C(290.5 + 346.5j, 290.5 + 346.5j, 290.79 + 352.79j, 291.5 + 353.5j)
        _C(291.5 + 353.5j, 292.5 + 354.5j, 295.19 + 354.12j, 295.5 + 353.5j)
        _C(295.5 + 353.5j, 296.5 + 351.5j, 295.5 + 342.75j, 295.5 + 344.5j)
        _C(295.5 + 344.5j, 295.5 + 346.5j, 298.4 + 345.82j, 300.5 + 345.5j)
        _C(300.5 + 345.5j, 301.19 + 345.39j, 301.68 + 345.12j, 301.97 + 344.95j)
        _C(301.97 + 344.95j, 303.82 + 343.89j, 305.16 + 341.45j, 304.5 + 340.5j)
        _C(304.5 + 340.5j, 304 + 339.78j, 302.21 + 339.7j, 301.5 + 340.5j)
        _C(301.5 + 340.5j, 301 + 341.06j, 301.12 + 341.96j, 302.5 + 346.5j)
        _C(302.5 + 346.5j, 303.61 + 350.15j, 303.96 + 350.96j, 303.5 + 351.5j)
        _C(303.5 + 351.5j, 302.48 + 352.71j, 298.5 + 351.41j, 298.5 + 350.5j)
        _C(298.5 + 350.5j, 298.5 + 349.47j, 302.72 + 350.28j, 306.5 + 346.5j)
        _C(306.5 + 346.5j, 308.5 + 344.5j, 310.5 + 342.74j, 310.5 + 341.5j)
        _C(310.5 + 341.5j, 310.5 + 340.5j, 307.39 + 340.14j, 306.5 + 341.5j)
        _C(306.5 + 341.5j, 305.21 + 343.47j, 307.36 + 347.23j, 309.5 + 347.5j)
        _C(309.5 + 347.5j, 311.97 + 347.81j, 314.06 + 343.42j, 314.5 + 342.5j)
        _C(314.5 + 342.5j, 317.15 + 336.94j, 314.98 + 330.5j, 314.5 + 330.5j)
        _C(314.5 + 330.5j, 311.5 + 330.5j, 312.5 + 344.5j, 316.5 + 344.5j)
        _C(316.5 + 344.5j, 319.5 + 344.5j, 319.5 + 338.5j, 320.5 + 336.5j)
        _C(320.5 + 336.5j, 322.74 + 332.03j, 322.5 + 325.5j, 320.5 + 325.5j)
        _C(320.5 + 325.5j, 317.5 + 325.5j, 318.24 + 330.74j, 319.5 + 335.5j)
        _C(319.5 + 335.5j, 320.83 + 340.52j, 324.39 + 342.55j, 323.5 + 344.5j)
        _C(323.5 + 344.5j, 322.98 + 345.65j, 320.56 + 345.56j, 319.5 + 344.5j)
        _C(319.5 + 344.5j, 318.5 + 343.5j, 318.5 + 337.5j, 320.5 + 336.5j)
        _C(320.5 + 336.5j, 326.91 + 333.3j, 329.64 + 330.89j, 332.5 + 328.5j)
        _C(332.5 + 328.5j, 335.54 + 325.97j, 336.13 + 323.92j, 338.5 + 323.5j)
        _C(338.5 + 323.5j, 341.25 + 323.02j, 342.47 + 325.81j, 345.5 + 325.5j)
        _C(345.5 + 325.5j, 349.15 + 325.13j, 352.21 + 320.57j, 351.5 + 319.5j)
        _C(351.5 + 319.5j, 350.88 + 318.57j, 346.8 + 319.39j, 344.5 + 321.5j)
        _C(344.5 + 321.5j, 339.78 + 325.83j, 340.21 + 337.69j, 345.5 + 343.5j)
        _C(345.5 + 343.5j, 355.5 + 354.5j, 388.5 + 355.5j, 400.5 + 335.5j)
        _C(400.5 + 335.5j, 401.43 + 333.94j, 405.5 + 323.5j, 403.5 + 317.5j)
        _C(403.5 + 317.5j, 401.58 + 311.73j, 391.27 + 309.43j, 390.5 + 312.5j)
        _C(390.5 + 312.5j, 389.5 + 316.5j, 398.5 + 317.5j, 403.5 + 317.5j)
        _C(403.5 + 317.5j, 410.5 + 317.5j, 439.52 + 312.44j, 447.5 + 288.5j)
        _C(447.5 + 288.5j, 454.5 + 267.5j, 449.79 + 258.28j, 441.5 + 247.5j)
        _C(441.5 + 247.5j, 431.5 + 234.5j, 410.13 + 235.53j, 409.5 + 242.5j)
        _C(409.5 + 242.5j, 409.35 + 244.2j, 409.64 + 245.56j, 410.32 + 246.65j)
        _C(410.32 + 246.65j, 414.58 + 253.52j, 431.18 + 251.91j, 441.5 + 247.5j)
        _C(441.5 + 247.5j, 453.43 + 242.41j, 467.2 + 229.2j, 467.5 + 210.5j)
        _C(467.5 + 210.5j, 467.77 + 193.58j, 456.96 + 175.19j, 439.5 + 171.5j)
        _C(439.5 + 171.5j, 420.96 + 167.58j, 398.25 + 180.38j, 403.5 + 186.5j)
        _C(403.5 + 186.5j, 409.5 + 193.5j, 429.5 + 184.5j, 439.5 + 171.5j)
        _C(439.5 + 171.5j, 449.19 + 158.9j, 461.5 + 135.5j, 444.5 + 114.5j)
        _C(444.5 + 114.5j, 427.56 + 93.58j, 410.41 + 95.15j, 390.5 + 102.5j)
        _C(390.5 + 102.5j, 377.21 + 107.4j, 365.97 + 118.11j, 370.5 + 121.5j)
        _C(370.5 + 121.5j, 374.5 + 124.5j, 386.14 + 115.57j, 390.5 + 102.5j)
        _C(390.5 + 102.5j, 397.5 + 81.5j, 400.5 + 59.5j, 384.5 + 45.5j)
        _C(384.5 + 45.5j, 371.19 + 33.85j, 355.31 + 39.88j, 344.5 + 48.5j)
        _C(344.5 + 48.5j, 332.72 + 57.89j, 324.5 + 73.5j, 331.5 + 76.5j)
        _C(331.5 + 76.5j, 337.31 + 78.99j, 345.59 + 62.66j, 344.5 + 48.5j)
        _C(344.5 + 48.5j, 343.5 + 35.5j, 335.75 + 16.91j, 317.5 + 16.5j)
        _C(317.5 + 16.5j, 302.54 + 16.16j, 288.57 + 30.12j, 286.5 + 41.5j)
        _C(286.5 + 41.5j, 284.5 + 52.5j, 286.5 + 75.5j, 295.5 + 71.5j)
        _C(295.5 + 71.5j, 301.63 + 68.78j, 294.85 + 52.05j, 286.5 + 41.5j)
        _C(286.5 + 41.5j, 267.5 + 17.5j, 238.92 + 9.36j, 208.5 + 19.5j)
        _C(208.5 + 19.5j, 184.5 + 27.5j, 174.5 + 45.5j, 181.5 + 78.5j)
        _C(181.5 + 78.5j, 186.71 + 103.04j, 212.77 + 122.67j, 218.5 + 113.5j)
        _C(218.5 + 113.5j, 223.5 + 105.5j, 200.5 + 81.5j, 181.5 + 78.5j)
        _C(181.5 + 78.5j, 158.49 + 74.87j, 120.15 + 85.46j, 112.5 + 113.5j)
        _C(112.5 + 113.5j, 109.5 + 124.5j, 116.05 + 143.32j, 134.5 + 156.5j)
        _C(134.5 + 156.5j, 155.5 + 171.5j, 181.46 + 173.17j, 184.5 + 159.5j)
        _C(184.5 + 159.5j, 186.5 + 150.5j, 161.5 + 139.5j, 134.5 + 156.5j)
        _C(134.5 + 156.5j, 113.14 + 169.95j, 102.72 + 188.47j, 105.5 + 213.5j)
        _C(105.5 + 213.5j, 107.5 + 231.5j, 120.12 + 244.79j, 140.5 + 250.5j)
        _C(140.5 + 250.5j, 165.5 + 257.5j, 179.14 + 245.54j, 178.5 + 238.5j)
        _C(178.5 + 238.5j, 177.5 + 227.5j, 152.5 + 231.5j, 140.5 + 250.5j)
        _C(140.5 + 250.5j, 129.69 + 267.61j, 124.78 + 296.54j, 141.5 + 311.5j)
        _C(141.5 + 311.5j, 160.5 + 328.5j, 188.81 + 318.81j, 197.5 + 304.5j)
        _C(197.5 + 304.5j, 201.28 + 298.27j, 201.5 + 288.5j, 198.5 + 288.5j)
        _C(198.5 + 288.5j, 194.38 + 288.5j, 191.1 + 299.7j, 197.5 + 304.5j)
        _C(197.5 + 304.5j, 216.58 + 318.81j, 268.18 + 326.21j, 305.5 + 316.5j)
        _C(305.5 + 316.5j, 317.17 + 313.47j, 327.5 + 306.5j, 327.5 + 303.5j)
        _C(327.5 + 303.5j, 327.5 + 292.45j, 328.4 + 286.81j, 335.5 + 268.5j)
        _C(335.5 + 268.5j, 335.73 + 267.9j, 339.37 + 258.76j, 347.38 + 250.05j)
        _C(347.38 + 250.05j, 350.15 + 247.04j, 352.1 + 245.53j, 354.5 + 244.5j)
        _C(354.5 + 244.5j, 361.52 + 241.49j, 369.53 + 243.8j, 369.5 + 244.5j)
        _C(369.5 + 244.5j, 369.47 + 245.2j, 361.28 + 247.11j, 354.5 + 244.5j)
        _C(354.5 + 244.5j, 344.46 + 240.63j, 338.9 + 227.4j, 338.5 + 216.5j)
        _C(338.5 + 216.5j, 338.12 + 206.13j, 342.23 + 192.45j, 351.5 + 188.5j)
        _C(351.5 + 188.5j, 357.84 + 185.8j, 365.51 + 188.11j, 365.5 + 188.5j)
        _C(365.5 + 188.5j, 365.49 + 188.88j, 358.31 + 190.12j, 351.5 + 188.5j)
        _C(351.5 + 188.5j, 335.88 + 184.78j, 326 + 166.83j, 325.5 + 155.5j)
        _C(325.5 + 155.5j, 325.33 + 151.61j, 326.19 + 148.11j, 326.19 + 148.11j)
        _C(326.19 + 148.11j, 327.41 + 143.13j, 329.82 + 139.96j, 332.5 + 136.5j)
        _C(332.5 + 136.5j, 335.47 + 132.67j, 339.01 + 128.1j, 342.28 + 128.78j)
        _C(342.28 + 128.78j, 342.56 + 128.84j, 343.33 + 129j, 343.5 + 129.5j)
        _C(343.5 + 129.5j, 344.01 + 131.06j, 338.41 + 135.12j, 332.5 + 136.5j)
        _C(332.5 + 136.5j, 329.63 + 137.17j, 326.61 + 136.83j, 320.58 + 136.16j)
        _C(320.58 + 136.16j, 315.41 + 135.58j, 311.51 + 135.12j, 306.5 + 133.5j)
        _C(306.5 + 133.5j, 302.93 + 132.34j, 300.31 + 131.5j, 297.3 + 129.48j)
        _C(297.3 + 129.48j, 295.34 + 128.17j, 288.47 + 123.57j, 287.5 + 116.5j)
        _C(287.5 + 116.5j, 286.72 + 110.79j, 290.07 + 105.38j, 290.5 + 105.5j)
        _C(290.5 + 105.5j, 290.92 + 105.62j, 290.68 + 111.61j, 287.5 + 116.5j)
        _C(287.5 + 116.5j, 283.12 + 123.24j, 275.05 + 125.02j, 272.52 + 125.59j)
        _C(272.52 + 125.59j, 268.74 + 126.43j, 262.59 + 127.79j, 258.5 + 124.5j)
        _C(258.5 + 124.5j, 253.92 + 120.82j, 253.71 + 112.76j, 254.5 + 112.5j)
        _C(254.5 + 112.5j, 255.26 + 112.25j, 259.55 + 118.51j, 258.5 + 124.5j)
        _C(258.5 + 124.5j, 257.5 + 130.19j, 252.06 + 133.54j, 250.5 + 134.5j)
        _C(250.5 + 134.5j, 242.46 + 139.45j, 233.58 + 137.11j, 231.5 + 136.5j)

        # 左眼
        _Mv(211.5 + 215.5j)
        _C(211.5 + 215.5j, 210.76 + 219.54j, 213.75 + 223.25j, 217.5 + 223.5j)
        _C(217.5 + 223.5j, 221.19 + 223.74j, 224.62 + 220.55j, 224.5 + 216.5j)

        # 右眼
        _Mv(289.5 + 218.5j)
        _C(289.5 + 218.5j, 289.38 + 222.46j, 292.06 + 225.83j, 295.5 + 226.5j)
        _C(295.5 + 226.5j, 299.55 + 227.29j, 303.93 + 224.21j, 304.5 + 219.5j)

        # 鼻子和嘴
        _Mv(205.5 + 265.5j)
        _C(205.5 + 265.5j, 205.77 + 265.6j, 209.73 + 267.27j, 212.5 + 264.5j)
        _C(212.5 + 264.5j, 215.5 + 261.5j, 215.5 + 259.87j, 215.5 + 259.5j)
        _C(215.5 + 259.5j, 215.5 + 256.5j, 215.5 + 247.5j, 215.5 + 247.5j)
        _C(215.5 + 247.5j, 215.5 + 247.5j, 204.5 + 242.5j, 205.5 + 238.5j)
        _C(205.5 + 238.5j, 206.46 + 234.65j, 228.15 + 233.8j, 229.5 + 236.5j)
        _C(229.5 + 236.5j, 231.5 + 240.5j, 215.5 + 247.5j, 215.5 + 247.5j)
        _L(215.5 + 247.5j, 215.5 + 259.5j)
        _C(215.5 + 259.5j, 217.09 + 264.26j, 218.39 + 267.06j, 220.61 + 268.65j)
        _C(220.61 + 268.65j, 223.77 + 270.91j, 227.22 + 270.64j, 229.5 + 270.5j)
        _C(229.5 + 270.5j, 235.43 + 270.14j, 239.64 + 267.06j, 241.5 + 265.5j)
        _L(241.5 + 265.5j, 241.5 + 263.5j)
        _C(241.5 + 263.5j, 242.5 + 255.43j, 248.55 + 251.15j, 249.5 + 250.5j)
        _C(249.5 + 250.5j, 248.55 + 251.15j, 242.5 + 255.43j, 241.5 + 263.5j)
        _C(241.5 + 263.5j, 240.35 + 272.76j, 246.86 + 278.91j, 247.5 + 279.5j)

        # 手
        _Mv(326.5 + 305.5j)
        _C(326.5 + 305.5j, 329.5 + 304.5j, 331.98 + 304.34j, 332.5 + 305.5j)
        _C(332.5 + 305.5j, 333.23 + 307.13j, 329.69 + 309.69j, 330.5 + 310.5j)
        _C(330.5 + 310.5j, 332.5 + 312.5j, 336.5 + 307.5j, 338.5 + 309.5j)
        _C(338.5 + 309.5j, 340.5 + 311.5j, 332.99 + 316j, 334.5 + 317.5j)
        _C(334.5 + 317.5j, 335.6 + 318.59j, 339.38 + 315.52j, 340.5 + 316.5j)
        _C(340.5 + 316.5j, 341.31 + 317.21j, 341.5 + 319.5j, 338.5 + 323.5j)
        _pu()

        _Mv(203.5 + 379.5j)
        # tur.hideturtle()  # 隐藏乌龟图标
        turtle.update()

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############太极八卦################
#####################################

def _taiji_draw_circle():
    turtle.penup()
    turtle.right(90)
    turtle.fd(50)
    turtle.pendown()

    turtle.fillcolor('black')
    turtle.begin_fill()
    turtle.left(90)
    turtle.circle(100, 180)

    turtle.circle(50, -180)
    turtle.left(180)
    turtle.circle(50, 180)
    turtle.end_fill()

    turtle.fillcolor('white')
    turtle.circle(100, -180)

    turtle.penup()
    turtle.goto(0, -16)
    turtle.pendown()

    turtle.fillcolor('white')
    turtle.left(180)
    turtle.begin_fill()
    turtle.circle(16)
    turtle.end_fill()

    turtle.penup()
    turtle.goto(0, 84)
    turtle.pendown()

    turtle.fillcolor('black')
    turtle.begin_fill()
    turtle.circle(16)
    turtle.end_fill()


def _taiji_draw_qian():
    turtle.penup()
    turtle.goto(-40, 250)
    turtle.pendown()
    turtle.fd(80)

    turtle.penup()
    turtle.goto(-40, 230)
    turtle.pendown()
    turtle.fd(30)
    turtle.color('white')
    turtle.fd(20)
    turtle.color('black')
    turtle.fd(30)

    turtle.penup()
    turtle.goto(-40, 210)
    turtle.pendown()
    turtle.fd(80)


def _taiji_draw_xun():
    lenght = [200, 180, 160]
    for i in lenght:
        turtle.penup()
        turtle.home()
        turtle.goto(0, 50)
        turtle.left(45)
        turtle.fd(i)

        turtle.left(90)
        turtle.fd(40)
        turtle.pendown()
        turtle.right(180)
        turtle.fd(30)
        turtle.color('white')
        turtle.fd(20)
        turtle.color('black')
        turtle.fd(30)


def _taiji_draw_kan():
    turtle.penup()
    turtle.home()
    turtle.goto(0, 50)
    turtle.fd(200)
    turtle.left(90)
    turtle.fd(40)
    turtle.right(180)
    turtle.pendown()
    turtle.fd(30)
    turtle.color('white')
    turtle.fd(20)
    turtle.color('black')
    turtle.fd(30)

    turtle.penup()
    turtle.goto(180, 90)
    turtle.pendown()
    turtle.fd(80)

    turtle.penup()
    turtle.goto(160, 90)
    turtle.pendown()
    turtle.fd(80)


def _taiji_draw_gen():
    lenght = [200, 180, 160]
    for i in lenght:
        turtle.penup()
        turtle.home()
        turtle.goto(0, 50)
        turtle.right(45)
        turtle.fd(i)
        turtle.left(90)
        turtle.fd(40)
        turtle.right(180)
        turtle.pendown()
        turtle.fd(80)


def _taiji_draw_kun():
    turtle.penup()
    turtle.home()
    turtle.goto(-40, -150)
    turtle.pendown()
    turtle.fd(30)
    turtle.color('white')
    turtle.fd(20)
    turtle.color('black')
    turtle.fd(30)

    turtle.penup()
    turtle.goto(-40, -130)
    turtle.pendown()
    turtle.fd(80)

    turtle.penup()
    turtle.goto(-40, -110)
    turtle.pendown()
    turtle.fd(35)
    turtle.color('white')
    turtle.fd(10)
    turtle.color('black')
    turtle.fd(35)


def _taiji_draw_zhen():
    for i in range(3):
        turtle.penup()
        turtle.home()
        turtle.goto(0, 50)
        turtle.right(135)
        turtle.fd(200 - 20 * i)
        turtle.left(90)
        turtle.fd(40)
        turtle.right(180)
        turtle.pendown()
        if i == 0:
            turtle.fd(80)
        else:
            turtle.fd(30)
            turtle.color('white')
            turtle.fd(20)
            turtle.color('black')
            turtle.fd(30)


def _taiji_draw_li():
    turtle.penup()
    turtle.home()

    turtle.goto(-200, 10)
    turtle.pendown()
    turtle.left(90)
    turtle.fd(30)
    turtle.color('white')
    turtle.fd(20)
    turtle.color('black')
    turtle.fd(30)

    turtle.penup()
    turtle.goto(-180, 10)
    turtle.pendown()
    turtle.fd(30)
    turtle.color('white')
    turtle.fd(20)
    turtle.color('black')
    turtle.fd(30)

    turtle.penup()
    turtle.goto(-160, 10)
    turtle.pendown()
    turtle.fd(80)


def _taiji_draw_dui():
    length = [200, 180, 160]
    for i in length:
        turtle.penup()
        turtle.home()
        turtle.goto(0, 50)
        turtle.left(135)
        turtle.fd(i)
        turtle.left(90)
        turtle.fd(40)
        turtle.left(180)
        turtle.pendown()
        if i == 160:
            turtle.fd(30)
            turtle.color('white')
            turtle.fd(20)
            turtle.color('black')
            turtle.fd(30)
        else:
            turtle.fd(80)


def taiji():
    try:
        turtle.bgcolor("white")
        turtle.speed(10)
        turtle.pensize(8)
        # turtle.shape('turtle')

        _taiji_draw_circle()
        _taiji_draw_qian()
        _taiji_draw_xun()
        _taiji_draw_kan()
        _taiji_draw_gen()
        _taiji_draw_kun()
        _taiji_draw_zhen()
        _taiji_draw_li()
        _taiji_draw_dui()
        turtle.hideturtle()
        # turtle.mainloop()//去掉注释则窗口不自动关闭
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############小黄人###################
#####################################

# =======头======
def _xhren_head():
    turtle.penup()
    turtle.fillcolor("#FFEE26")
    turtle.goto(-130, 10)
    turtle.pendown()
    turtle.begin_fill()
    turtle.seth(81)
    turtle.fd(90)
    turtle.seth(100)
    turtle.circle(-500, 3)
    turtle.circle(-100, 10)
    turtle.circle(-200, 25)
    turtle.circle(-110, 20)
    turtle.circle(-140, 30)
    turtle.circle(-180, 30)
    turtle.circle(-200, 20)
    turtle.circle(-140, 10)
    turtle.circle(-160, 50)
    turtle.seth(85)
    turtle.fd(-148)
    turtle.seth(-112)
    turtle.circle(-250, 14)
    turtle.fd(200)
    turtle.right(80)
    turtle.fd(190)
    turtle.seth(110)
    turtle.circle(-200, 7)
    turtle.circle(-130, 30)
    turtle.end_fill()


# =======肚兜======
# ====后脚=====
def _xhren_houjiao():
    turtle.begin_fill()

    turtle.penup()
    turtle.goto(-120, -250)
    turtle.pendown()
    turtle.fillcolor("#030003")
    turtle.setheading(-135)
    turtle.circle(60, 20)
    turtle.fd(35)
    turtle.circle(20, 160)
    turtle.circle(100, 10)
    turtle.fd(20)
    turtle.goto(-120, -250)

    turtle.end_fill()


def _xhren_houtui():
    turtle.begin_fill()
    turtle.color("black", "#0045D9")
    turtle.penup()
    turtle.goto(-50, -300)
    turtle.pendown()
    turtle.setheading(-150)
    turtle.circle(-80, 60)
    turtle.setheading(90)
    turtle.circle(-40, 67)
    turtle.seth(-30)
    turtle.goto(-50, -300)
    turtle.end_fill()


# ===衣服====
def _xhren_yifu():
    turtle.begin_fill()

    turtle.penup()
    turtle.goto(-45, -70)
    turtle.pendown()
    turtle.fillcolor("#0045D9")
    turtle.setheading(-15)

    turtle.circle(500, 5)
    turtle.circle(400, 26)

    turtle.seth(-112)
    turtle.circle(-250, 7)
    turtle.seth(-69)
    turtle.circle(-250, 7)
    turtle.right(15)
    turtle.circle(-320, 18)
    turtle.circle(-330, 10)
    turtle.fd(80)
    turtle.right(81)
    turtle.fd(190)
    turtle.seth(141)
    turtle.circle(-180, 15)
    turtle.circle(-150, 30)
    turtle.right(6)
    turtle.circle(-90, 15)
    turtle.seth(-45)
    turtle.circle(50, 10)
    turtle.seth(-30)
    turtle.circle(200, 20)
    turtle.circle(150, 10)
    turtle.seth(92)
    turtle.circle(500, 10)

    turtle.setheading(75)
    turtle.goto(-45, -70)

    turtle.end_fill()


# =====口袋=====
def _xhren_koudai():
    turtle.begin_fill()
    turtle.penup()
    turtle.goto(52, -120)
    turtle.pendown()
    turtle.fillcolor("#BFC5AD")
    turtle.seth(-15)
    turtle.circle(200, 25)
    turtle.seth(-88)
    turtle.circle(-200, 18)
    turtle.seth(-150)
    turtle.circle(-90, 5)
    turtle.right(10)
    turtle.circle(-90, 45)
    turtle.right(20)
    turtle.circle(-50, 50)
    turtle.goto(52, -120)
    turtle.end_fill()

    turtle.begin_fill()
    turtle.penup()
    turtle.goto(70, -155)
    turtle.pendown()
    turtle.fillcolor("#0045D9")
    turtle.circle(-25)
    turtle.end_fill()

    turtle.penup()
    turtle.goto(120, -160)
    turtle.pencolor("#5C7F58")
    turtle.pendown()
    turtle.seth(180)
    turtle.fd(20)
    turtle.right(60)
    turtle.circle(6, 340)
    turtle.pencolor("black")


# ======右手======
def _xhren_youshou():
    turtle.begin_fill()
    turtle.fillcolor("#FFEE26")
    turtle.pencolor("black")
    turtle.penup()
    turtle.goto(-130, 10)
    turtle.pendown()
    turtle.goto(-130, -25)
    turtle.seth(130)
    turtle.circle(130, 20)
    turtle.circle(20, 50)
    turtle.right(10)
    turtle.pencolor("black")
    turtle.circle(120, 20)
    turtle.circle(90, 30)
    turtle.seth(-25)
    turtle.fd(33)
    turtle.seth(40)
    turtle.fd(35)
    turtle.circle(-30, 30)
    turtle.circle(-15, 60)
    turtle.right(5)
    turtle.fd(80)
    turtle.end_fill()


def _xhren_youzhua():
    turtle.begin_fill()
    turtle.fillcolor("#BEC5B3")
    turtle.penup()
    turtle.goto(-255, -40)
    turtle.pendown()
    turtle.seth(-120)
    turtle.circle(-100, 10)
    turtle.right(60)
    turtle.circle(20, 60)
    turtle.circle(10, 90)
    turtle.right(60)
    turtle.fd(10)
    turtle.circle(20, 100)
    turtle.left(10)
    turtle.fd(15)
    turtle.seth(50)
    turtle.circle(-60, 30)
    turtle.left(60)
    turtle.circle(10, 60)
    turtle.fd(5)
    turtle.right(90)
    turtle.fd(21)
    turtle.goto(-255, -40)
    turtle.end_fill()
    # 黑色


# ======前腿====
def _xhren_qiantui():
    turtle.begin_fill()

    turtle.penup()
    turtle.goto(-50, -295)
    turtle.pendown()
    turtle.fillcolor("#0045D9")
    # turtle.fillcolor("red")
    turtle.setheading(-30)
    turtle.fd(127)
    turtle.seth(62)
    turtle.fd(60)
    turtle.seth(155)
    turtle.circle(300, 22)
    turtle.pencolor("#0045D9")
    turtle.goto(-49, -294)
    turtle.pencolor("black")
    turtle.goto(-50, -295)

    turtle.end_fill()


# ====前脚======
def _xhren_qianjiao():
    turtle.begin_fill()

    turtle.penup()
    turtle.goto(140, -260)
    turtle.pendown()
    turtle.fillcolor("#030003")
    turtle.seth(110)
    turtle.circle(20, 120)
    turtle.seth(-120)
    turtle.circle(500, 12)
    turtle.circle(20, 82)
    turtle.goto(140, -260)

    turtle.end_fill()


def _xhren_jiaodi():
    turtle.begin_fill()

    turtle.penup()
    turtle.goto(140, -260)
    turtle.pendown()
    turtle.fillcolor("#BFC5AD")
    turtle.seth(150)
    turtle.circle(20, 95)
    turtle.seth(-120)
    turtle.circle(500, 10)
    turtle.seth(-30)
    turtle.circle(-15, 60)
    turtle.seth(-112)
    turtle.fd(17)
    turtle.left(90)
    turtle.circle(30, 90)

    turtle.seth(70)
    turtle.circle(-50, 25)
    turtle.fd(7)
    turtle.circle(66, 60)
    turtle.circle(40, 10)
    turtle.goto(140, -260)

    turtle.end_fill()


def _xhren_xie():
    turtle.pencolor("black")
    turtle.penup()
    turtle.goto(83, -353)
    turtle.pendown()
    turtle.seth(-30)
    turtle.fd(31)


def _xhren_yanjing():
    turtle.begin_fill()

    turtle.penup()
    turtle.goto(-125, 140)
    turtle.pendown()
    turtle.fillcolor("#000000")
    turtle.pencolor("black")
    turtle.seth(100)
    turtle.circle(-25, 80)
    turtle.seth(40)
    turtle.circle(-200, 23)
    turtle.seth(-90)
    turtle.fd(45)
    turtle.seth(195)
    turtle.circle(200, 27)
    turtle.seth(150)
    turtle.circle(-12, 90)
    turtle.goto(-125, 140)
    turtle.end_fill()
    # 黑色
    turtle.begin_fill()

    turtle.penup()
    turtle.goto(-39, 205)
    turtle.pendown()
    turtle.fillcolor("#E6E8FA")
    turtle.setheading(90)
    turtle.circle(-8, 180)
    turtle.seth(-90)
    turtle.fd(45)
    turtle.circle(-8, 180)
    turtle.goto(-39, 205)
    turtle.end_fill()
    # 银色
    turtle.begin_fill()

    turtle.penup()
    turtle.goto(-23, 160)
    turtle.pendown()
    turtle.fillcolor("#E6E8FA")
    turtle.seth(-78)
    turtle.circle(85, 130)
    turtle.goto(-23, 160)
    turtle.end_fill()
    # 银色
    turtle.begin_fill()
    turtle.penup()
    turtle.goto(-23, 190)
    turtle.pendown()
    turtle.fillcolor("#E6E8FA")
    turtle.seth(-90)
    turtle.circle(90)
    turtle.end_fill()
    # 银色
    turtle.begin_fill()
    turtle.penup()
    turtle.goto(155, 205)
    turtle.pendown()
    turtle.fillcolor("#000000")
    turtle.seth(-15)
    turtle.circle(-100, 20)
    turtle.seth(-60)
    turtle.circle(-105, 25)
    turtle.seth(160)
    turtle.circle(200, 13.5)
    turtle.seth(75)
    turtle.circle(90, 20)
    turtle.goto(155, 205)
    turtle.end_fill()
    # 黑色
    turtle.begin_fill()
    turtle.penup()
    turtle.goto(128, 195)
    turtle.pendown()
    turtle.fillcolor("#ffffff")
    turtle.circle(60)
    turtle.end_fill()
    # 白色
    turtle.begin_fill()
    turtle.penup()
    turtle.goto(110, 150)
    turtle.pendown()
    turtle.fillcolor("#000000")
    turtle.seth(70)
    turtle.circle(70, 110)
    turtle.seth(20)
    turtle.circle(-60, 150)
    turtle.end_fill()
    # 黑色
    turtle.begin_fill()
    turtle.penup()
    turtle.goto(25, 210)
    turtle.pendown()
    turtle.fillcolor("#B85300")
    turtle.circle(20)
    turtle.end_fill()
    # 白色
    turtle.begin_fill()
    turtle.penup()
    turtle.goto(32, 204)
    turtle.pendown()
    turtle.fillcolor("#000000")
    turtle.circle(8)
    turtle.end_fill()
    # 黑色


# ====嘴巴=====
def _xhren_zui():
    turtle.begin_fill()
    turtle.penup()

    turtle.fillcolor("#FF1305")
    turtle.goto(-25, 60)
    turtle.pendown()
    turtle.right(30)
    turtle.circle(-30, 70)
    turtle.left(5)
    turtle.circle(300, 20)
    turtle.circle(120, 20)
    turtle.seth(-70)
    turtle.circle(-50, 60)
    turtle.left(10)
    turtle.circle(-100, 30)
    turtle.circle(-60, 35)
    turtle.right(8)
    turtle.circle(-200, 15)
    turtle.circle(-100, 15)
    turtle.circle(-50, 25)
    turtle.circle(-200, 10)
    turtle.goto(-25, 60)
    turtle.end_fill()


# =====衣领====
def _xhren_yiling():
    turtle.begin_fill()
    turtle.penup()

    turtle.fillcolor("#0045D9")
    turtle.goto(-130, 10)
    turtle.pendown()
    turtle.setheading(-59)
    turtle.circle(225, 38)
    turtle.setheading(-100)
    turtle.forward(28)
    turtle.setheading(160)
    turtle.circle(-255, 35)
    turtle.setheading(90)
    turtle.circle(-30, 45)
    turtle.goto(-130, 10)
    turtle.end_fill()


# ====扣子====
def _xhren_zuokou():
    turtle.begin_fill()
    turtle.penup()

    turtle.fillcolor("#FFFFFF")
    turtle.goto(-40, -80)
    turtle.pendown()
    turtle.seth(0)
    turtle.circle(-9, 360)
    turtle.end_fill()


# ====左衣领====
def _xhren_zuoyl():
    turtle.begin_fill()
    turtle.penup()

    turtle.fillcolor("#0045D9")
    turtle.goto(191, -40)
    turtle.pendown()
    turtle.seth(-112)
    turtle.circle(-250, 17)
    turtle.seth(-68)
    turtle.fd(25)
    turtle.seth(49)
    turtle.circle(130, 36)
    turtle.goto(191, -40)
    turtle.end_fill()

    turtle.begin_fill()
    turtle.penup()
    turtle.fillcolor("#FFFFFF")
    turtle.goto(169, -93)
    turtle.pendown()
    turtle.seth(0)
    turtle.circle(-9, 360)
    turtle.end_fill()


# ====左手====
def _xhren_zuoshou():
    turtle.begin_fill()
    turtle.penup()

    turtle.fillcolor("#FFEE26")
    turtle.goto(195, -56)
    turtle.pendown()
    turtle.seth(-8)
    turtle.circle(150, 15)
    turtle.circle(25, 40)
    turtle.left(2)
    turtle.fd(60)
    turtle.right(85)
    turtle.fd(28)
    turtle.right(92)
    turtle.fd(45)
    turtle.circle(-100, 20)
    turtle.circle(-80, 40)
    turtle.circle(80, 13)
    turtle.goto(195, -56)
    turtle.end_fill()


# ====左掌====
def _xhren_zuozhua():
    turtle.begin_fill()
    turtle.penup()

    turtle.fillcolor("#BEC5B3")

    turtle.goto(295, 25)
    turtle.pendown()
    turtle.seth(55)
    turtle.fd(-30)
    turtle.right(110)
    turtle.circle(80, 38)
    turtle.left(90)
    turtle.fd(10)
    turtle.seth(20)
    turtle.circle(100, 30)
    turtle.circle(35, 180)
    turtle.goto(295, 25)
    turtle.end_fill()

    turtle.begin_fill()
    turtle.fillcolor("#BEC5B3")
    turtle.seth(140)
    turtle.circle(-15)
    turtle.end_fill()


def xiaohuangren():
    try:
        turtle.screensize(750, 780, "#f0f0f0")
        turtle.pensize(4)
        turtle.speed(10)
        _xhren_head()
        _xhren_zui()
        _xhren_youshou()
        _xhren_yanjing()
        _xhren_youzhua()
        _xhren_houjiao()
        _xhren_houtui()
        _xhren_yifu()
        _xhren_koudai()
        _xhren_qiantui()
        _xhren_qianjiao()
        _xhren_jiaodi()
        _xhren_xie()
        _xhren_yiling()
        _xhren_zuokou()
        _xhren_zuoshou()
        _xhren_zuozhua()
        _xhren_zuoyl()
        turtle.penup()
        turtle.goto(80, -40)
        turtle.pendown()
        turtle.seth(100)
        turtle.circle(90, 85)

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############熊本熊###################
#####################################

# 耳朵的环
def _xbx_circle(x, y, color, size):
    turtle.setheading(0)
    turtle.up()
    turtle.goto(x, y)
    turtle.down()
    turtle.begin_fill()
    turtle.fillcolor(color)
    turtle.circle(size)
    turtle.end_fill()


# 耳朵
def _xbx_ear():
    _xbx_circle(150, 250, "black", 50)
    _xbx_circle(150, 260, "white", 35)
    _xbx_circle(-150, 250, "black", 50)
    _xbx_circle(-150, 260, "white", 35)


def _xbx_body():
    turtle.begin_fill()
    turtle.fillcolor("black")
    turtle.up()
    turtle.goto(200, 150)
    turtle.down()
    turtle.left(90)
    turtle.circle(200, 180)
    # print(turtle.pos())
    turtle.goto(-200, -150)
    turtle.circle(200, 180)
    turtle.goto(200, 150)
    turtle.end_fill()


# 左手
def _xbx_zuoshou():
    turtle.up()
    turtle.goto(200, 50)
    turtle.down()
    turtle.right(90)
    turtle.begin_fill()
    turtle.fillcolor("black")
    turtle.fd(200)
    turtle.left(90)
    turtle.fd(50)
    turtle.left(90)
    turtle.fd(200)
    turtle.end_fill()
    turtle.up()
    turtle.goto(420, 125)
    turtle.down()
    turtle.begin_fill()
    turtle.fillcolor("black")
    turtle.circle(50)
    turtle.end_fill()


# 右手
def _xbx_youshou():
    turtle.up()
    turtle.goto(-200, 50)
    turtle.down()
    turtle.begin_fill()
    turtle.fillcolor("black")
    turtle.fd(200)
    turtle.right(90)
    turtle.fd(50)
    turtle.right(90)
    turtle.fd(200)
    turtle.end_fill()
    turtle.up()
    turtle.goto(-420, 25)
    turtle.down()
    turtle.begin_fill()
    turtle.fillcolor("black")
    turtle.circle(50)
    turtle.end_fill()


# 鼻子
def _xbx_nose():
    turtle.up()
    turtle.goto(0, 25)
    turtle.down()
    turtle.begin_fill()
    turtle.circle(110)
    turtle.fillcolor("white")
    turtle.end_fill()
    turtle.up()
    turtle.goto(0, 150)  # 鼻头
    turtle.down()
    turtle.begin_fill()
    turtle.circle(20)
    turtle.fillcolor("black")
    turtle.end_fill()


# 腮红
def _xbx_cheek():
    turtle.up()
    turtle.goto(-160, 80)
    turtle.down()
    turtle.begin_fill()
    turtle.fillcolor("red")
    turtle.circle(38)
    turtle.end_fill()

    turtle.up()
    turtle.goto(160, 80)
    turtle.down()
    turtle.begin_fill()
    turtle.fillcolor("red")
    turtle.circle(38)
    turtle.end_fill()


# 眼睛
def _xbx_eyes():
    turtle.up()
    turtle.goto(-110, 200)
    turtle.down()
    turtle.begin_fill()
    turtle.fillcolor("white")
    turtle.circle(40)
    turtle.end_fill()

    turtle.up()
    turtle.goto(110, 200)
    turtle.down()
    turtle.begin_fill()
    turtle.fillcolor("white")
    turtle.circle(40)
    turtle.end_fill()


# 黑眼珠
def _xbx_balckeyes():
    turtle.up()
    turtle.goto(-110, 240)
    turtle.down()
    turtle.circle(3)

    turtle.up()
    turtle.goto(110, 240)
    turtle.down()
    turtle.circle(3)


# 眉毛
def _xbx_eyebrows():
    turtle.setheading(-180)
    turtle.up()
    turtle.goto(-100, 290)
    turtle.down()
    turtle.pensize(2)
    turtle.pencolor("white")
    turtle.circle(60, 30)

    turtle.setheading(-180)
    turtle.up()
    turtle.goto(120, 290)
    turtle.down()
    turtle.pensize(2)
    turtle.pencolor("white")
    turtle.circle(60, 30)


# 嘴
def _xbx_mouth():
    turtle.up()
    turtle.goto(-45, 120)
    turtle.down()
    turtle.pencolor("black")
    turtle.begin_fill()
    turtle.fillcolor("black")
    turtle.setheading(-90)
    turtle.circle(50, 180)
    turtle.end_fill()


def xiongbenxiong():
    try:
        turtle.screensize(1000, 720, "#f0f0f0")
        turtle.pensize(5)
        turtle.speed(10)

        _xbx_ear()
        _xbx_body()
        _xbx_zuoshou()
        _xbx_youshou()
        _xbx_nose()
        _xbx_cheek()
        _xbx_eyes()
        _xbx_balckeyes()
        _xbx_eyebrows()
        _xbx_mouth()

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############一拳超人###################
#####################################

# 头的轮廓
def _yqcr_head():
    turtle.pensize(2)
    turtle.color('black', '#F5DEB3')
    turtle.begin_fill()
    turtle.left(40)
    turtle.circle(180, 50)
    turtle.circle(90, 180)
    turtle.circle(180, 50)
    turtle.circle(30, 60)
    turtle.circle(100, 40)
    turtle.end_fill()
    turtle.penup()
    turtle.goto(-90, 180)  # 脸的中间位置
    turtle.dot(10, 'white')
    turtle.penup()


# 眉毛
def _yqcr_eyebrows():
    turtle.goto(-16, 140)  # 右边的眉毛起始位置
    turtle.pendown()
    turtle.forward(13)
    turtle.right(75)
    turtle.forward(50)

    turtle.penup()
    turtle.goto(-60, 140)  # 左边的眉毛起始位置
    turtle.pendown()
    turtle.right(-150)
    turtle.forward(13)
    turtle.right(-75)
    turtle.forward(37)
    turtle.penup()


# 眼睛
def _yqcr_eye():
    turtle.color('black', 'white')
    turtle.goto(-60, 125)  # 左眼睛起始位置
    turtle.pendown()
    turtle.begin_fill()
    turtle.right(40)
    turtle.circle(70, 30)
    turtle.circle(5, 170)
    turtle.circle(90, 10)
    turtle.circle(5, 170)
    turtle.end_fill()
    turtle.penup()

    turtle.goto(30, 125)  # 右眼睛起始位置
    turtle.color('black', 'white')
    turtle.pendown()
    turtle.begin_fill()
    turtle.right(30)
    turtle.circle(70, 30)
    turtle.circle(5, 170)
    turtle.circle(90, 10)
    turtle.circle(5, 170)
    turtle.end_fill()
    turtle.penup()


# 眼珠
def _yqcr_blackeyes():
    turtle.goto(-95, 118)  # 左眼珠子位置
    turtle.dot(5, 'black')
    turtle.penup()

    turtle.goto(-5, 125)  # 右眼珠子位置
    turtle.dot(5, 'black')
    turtle.penup()


# 鼻子
def _yqcr_nose():
    turtle.goto(-38, 118)
    turtle.pendown()
    turtle.left(90)
    turtle.circle(120, 20)
    turtle.penup()


# 嘴巴
def _yqcr_mouth():
    turtle.goto(-58, 50)
    turtle.pendown()
    turtle.left(80)
    turtle.circle(150, 20)


def yqcr():
    try:
        _yqcr_head()
        _yqcr_eyebrows()
        _yqcr_eye()
        _yqcr_blackeyes()
        _yqcr_nose()
        _yqcr_mouth()

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
#########动感正方形(螺旋正方形)##########
#####################################
def _lxzfx_init(side, angle):
    turtle.seth(angle)
    for i in range(4):
        turtle.fd(side)
        turtle.lt(90)


def lxzfx():
    try:
        turtle.speed(15)
        for i in range(1, 5):
            cl = ["", "red", "green", "blue", "blue"]
            turtle.pencolor(cl[i])
            for j in range(12):
                turtle.pensize(i)
                # turtle.clear()
                _lxzfx_init(i * 50, j * 30)

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
################嘟嘴##################
#####################################

def pout():
    try:
        turtle.colormode(255)
        turtle.fillcolor((255, 230, 146))
        turtle.begin_fill()
        turtle.pencolor((255, 230, 146))
        turtle.circle(150, 360)
        turtle.end_fill()
        turtle.penup()
        turtle.goto(-100, 200)
        turtle.pendown()
        turtle.pencolor((149, 95, 23))
        turtle.left(350)
        turtle.pensize(5)
        turtle.forward(30)
        turtle.right(130)
        turtle.forward(35)
        turtle.penup()
        turtle.goto(90, 205)
        turtle.pendown()
        turtle.left(350)
        turtle.forward(30)
        turtle.right(240)
        turtle.forward(35)
        turtle.penup()
        turtle.goto(0, 75)
        turtle.pendown()
        a = 1
        for i in range(20):
            if 0 <= i < 5 or 10 <= i < 15:
                a = a + 0.8
                turtle.left(10)
                turtle.forward(a)
            else:
                a = a - 0.8
                turtle.left(10)
                turtle.forward(a)
        turtle.penup()
        turtle.goto(0, 75)
        turtle.pendown()
        turtle.left(190)
        a = 1
        for i in range(20):
            if 0 <= i < 5 or 10 <= i < 15:
                a = a + 0.8
                turtle.right(10)
                turtle.forward(a)
            else:
                a = a - 0.8
                turtle.right(10)
                turtle.forward(a)
        turtle.penup()
        turtle.goto(-60, 160)
        turtle.pendown()
        turtle.pencolor((255, 106, 106))
        turtle.left(100)
        turtle.forward(25)
        turtle.penup()
        turtle.goto(-75, 155)
        turtle.pendown()
        turtle.forward(24)
        turtle.penup()
        turtle.goto(-90, 155)
        turtle.pendown()
        turtle.forward(23)
        turtle.penup()
        turtle.goto(60, 160)
        turtle.pendown()
        turtle.forward(25)
        turtle.penup()
        turtle.goto(75, 155)
        turtle.pendown()
        turtle.forward(24)
        turtle.penup()
        turtle.goto(90, 155)
        turtle.pendown()
        turtle.forward(23)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
##############海绵宝宝################
#####################################
def _hmbb_face():
    turtle.tracer(3)
    turtle.penup()
    turtle.goto(-80, 160)
    turtle.pendown()
    turtle.seth(-120)
    turtle.begin_fill()
    turtle.fillcolor('yellow')
    for i in range(4):
        turtle.circle(20, 60)
        turtle.circle(-20, 60)
    turtle.seth(-30)
    for i in range(4):
        turtle.circle(20, 60)
        turtle.circle(-20, 60)
    turtle.seth(60)
    for i in range(4):
        turtle.circle(20, 60)
        turtle.circle(-20, 60)
    turtle.seth(150)
    for i in range(4):
        turtle.circle(20, 60)
        turtle.circle(-20, 60)
    turtle.end_fill()


def _hmbb_lefteye():
    turtle.penup()
    turtle.goto(0, 100)
    turtle.pd()
    turtle.begin_fill()
    turtle.fillcolor('white')
    turtle.seth(90)
    turtle.circle(-26)
    turtle.circle(26)
    turtle.end_fill()

    turtle.penup()
    turtle.goto(-36, 100)
    turtle.pendown()
    turtle.seth(90)
    turtle.circle(-10)
    turtle.penup()
    turtle.goto(-30, 100)
    turtle.pendown()
    turtle.begin_fill()
    turtle.fillcolor('black')
    turtle.seth(90)
    turtle.circle(-4)
    turtle.end_fill()


def _hmbb_righteye():
    turtle.penup()
    turtle.goto(36, 100)
    turtle.pendown()
    turtle.seth(90)
    turtle.circle(10)
    turtle.penup()
    turtle.goto(30, 100)
    turtle.pendown()
    turtle.seth(90)
    turtle.begin_fill()
    turtle.fillcolor('black')
    turtle.circle(4)
    turtle.end_fill()


def _hmbb_nose():
    turtle.penup()
    turtle.goto(10, 75)
    turtle.pd()
    turtle.circle(10, 270)


def _hmbb_mouth():
    turtle.penup()
    turtle.goto(-52, 70)
    turtle.pd()
    turtle.begin_fill()
    turtle.fillcolor('pink')
    turtle.seth(-30)
    turtle.circle(104, 60)
    turtle.seth(-90)
    turtle.circle(-52, 180)
    turtle.end_fill()


# 身体
def _hmbb_body():
    turtle.penup()
    turtle.goto(-80, 0)
    turtle.pendown()
    turtle.seth(-90)
    turtle.fd(50)
    turtle.seth(0)
    turtle.fd(160)
    turtle.seth(90)
    turtle.fd(50)
    turtle.penup()
    turtle.goto(-80, -15)
    turtle.pd()
    turtle.goto(80, -15)

    turtle.penup()
    turtle.begin_fill()
    turtle.fillcolor('red')
    turtle.goto(-5, -15)
    turtle.pendown()
    turtle.goto(-10, -20)
    turtle.goto(0, -50)
    turtle.goto(10, -20)
    turtle.goto(5, -15)
    turtle.end_fill()


# 腿脚
def _hmbb_legs():
    turtle.penup()
    turtle.goto(-50, -50)
    turtle.pendown()
    turtle.begin_fill()
    turtle.fillcolor('brown')
    turtle.goto(-50, -60)
    turtle.goto(-20, -60)
    turtle.goto(-20, -50)
    turtle.penup()
    turtle.goto(-40, -60)
    turtle.pendown()
    turtle.goto(-40, -90)
    turtle.seth(90)
    turtle.circle(8, 180)
    turtle.goto(-56, -100)
    turtle.goto(-30, -100)
    turtle.goto(-30, -60)
    turtle.end_fill()

    turtle.penup()
    turtle.goto(50, -50)
    turtle.pendown()
    turtle.begin_fill()
    turtle.fillcolor('brown')
    turtle.goto(50, -60)
    turtle.goto(20, -60)
    turtle.goto(20, -50)
    turtle.penup()
    turtle.goto(40, -60)
    turtle.pendown()
    turtle.goto(40, -90)
    turtle.seth(90)
    turtle.circle(-8, 180)
    turtle.goto(56, -100)
    turtle.goto(30, -100)
    turtle.goto(30, -60)
    turtle.end_fill()


# 手
def _hmbb_hands():
    turtle.penup()
    turtle.goto(-82.68, 70)
    turtle.pendown()
    turtle.goto(-97.68, 60)
    turtle.goto(-97.68, 20)
    turtle.goto(-82.68, 30)

    turtle.penup()
    turtle.goto(77.32, 70)
    turtle.pendown()
    turtle.goto(97.32, 60)
    turtle.goto(97.32, 20)
    turtle.goto(77.32, 30)

    turtle.penup()
    turtle.goto(-97.68, 45)
    turtle.pendown()
    turtle.goto(-137.68, 25)
    turtle.seth(150)
    turtle.circle(10, 300)
    turtle.goto(-97.68, 35)

    turtle.penup()
    turtle.goto(97.32, 45)
    turtle.pendown()
    turtle.goto(137.32, 25)
    turtle.seth(30)
    turtle.circle(-10, 300)
    turtle.goto(97.32, 35)


def hmbb():
    try:
        _hmbb_face()
        _hmbb_lefteye()
        _hmbb_righteye()
        _hmbb_nose()
        _hmbb_mouth()
        _hmbb_body()
        _hmbb_legs()
        _hmbb_hands()

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############滑稽###################
#####################################
def funny():
    try:
        turtle.penup()
        turtle.fd(75)
        turtle.pendown()
        turtle.pensize(150)
        turtle.pencolor("gold")
        turtle.seth(90)
        turtle.circle(75)
        turtle.seth(0)
        turtle.penup()
        turtle.fd(21)
        turtle.seth(-90)
        turtle.fd(72)
        turtle.seth(53)
        turtle.pendown()
        turtle.pencolor("black")
        turtle.pensize(5)
        turtle.circle(120, -106)
        turtle.seth(90)
        turtle.penup()
        turtle.fd(82)
        turtle.seth(180)
        turtle.fd(44)
        turtle.seth(90)
        turtle.seth(0)
        turtle.pendown()
        turtle.pensize(20)
        turtle.pencolor("pink")
        turtle.fd(60)
        turtle.penup()
        turtle.fd(160)
        turtle.pendown()
        turtle.fd(60)
        turtle.seth(90)
        turtle.penup()
        turtle.fd(40)
        turtle.seth(180)
        turtle.fd(10)
        turtle.seth(163)
        turtle.pendown()
        turtle.pencolor("whitesmoke")
        turtle.pensize(30)
        turtle.circle(154.54, 30)
        turtle.seth(180)
        turtle.penup()
        turtle.fd(100)
        turtle.seth(164)
        turtle.pendown()
        turtle.circle(154.54, 30)
        turtle.penup()
        turtle.seth(0)
        turtle.fd(25)
        turtle.seth(90)
        turtle.fd(2)
        turtle.pendown()
        turtle.pencolor("black")
        turtle.pensize(16)
        turtle.circle(8)
        turtle.penup()
        turtle.seth(0)
        turtle.fd(180)
        turtle.seth(90)
        turtle.pendown()
        turtle.circle(8)
        turtle.penup()
        turtle.seth(180)
        turtle.fd(10)
        turtle.seth(90)
        turtle.fd(33)
        turtle.seth(-120)
        turtle.pendown()
        turtle.pensize(5)
        turtle.circle(40, -120)
        turtle.penup()
        turtle.seth(180)
        turtle.fd(201.56)
        turtle.seth(120)
        turtle.pendown()
        turtle.circle(40, 120)

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############白熊###################
#####################################
def whitebear():
    try:
        turtle.speed(400)

        turtle.pu()
        turtle.setpos(-100, 200)
        turtle.pd()
        turtle.pensize(4)
        turtle.circle(15, 360)
        turtle.pu()
        turtle.setpos(40, 200)
        turtle.pd()
        turtle.circle(15, 360)
        turtle.pu()
        turtle.setpos(-105, 195)
        turtle.pd()
        turtle.seth(45)
        turtle.circle(-105, 90)

        turtle.seth(295)
        turtle.fd(9)
        turtle.seth(285)
        turtle.fd(9)
        turtle.seth(280)
        turtle.fd(6)
        # 红酒窝
        turtle.pensize(1)
        turtle.color('black', 'red')
        turtle.begin_fill()
        turtle.seth(330)
        turtle.circle(-24, 360)
        turtle.end_fill()
        # 右半边
        turtle.pensize(4)
        turtle.pu()
        turtle.setpos(55, 132)
        turtle.pd()
        turtle.seth(281)
        turtle.fd(20)
        turtle.seth(298)
        turtle.fd(60)
        turtle.seth(288)
        turtle.fd(80)
        turtle.seth(280)
        turtle.fd(30)
        turtle.seth(270)
        turtle.fd(5)
        turtle.seth(260)
        turtle.fd(10)
        turtle.seth(250)
        turtle.fd(10)
        turtle.seth(210)
        turtle.fd(13)
        turtle.seth(180)
        turtle.fd(3)
        turtle.seth(150)
        turtle.fd(13)
        turtle.seth(270)
        turtle.fd(50)
        turtle.seth(265)
        turtle.fd(55)
        turtle.seth(275)
        turtle.fd(20)
        turtle.seth(285)
        turtle.fd(15)
        turtle.seth(260)
        turtle.fd(5)
        turtle.seth(230)
        turtle.fd(5)
        turtle.seth(180)
        turtle.fd(45)
        turtle.seth(150)
        turtle.fd(7)
        turtle.seth(100)
        turtle.fd(20)
        turtle.seth(85)
        turtle.fd(13)
        turtle.seth(110)
        turtle.fd(30)
        turtle.seth(180)
        turtle.fd(80)
        # 左半边
        turtle.seth(250)
        turtle.fd(30)
        turtle.seth(275)
        turtle.fd(13)
        turtle.seth(260)
        turtle.fd(20)
        turtle.seth(210)
        turtle.fd(7)
        turtle.seth(180)
        turtle.fd(45)
        turtle.seth(130)
        turtle.fd(5)
        turtle.seth(100)
        turtle.fd(5)
        turtle.seth(75)
        turtle.fd(15)
        turtle.seth(85)
        turtle.fd(20)
        turtle.seth(95)
        turtle.fd(55)
        turtle.seth(90)
        turtle.fd(45)
        turtle.seth(180)
        turtle.fd(3)
        turtle.seth(210)
        turtle.fd(13)
        turtle.seth(180)
        turtle.fd(2)
        turtle.seth(160)
        turtle.fd(16)
        turtle.seth(100)
        turtle.fd(10)
        turtle.seth(90)
        turtle.fd(5)
        turtle.seth(95)
        turtle.fd(15)
        turtle.seth(90)
        turtle.fd(5)
        turtle.seth(85)
        turtle.fd(14)
        turtle.seth(78)
        turtle.fd(82)
        turtle.seth(64)
        turtle.fd(48)
        turtle.seth(83)
        turtle.fd(35)
        # 红酒窝
        turtle.color('black', 'red')
        turtle.begin_fill()
        turtle.pensize(1)
        turtle.seth(320)
        turtle.circle(24, 360)
        turtle.end_fill()
        # 右半边补
        turtle.pensize(4)
        turtle.pu()
        turtle.setpos(-114, 170)
        turtle.pd()
        turtle.seth(75)
        turtle.fd(15)
        turtle.seth(65)
        turtle.fd(15)
        # 眼睛
        turtle.pensize(2)
        turtle.pu()
        turtle.setpos(-61, 155)
        turtle.pd()
        turtle.seth(0)
        turtle.circle(18, 360)
        turtle.pensize(2)
        turtle.pu()
        turtle.setpos(-5, 155)
        turtle.pd()
        turtle.seth(0)
        turtle.circle(18, 360)
        # 眼球
        turtle.pensize(3)
        turtle.pu()
        turtle.setpos(-5, 172)
        turtle.pd()
        turtle.seth(0)
        turtle.circle(2, 360)
        turtle.pensize(3)
        turtle.pu()
        turtle.setpos(-61, 172)
        turtle.pd()
        turtle.seth(0)
        turtle.circle(2, 360)
        # 眉毛
        turtle.pu()
        turtle.setpos(-80, 204)
        turtle.pd()
        turtle.pensize(5)
        turtle.seth(50)
        turtle.circle(-11, 90)
        turtle.pu()
        turtle.setpos(7, 204)
        turtle.pd()
        turtle.pensize(5)
        turtle.seth(50)
        turtle.circle(-11, 90)
        # 嘴巴
        turtle.pensize(1)
        turtle.pu()
        turtle.setpos(-30, 130)
        turtle.pd()
        turtle.color('black', 'black')
        turtle.begin_fill()
        turtle.seth(0)
        turtle.circle(-13, 360)
        turtle.end_fill()
        turtle.pensize(3)
        turtle.pu()
        turtle.setpos(-30, 104)
        turtle.pd()
        turtle.seth(270)
        turtle.fd(5)
        turtle.pu()
        turtle.setpos(-30, 99)
        turtle.pd()
        turtle.seth(220)
        turtle.pensize(3)
        turtle.fd(15)
        turtle.pu()
        turtle.setpos(-30, 99)
        turtle.pd()
        turtle.seth(320)
        turtle.pensize(3)
        turtle.fd(15)

        turtle.hideturtle()
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############瓢虫###################
#####################################
def ladybug():
    try:
        turtle.penup()
        turtle.pensize(10)
        turtle.fillcolor('red')
        turtle.pencolor('black')
        turtle.speed('fast')
        turtle.seth(90)
        turtle.fd(100)
        turtle.seth(180)
        turtle.pd()
        turtle.begin_fill()
        turtle.circle(100, 90)
        turtle.seth(-90)
        turtle.fd(10)
        turtle.circle(100, 180)
        turtle.fd(10)
        turtle.circle(100, 90)
        turtle.end_fill()

        turtle.seth(-90)
        turtle.pensize(10)
        turtle.fd(210)
        turtle.pu()
        turtle.seth(0)
        turtle.fd(40)
        turtle.seth(90)
        turtle.fd(40)

        turtle.pd()
        turtle.fillcolor('black')
        turtle.begin_fill()
        turtle.circle(10, 360)
        turtle.end_fill()

        turtle.pu()
        turtle.seth(10)
        turtle.fd(50)
        turtle.seth(90)
        turtle.fd(40)
        turtle.pd()
        turtle.begin_fill()
        turtle.circle(10, 360)
        turtle.end_fill()

        turtle.pu()
        turtle.seth(120)
        turtle.fd(60)
        turtle.pd()
        turtle.begin_fill()
        turtle.circle(10, 360)
        turtle.end_fill()

        turtle.pu()
        turtle.seth(178)
        turtle.fd(108)
        turtle.pd()
        turtle.begin_fill()
        turtle.circle(10, 360)
        turtle.end_fill()
        turtle.pu()
        turtle.seth(-120)
        turtle.fd(60)
        turtle.pd()
        turtle.begin_fill()
        turtle.circle(10, 360)
        turtle.end_fill()

        turtle.pu()
        turtle.seth(-55)
        turtle.fd(70)
        turtle.pd()
        turtle.begin_fill()
        turtle.circle(10, 360)
        turtle.end_fill()

        turtle.pu()
        turtle.seth(80)
        turtle.fd(180)
        turtle.seth(90)
        turtle.pd()
        turtle.circle(50, 80)
        turtle.circle(5, 360)
        turtle.pu()
        turtle.seth(0)
        turtle.circle(-50, 90)
        turtle.seth(0)
        turtle.fd(3)
        turtle.seth(90)
        turtle.pd()
        turtle.circle(-50, 80)
        turtle.circle(-5, 360)
        turtle.pu()

        turtle.seth(-70)
        turtle.fd(100)
        turtle.seth(40)
        turtle.pd()
        turtle.fd(30)
        turtle.seth(-30)
        turtle.fd(35)
        turtle.pu()

        turtle.seth(240)
        turtle.fd(55)
        turtle.pd()
        turtle.seth(30)
        turtle.fd(30)
        turtle.seth(-40)
        turtle.fd(40)
        turtle.pu()

        turtle.seth(213)
        turtle.fd(75)
        turtle.pd()
        turtle.seth(-5)
        turtle.fd(30)
        turtle.seth(-70)
        turtle.fd(40)

        turtle.pu()
        turtle.seth(-180)
        turtle.fd(290)
        turtle.pd()
        turtle.seth(70)
        turtle.fd(40)
        turtle.seth(5)
        turtle.fd(33)

        turtle.pu()
        turtle.seth(90)
        turtle.fd(55)
        turtle.seth(150)
        turtle.pd()
        turtle.fd(30)
        turtle.seth(210)
        turtle.fd(40)

        turtle.pu()
        turtle.seth(79)
        turtle.fd(45)
        turtle.seth(33)
        turtle.pd()
        turtle.fd(40)
        turtle.seth(-30)
        turtle.fd(35)

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############风车###################
#####################################
def _fengche_windmill(col1, col2, arg):
    turtle.color(col1, col1)
    turtle.seth(arg)
    turtle.circle(30, 90)
    turtle.seth(arg)
    turtle.begin_fill()
    turtle.fd(120)
    turtle.seth(arg - 90)
    turtle.fd(150)
    turtle.seth((arg + 135) % 360)
    turtle.fd(150 * (1.414) - 30)
    turtle.end_fill()
    # 正右三角
    turtle.color(col2, col2)
    turtle.begin_fill()
    turtle.seth((arg + 45) % 360)
    turtle.circle(30, 90)
    turtle.seth((arg + 45) % 360)
    turtle.fd(75 * 1.414 - 30)
    turtle.seth((arg + 315) % 360)
    turtle.fd(150 / 1.414)
    turtle.seth((arg + 180) % 360)
    turtle.fd(120)
    turtle.end_fill()


def _fengche_clear():
    turtle.seth(0)
    turtle.pencolor("white")
    turtle.pensize(5)
    turtle.circle(30)
    turtle.up()
    turtle.goto(0, 0)
    turtle.down()
    turtle.seth(0)


def fengche():
    try:
        turtle.pensize(3)
        turtle.colormode(255)
        turtle.tracer(10)
        _fengche_windmill('green', 'darkgreen', 0)
        _fengche_windmill((26, 188, 156), (22, 160, 133), 90)
        _fengche_windmill((241, 196, 15), (243, 156, 18), 180)
        _fengche_windmill((231, 76, 60), (192, 57, 43), 270)
        _fengche_clear()
        turtle.update()

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
##############表白/love###############
#####################################
def love():
    try:
        turtle.pensize(10)
        turtle.pencolor("black")
        turtle.penup()
        turtle.goto(-50, 180)
        turtle.pendown()
        turtle.goto(50, 180)
        turtle.penup()
        turtle.goto(-75, 90)
        turtle.pendown()
        turtle.goto(75, 90)
        turtle.penup()
        turtle.goto(-100, 0)
        turtle.pendown()
        turtle.goto(100, 0)
        turtle.penup()
        turtle.goto(-125, -90)
        turtle.pendown()
        turtle.goto(125, -90)
        turtle.penup()
        turtle.goto(-125, -180)
        turtle.pendown()
        turtle.goto(125, -180)
        turtle.penup()
        turtle.goto(-50, 180)
        turtle.pendown()
        turtle.goto(-50, 90)
        turtle.penup()
        turtle.goto(0, 180)
        turtle.pendown()
        turtle.goto(0, 90)
        turtle.penup()
        turtle.goto(50, 180)
        turtle.pendown()
        turtle.goto(50, 90)
        turtle.penup()
        turtle.goto(-75, 90)
        turtle.pendown()
        turtle.goto(-75, 0)
        turtle.penup()
        turtle.goto(-25, 90)
        turtle.pendown()
        turtle.goto(-25, 0)
        turtle.penup()
        turtle.goto(25, 90)
        turtle.pendown()
        turtle.goto(25, 0)
        turtle.penup()
        turtle.goto(75, 90)
        turtle.pendown()
        turtle.goto(75, 0)
        turtle.penup()
        turtle.goto(-100, 0)
        turtle.pendown()
        turtle.goto(-100, -90)
        turtle.penup()
        turtle.goto(-50, 0)
        turtle.pendown()
        turtle.goto(-50, -90)
        turtle.penup()
        turtle.goto(0, 0)
        turtle.pendown()
        turtle.goto(0, -90)
        turtle.penup()
        turtle.goto(50, 0)
        turtle.pendown()
        turtle.goto(50, -90)
        turtle.penup()
        turtle.goto(100, 0)
        turtle.pendown()
        turtle.goto(100, -90)
        turtle.penup()
        turtle.goto(-125, -90)
        turtle.pendown()
        turtle.goto(-125, -180)
        turtle.penup()
        turtle.goto(-75, -90)
        turtle.pendown()
        turtle.goto(-75, -180)
        turtle.penup()
        turtle.goto(-25, -90)
        turtle.pendown()
        turtle.goto(-25, -180)
        turtle.penup()
        turtle.goto(25, -90)
        turtle.pendown()
        turtle.goto(25, -180)
        turtle.penup()
        turtle.goto(75, -90)
        turtle.pendown()
        turtle.goto(75, -180)
        turtle.penup()
        turtle.goto(125, -90)
        turtle.pendown()
        turtle.goto(125, -180)
        turtle.penup()
        turtle.goto(-50, 150)
        turtle.pendown()
        turtle.goto(-25, 150)
        turtle.penup()
        turtle.goto(-25, 120)
        turtle.pendown()
        turtle.goto(0, 120)
        turtle.penup()
        turtle.goto(25, 150)
        turtle.pendown()
        turtle.goto(25, 120)
        turtle.penup()
        turtle.goto(-75, 30)
        turtle.pendown()
        turtle.goto(-50, 30)
        turtle.penup()
        turtle.goto(-50, 60)
        turtle.pendown()
        turtle.goto(0, 60)
        turtle.penup()
        turtle.goto(0, 30)
        turtle.pendown()
        turtle.goto(25, 30)
        turtle.penup()
        turtle.goto(50, 60)
        turtle.pendown()
        turtle.goto(50, 30)
        turtle.penup()
        turtle.goto(-75, -20)
        turtle.pendown()
        turtle.goto(-75, -30)
        turtle.penup()
        turtle.goto(-100, -50)
        turtle.pendown()
        turtle.goto(-75, -50)
        turtle.goto(-75, -70)
        turtle.penup()
        turtle.goto(-25, 0)
        turtle.pendown()
        turtle.goto(-25, -55)
        turtle.penup()
        turtle.goto(-50, -80)
        turtle.pendown()
        turtle.goto(-25, -80)
        turtle.penup()
        turtle.goto(-4, 0)
        turtle.pendown()
        turtle.goto(-4, -55)
        turtle.penup()
        turtle.goto(-4, -80)
        turtle.pendown()
        turtle.goto(-4, -90)
        turtle.penup()
        turtle.goto(0, -30)
        turtle.pendown()
        turtle.goto(25, -30)
        turtle.penup()
        turtle.goto(25, -60)
        turtle.pendown()
        turtle.goto(50, -60)
        turtle.penup()
        turtle.goto(75, -30)
        turtle.pendown()
        turtle.goto(75, -60)
        turtle.penup()
        turtle.goto(-125, -150)
        turtle.pendown()
        turtle.goto(-100, -150)
        turtle.penup()
        turtle.goto(-100, -120)
        turtle.pendown()
        turtle.goto(-75, -120)
        turtle.penup()
        turtle.goto(-50, -110)
        turtle.pendown()
        turtle.goto(-50, -120)
        turtle.penup()
        turtle.goto(-75, -145)
        turtle.pendown()
        turtle.goto(-50, -145)
        turtle.goto(-50, -165)
        turtle.penup()
        turtle.goto(0, -90)
        turtle.pendown()
        turtle.goto(0, -145)
        turtle.penup()
        turtle.goto(-25, -170)
        turtle.pendown()
        turtle.goto(0, -170)
        turtle.penup()
        turtle.goto(21, -90)
        turtle.pendown()
        turtle.goto(21, -145)
        turtle.penup()
        turtle.goto(21, -170)
        turtle.pendown()
        turtle.goto(21, -180)
        turtle.penup()
        turtle.goto(25, -120)
        turtle.pendown()
        turtle.goto(50, -120)
        turtle.penup()
        turtle.goto(50, -150)
        turtle.pendown()
        turtle.goto(75, -150)
        turtle.penup()
        turtle.goto(100, -120)
        turtle.pendown()
        turtle.goto(100, -150)
        turtle.penup()
        turtle.goto(200, -250)
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############皮卡丘##################
#####################################


# 辅助函数
def _pikachu_E(
        cx, cy,
        a, b,
        matrix=(1, 0, 0, 1, 0, 0)):
    cp = complex(cx, cy)  # 中心
    sp = cp + a  # 绘制起点
    turtle.penup()
    _M(_pikachu_transform(sp, matrix))
    turtle.color("#FB8D8C")
    turtle.pensize(0.1)
    turtle.fillcolor("#FB8D8C")
    turtle.begin_fill()
    turtle.pendown()
    for i in range(0, 360 + 1):
        x = a * math.sin(i * 2 * math.pi / 360 + math.pi / 2) + cx
        y = b * math.cos(i * 2 * math.pi / 360 + math.pi / 2) + cy
        p = complex(x, y)
        _M(_pikachu_transform(p, matrix))
    turtle.end_fill()
    _pu()


def _pikachu_transform(p, matrix=(1, 0, 0, 1, 0, 0)):
    a, b, c = matrix[0], matrix[1], matrix[2],
    d, e, f = matrix[3], matrix[4], matrix[5],
    return complex(
        a * p.real + c * p.imag + e,
        b * p.real + d * p.imag + f
    )


# pikachu_身体
def _pikachu_body():
    _pd(420.5 + 130.5j, rgb="#816124", bold=6)  # 身体 pd
    _f(420.5 + 130.5j, "#FFFC9D")
    _C(420.5 + 130.5j, 406.87 + 122.22j, 376.07 + 106.14j, 334.5 + 106.5j)
    _C(334.5 + 106.5j, 272.08 + 107.05j, 231.12 + 144.27j, 221.5 + 153.5j)
    _L(221.5 + 153.5j, 235.5 + 141.5j)
    _C(235.5 + 141.5j, 212.68 + 140.71j, 180.37 + 141.73j, 148.5 + 147.5j)
    _C(148.5 + 147.5j, 107.27 + 154.96j, 86.82 + 160.88j, 62.5 + 172.5j)
    _C(62.5 + 172.5j, 75.29 + 179.74j, 94.99 + 188.89j, 120.5 + 193.5j)
    _C(120.5 + 193.5j, 152.85 + 199.34j, 188.71 + 192.2j, 204.5 + 188.5j)
    _C(204.5 + 188.5j, 200.5 + 202.5j, 194.15 + 226.33j, 192.5 + 244.5j)
    _C(192.5 + 244.5j, 190.5 + 266.5j, 192.5 + 342.5j, 189.5 + 355.5j)
    _C(189.5 + 355.5j, 184.56 + 376.91j, 152 + 435j, 152 + 435j)
    _L(152 + 435j, 112 + 391j)
    _L(112 + 391j, 50 + 432j)
    _L(50 + 432j, 0.5 + 364.5j)
    _L(0.5 + 364.5j, 0.5 + 431.5j)
    _L(0.5 + 431.5j, 49.5 + 461.5j)
    _L(49.5 + 461.5j, 101.5 + 429.5j)
    _L(101.5 + 429.5j, 147.5 + 450.5j)
    _C(147.5 + 450.5j, 147.5 + 461.83j, 145.77 + 476.92j, 147.5 + 485.5j)
    _C(147.5 + 485.5j, 148.71 + 491.51j, 154.1 + 501.65j, 158.5 + 508.5j)
    _C(158.5 + 508.5j, 164.2 + 517.37j, 172.68 + 528.69j, 179.5 + 531.5j)
    _C(179.5 + 531.5j, 228.85 + 551.83j, 393 + 531.5j, 393 + 531.5j)
    _C(393 + 531.5j, 393 + 531.5j, 408.21 + 525.6j, 420.5 + 524.5j)
    _C(420.5 + 524.5j, 440.25 + 522.73j, 460.55 + 528.07j, 467.5 + 531.5j)
    _C(467.5 + 531.5j, 476.45 + 520.82j, 487.49 + 502.89j, 496.5 + 485.5j)
    _C(496.5 + 485.5j, 510.46 + 458.55j, 515.61 + 429.58j, 518.5 + 411.5j)
    _C(518.5 + 411.5j, 510.7 + 415.96j, 498.99 + 424.21j, 488.5 + 435.5j)
    _C(488.5 + 435.5j, 477.86 + 446.95j, 471.37 + 458.32j, 467.5 + 466.5j)
    _L(467.5 + 466.5j, 470.5 + 460.5j)
    _L(470.5 + 460.5j, 461.5 + 319.5j)
    _L(461.5 + 319.5j, 453.5 + 330.5j)
    _C(453.5 + 330.5j, 481.5 + 292.5j, 483.5 + 275.68j, 483.5 + 259.5j)
    _C(483.5 + 259.5j, 483.5 + 237.5j, 465.5 + 214.5j, 463.5 + 194.5j)
    _C(463.5 + 194.5j, 463.23 + 191.75j, 464.65 + 184.98j, 462.5 + 176.5j)
    _C(462.5 + 176.5j, 460.44 + 168.38j, 456.49 + 162.32j, 453.5 + 158.5j)
    _L(453.5 + 158.5j, 460.5 + 170.5j)
    _C(460.5 + 170.5j, 478.16 + 163.45j, 497.24 + 154.06j, 518.5 + 141.5j)
    _C(518.5 + 141.5j, 542.18 + 127.5j, 560.78 + 114.84j, 576.5 + 101.5j)
    _C(576.5 + 101.5j, 550.5 + 98.5j, 503.5 + 103.5j, 483.5 + 105.5j)
    _C(483.5 + 105.5j, 458.54 + 108j, 430.8 + 116.23j, 409.5 + 124.5j)
    _L(409.5 + 124.5j, 420.5 + 130.5j)
    turtle.end_fill()
    _pu()  # 身体 pu


# 左脚
def _pikachu_leftfoot():
    _pd(268.5 + 467.5j, rgb="#816124", bold=6)  # 左脚 pd
    _C(268.5 + 467.5j, 299.04 + 420.77j, 308.38 + 413.95j, 311.5 + 415.5j)
    _C(311.5 + 415.5j, 317.66 + 418.57j, 304.92 + 457.13j, 297.5 + 476.5j)
    _C(297.5 + 476.5j, 287.43 + 502.78j, 275.93 + 523.1j, 267.5 + 536.5j)


# 左手
def _pikachu_lefthand():
    _Mv(322.5 + 490.5j)
    _f(322.5 + 490.5j, "#FFFC9D")
    _C(322.5 + 490.5j, 344.85 + 527.85j, 359.51 + 545.18j, 366.5 + 542.5j)
    _C(366.5 + 542.5j, 372.1 + 540.35j, 372.77 + 525.35j, 368.5 + 497.5j)
    turtle.end_fill()


# 右手
def _pikachu_righthand():
    _Mv(399.5 + 501.5j)
    _f(399.5 + 501.5j, "#FFFC9D")
    _C(399.5 + 501.5j, 403.32 + 521.92j, 407.65 + 532.25j, 412.5 + 532.5j)
    _C(412.5 + 532.5j, 419.44 + 532.85j, 427.44 + 512.52j, 436.5 + 471.5j)
    turtle.end_fill()
    _pu()  # 左脚 pd-pu


# 右眼
def _pikachu_righteye():
    _pd(252.7 + 228.84j, rgb="#29ABE2", bold=6)  # 右眼-pd
    _f(252.7 + 228.84j, "#29ABE2")
    _C(252.7 + 228.84j, 261.37 + 225.51j, 270.03 + 222.17j, 278.7 + 218.84j)
    _C(278.7 + 218.84j, 284.05 + 216.78j, 281.73 + 208.08j, 276.31 + 210.16j)
    _C(276.31 + 210.16j, 267.64 + 213.49j, 258.98 + 216.83j, 250.31 + 220.16j)
    _C(250.31 + 220.16j, 244.95 + 222.22j, 247.28 + 230.92j, 252.7 + 228.84j)
    _L(252.7 + 228.84j, 252.7 + 228.84j)
    turtle.end_fill()


# 左眼
def _pikachu_lefteye():
    _Mv(415.5 + 207j)
    _f(415.5 + 207j, "#29ABE2")
    _C(415.5 + 207j, 423.17 + 207j, 430.83 + 207j, 438.5 + 207j)
    _C(438.5 + 207j, 444.29 + 207j, 444.3 + 198j, 438.5 + 198j)
    _C(438.5 + 198j, 430.83 + 198j, 423.17 + 198j, 415.5 + 198j)
    _C(415.5 + 198j, 409.71 + 198j, 409.7 + 207j, 415.5 + 207j)
    _L(415.5 + 207j, 415.5 + 207j)
    turtle.end_fill()


# 嘴
def _pikachu_mouth():
    _Mv(374.61 + 224.7j)
    _C(374.61 + 224.7j, 373.87 + 226.96j, 373.41 + 229.28j, 372.72 + 231.54j)
    _C(372.72 + 231.54j, 371.86 + 234.36j, 370.89 + 234.59j, 367.97 + 233.71j)
    _C(367.97 + 233.71j, 364.24 + 232.59j, 360.67 + 231.63j, 356.93 + 233.24j)
    _C(356.93 + 233.24j, 354 + 234.5j, 352.15 + 236.99j, 349.79 + 239.01j)
    _C(349.79 + 239.01j, 344.75 + 243.32j, 340.79 + 240.01j, 336.02 + 236.9j)
    _C(336.02 + 236.9j, 332.78 + 234.78j, 329.77 + 239.98j, 332.99 + 242.08j)
    _C(332.99 + 242.08j, 337.32 + 244.9j, 342.21 + 248.67j, 347.65 + 247.05j)
    _C(347.65 + 247.05j, 352.57 + 245.59j, 354.65 + 240.81j, 359 + 238.87j)
    _C(359 + 238.87j, 364.11 + 236.6j, 369.61 + 242.75j, 374.71 + 239.51j)
    _C(374.71 + 239.51j, 378.75 + 236.95j, 379.07 + 230.35j, 380.39 + 226.28j)
    _C(380.39 + 226.28j, 381.59 + 222.62j, 375.8 + 221.04j, 374.61 + 224.7j)
    _L(374.61 + 224.7j, 374.61 + 224.7j)
    _pu()  # 右眼 pd-pu


# 腮红 左
def _pikachu_leftcheek():
    _pikachu_E(255.5, 282.5, 22.5, 23.5)


# 腮红 右
def _pikachu_rightcheek():
    _pikachu_E(425.5, 260, 16.5, 21)


# 左耳_花纹
def _pikachu_leftear():
    _f(63.5 + 172.5j, "#816124")
    _C(63.5 + 172.5j, 76.29 + 179.74j, 95.99 + 188.89j, 121.5 + 193.5j)
    _C(121.5 + 193.5j, 153.85 + 199.34j, 147.5 + 195.5j, 147.5 + 195.5j)
    _C(147.5 + 195.5j, 141.5 + 192.5j, 132.74 + 182.44j, 130.5 + 173.5j)
    _C(130.5 + 173.5j, 128.5 + 165.5j, 134.5 + 153.5j, 138.5 + 149.5j)
    _C(138.5 + 149.5j, 138.5 + 149.5j, 87.82 + 160.88j, 63.5 + 172.5j)
    turtle.end_fill()


# 右耳花纹
def _pikachu_rightear():
    _f(577.5 + 101.5j, "#816124")
    _C(577.5 + 101.5j, 551.5 + 98.5j, 495.5 + 104.5j, 495.5 + 104.5j)
    _C(495.5 + 104.5j, 503.5 + 104.5j, 518.26 + 110.08j, 522.5 + 117.5j)
    _C(522.5 + 117.5j, 526.5 + 124.5j, 523.5 + 137.5j, 514.5 + 144.5j)
    _C(514.5 + 144.5j, 538.18 + 130.5j, 561.78 + 114.84j, 577.5 + 101.5j)
    turtle.end_fill()


# 背部花纹
def _pikachu_back():
    _f(180.5 + 381.5j, "#816124")
    _C(180.5 + 381.5j, 179.19 + 388.04j, 174.5 + 405.5j, 178.5 + 418.5j)
    _C(178.5 + 418.5j, 183.42 + 434.5j, 194.62 + 445.6j, 191.5 + 449.5j)
    _C(191.5 + 449.5j, 187.5 + 454.5j, 175.5 + 439.5j, 159.5 + 422.5j)
    _C(180.5 + 381.5j, 197.5 + 404.5j, 206.5 + 412.5j, 209.5 + 409.5j)
    _C(209.5 + 409.5j, 213.04 + 405.96j, 194.67 + 394.75j, 193.5 + 379.5j)
    _C(193.5 + 379.5j, 192.5 + 366.5j, 192.37 + 344.38j, 192.5 + 336.5j)
    turtle.end_fill()


# 尾巴花纹
def _pikachu_tail():
    _f(120.62 + 437.37j, "#816124")
    _C(120.62 + 437.37j, 120.62 + 437.37j, 118.5 + 397.44j, 118.5 + 396.24j)
    _L(118.5 + 396.24j, 155 + 435.31j)
    _L(155 + 435.31j, 150.24 + 451.25j)
    _L(150.24 + 451.25j, 120.62 + 437.37j)
    turtle.end_fill()


def pikachu():
    try:
        turtle.screensize(600, 600, "white")

        turtle.pensize(6)
        turtle.speed(0)
        turtle.penup()

        _pikachu_body()
        _pikachu_leftfoot()
        _pikachu_lefthand()
        _pikachu_righthand()
        _pikachu_righteye()
        _pikachu_lefteye()
        _pikachu_mouth()
        _pikachu_leftcheek()
        _pikachu_rightcheek()
        _pikachu_leftear()
        _pikachu_rightear()
        _pikachu_back()
        _pikachu_tail()
        turtle.hideturtle()  # 隐藏乌龟图标
        turtle.update()

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############轻松熊#################
#####################################
# 身体
def _qingsongbear_body():
    turtle.penup()
    turtle.goto(-70, -85)
    turtle.seth(135)
    turtle.pendown()
    turtle.begin_fill()
    turtle.circle(18, 180)
    turtle.circle(200, 17)
    turtle.seth(-90)
    turtle.circle(400, 13)
    turtle.circle(18, 180)
    turtle.seth(-104)
    turtle.circle(18, 180)
    turtle.circle(400, 13)
    turtle.seth(28)
    turtle.circle(200, 17)
    turtle.circle(18, 180)
    turtle.end_fill()


# body white
def _qingsongbear_body_white():
    turtle.penup()
    turtle.goto(0, -185)
    turtle.fillcolor("white")
    turtle.pencolor("white")
    turtle.seth(0)
    turtle.pendown()
    turtle.begin_fill()
    turtle.circle(20, 22.5)
    turtle.circle(30, 135)
    turtle.circle(20, 45)
    turtle.circle(30, 135)
    turtle.circle(20, 22.5)
    turtle.end_fill()


# face
def _qingsongbear_face():
    turtle.fillcolor('#B8860B')
    turtle.pencolor('#5E2612')
    turtle.seth(-22.5)
    turtle.penup()
    turtle.goto(0, 0)
    turtle.fd(120)
    turtle.pendown()
    turtle.seth(60)
    turtle.begin_fill()
    turtle.circle(75, 45)
    turtle.circle(125, 135)
    turtle.circle(75, 45)
    turtle.circle(125, 135)
    turtle.end_fill()
    turtle.pensize(17)
    turtle.penup()
    turtle.goto(45, 0)
    turtle.pendown()
    turtle.circle(5, 360)
    turtle.penup()
    turtle.goto(-45, 0)
    turtle.pendown()
    turtle.circle(5, 360)
    # face white
    turtle.penup()
    turtle.seth(-22.5)
    turtle.fd(75)
    turtle.seth(60)
    turtle.pendown()
    turtle.fillcolor("white")
    turtle.begin_fill()
    turtle.pencolor("white")
    turtle.circle(15, 45)
    turtle.circle(30, 135)
    turtle.circle(15, 45)
    turtle.circle(30, 135)
    turtle.end_fill()
    # face2
    turtle.fillcolor('#B8860B')
    turtle.pencolor('#5E2612')
    turtle.penup()
    turtle.goto(0, -15)
    turtle.pendown()
    turtle.pensize(10)
    turtle.seth(0)
    turtle.circle(5, 360)
    turtle.seth(-45)
    turtle.fd(20)
    turtle.penup()
    turtle.goto(0, -15)
    turtle.seth(-135)
    turtle.pendown()
    turtle.fd(20)
    turtle.penup()
    turtle.goto(65, 100)
    turtle.circle(35, 170)
    turtle.pendown()
    turtle.begin_fill()
    turtle.circle(35, 205)
    turtle.end_fill()
    turtle.penup()
    turtle.goto(-65, 100)
    turtle.seth(-45)
    turtle.circle(-35, 175)
    turtle.pendown()
    turtle.begin_fill()
    turtle.circle(-35, 195)
    turtle.end_fill()


# heart
def _qingsongbear_heart():
    turtle.penup()
    turtle.goto(150, 150)
    turtle.seth(45)
    turtle.pencolor("red")
    turtle.fillcolor("red")
    turtle.pendown()
    turtle.begin_fill()
    turtle.fd(19)
    turtle.circle(25, 45)
    turtle.circle(11.25, 180)
    turtle.seth(90)
    turtle.circle(11.25, 180)
    turtle.circle(25, 45)
    turtle.fd(19)
    turtle.end_fill()


def bear():
    try:
        turtle.tracer(10)
        turtle.ht()
        turtle.fillcolor('#B8860B')
        turtle.pensize(10)
        turtle.pencolor('#5E2612')
        _qingsongbear_body()
        _qingsongbear_body_white()
        _qingsongbear_face()
        _qingsongbear_heart()

        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############Car###################
#####################################
# 车头
def car_head(c='#FFA500'):
    turtle.screensize(800, 600)
    # fill_rect(200, 100, 100, 100, c)
    _turtle_fill_rect(-200, 200, 100, 100, c)
    __flush()


# 车身
def car_body(c='#FF6147'):
    turtle.screensize(800, 600)
    # fill_rect(200, 200, 350, 100, c)
    _turtle_fill_rect(-200, 100, 350, 100, c)
    __flush()


# 前车轮
def car_wheel1(c='#FFD601'):
    turtle.screensize(800, 600)
    _turtle_fill_circle(-100, -50, 50, c)
    __flush()


# 后车轮
def car_wheel2(c='#FFD601'):
    turtle.screensize(800, 600)
    _turtle_fill_circle(50, -50, 50, c)
    __flush()


def car():
    try:
        turtle.screensize(800, 600)
        car_head()
        car_body()
        car_wheel1()
        car_wheel2()
        stop()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############LOGO###################
#####################################


def logo():
    try:
        canvas()
        pen_speed(6)
        pen_color('#FD5C09')
        _turtle_fill_rect(-50, 50, 100, 100, '#FD5C09')
        pen_color('black')
        _turtle_fill_circle(0, -40, 40, 'black')
        pen_color('#FEB084')
        _turtle_fill_circle(-13, -7.5, 15, '#FEB084')
        _turtle_fill_circle(13, -7.5, 15, '#FEB084')
        _turtle_fill_circle(0, -27.5, 15, '#FEB084')
        __flush()
    except (ParameterTypeError, ParameterValueError) as e:
        raise e
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')



#####################################
############Python画画################
#####################################
# start from the most northwest corner of the computer.
def _cxhh_computer():
    turtle.pensize(4)
    turtle.pencolor('blue')
    turtle.seth(10)
    turtle.circle(-500, 16)
    turtle.rt(90)
    turtle.fd(10)
    turtle.rt(90)
    turtle.circle(500, 14)
    turtle.lt(85)
    turtle.fd(85)
    turtle.rt(90)
    turtle.fd(15)
    turtle.rt(90)
    turtle.fd(90)
    turtle.rt(120)
    turtle.fd(90)
    turtle.seth(265)
    turtle.circle(500, 8)
    turtle.lt(88)
    turtle.circle(550, 9)
    turtle.seth(90)
    turtle.fd(60)
    turtle.lt(85)
    turtle.circle(500, 10)
    turtle.pu()
    turtle.seth(40)
    turtle.fd(79)
    turtle.seth(-63)
    turtle.pd()
    turtle.fd(52)
    turtle.pu()
    turtle.seth(-160)
    turtle.fd(147)
    turtle.seth(-22)
    turtle.pd()
    turtle.fd(63)
    turtle.pu()
    turtle.bk(20)
    turtle.seth(-120)
    turtle.pd()
    turtle.circle(17, 60)
    turtle.lt(30)
    turtle.circle(50, 50)
    turtle.lt(30)
    turtle.circle(17, 60)
    turtle.pu()
    turtle.lt(180)
    turtle.circle(-17, 60)
    turtle.seth(-40)
    turtle.pd()
    turtle.circle(-50, 40)
    turtle.seth(-160)
    turtle.circle(-100, 42)
    turtle.seth(90)
    turtle.circle(-50, 40)
    turtle.pu()
    turtle.left(180)
    turtle.circle(-50, 10)
    turtle.seth(-39)
    turtle.pd()
    turtle.circle(50, 70)


# the key on the keyboard,start from the most southeast corner of the computer.
def _cxhh_square():
    turtle.seth(110)
    turtle.fd(7)
    turtle.lt(90)
    turtle.fd(9)
    turtle.lt(90)
    turtle.fd(7)
    turtle.lt(90)
    turtle.fd(9)


# start from the most southeast corner of the computer.
def _cxhh_keyboard():
    turtle.pencolor('red')
    turtle.seth(110)
    turtle.fd(20)
    turtle.lt(90)
    turtle.fd(120)
    turtle.lt(110)
    turtle.fd(40)
    turtle.lt(73)
    turtle.fd(100)
    turtle.seth(100)
    turtle.pu()
    turtle.fd(5)
    turtle.pd()
    _cxhh_square()
    turtle.bk(9)
    _cxhh_square()
    turtle.bk(9)
    _cxhh_square()
    turtle.bk(9)
    _cxhh_square()
    turtle.bk(9)
    _cxhh_square()
    turtle.bk(9)
    _cxhh_square()
    turtle.bk(9)
    turtle.fd(45 + 9)
    turtle.lt(90)
    turtle.fd(7)
    _cxhh_square()
    turtle.bk(9)
    _cxhh_square()
    turtle.bk(9)
    _cxhh_square()
    turtle.pu()
    turtle.bk(18)
    turtle.lt(90)
    turtle.fd(7)
    turtle.pd()
    turtle.fd(7)
    turtle.lt(90)
    turtle.fd(35)
    turtle.lt(90)
    turtle.fd(7)
    turtle.lt(90)
    turtle.fd(35)
    turtle.pu()
    turtle.bk(44)
    turtle.pd()
    _cxhh_square()
    turtle.bk(9)
    _cxhh_square()
    turtle.fd(9)
    turtle.rt(90)
    turtle.fd(7)
    _cxhh_square()
    turtle.bk(9)
    _cxhh_square()
    turtle.fd(9)
    turtle.rt(90)
    turtle.fd(7)
    _cxhh_square()
    turtle.bk(9)
    _cxhh_square()


# start from the most southeast corner of the programmer.
def _cxhh_programmer():
    turtle.pencolor('purple')
    turtle.seth(90)
    turtle.fd(50)
    turtle.seth(45)
    turtle.circle(70, 10)
    turtle.pu()
    turtle.circle(70, 58)
    turtle.pd()
    turtle.circle(70, 202)
    turtle.seth(-100)
    turtle.circle(500, 10)
    turtle.pu()
    turtle.seth(70)
    turtle.fd(170)
    turtle.pd()
    turtle.seth(-90)
    turtle.fd(15)
    turtle.rt(80)
    turtle.fd(10)
    turtle.seth(25)
    turtle.pu()
    turtle.fd(45)
    turtle.pd()
    turtle.seth(-70)
    turtle.fd(15)
    turtle.seth(10)
    turtle.fd(10)
    turtle.pu()
    turtle.seth(-100)
    turtle.fd(15)
    turtle.seth(-175)
    turtle.pd()
    turtle.pensize(8)
    turtle.fd(1)
    turtle.pu()
    turtle.fd(40)
    turtle.pd()
    turtle.fd(1)
    turtle.pensize(4)
    turtle.seth(-30)
    turtle.pu()
    turtle.fd(20)
    turtle.pd()
    turtle.seth(-40)
    turtle.circle(13, 50)


# the beginning angle is theta
def _cxhh_questionmark(theta):
    turtle.pd()
    turtle.pensize(4)
    turtle.seth(theta)
    turtle.fd(6)
    turtle.circle(-8, 180)
    turtle.lt(60)
    turtle.pu()
    turtle.fd(12)
    turtle.pd()
    turtle.pensize(5)
    turtle.fd(1)
    turtle.pu()


def programmer():
    try:
        turtle.tracer(10)
        _cxhh_computer()
        turtle.pu()
        turtle.seth(-170)
        turtle.fd(65)
        turtle.pd()
        turtle.pensize(3)
        _cxhh_keyboard()
        turtle.pu()
        turtle.seth(180)
        turtle.fd(130)
        turtle.pd()
        turtle.pensize(3)
        turtle.pencolor('black')
        turtle.seth(20)
        turtle.fd(237)
        turtle.pu()
        turtle.fd(114)
        turtle.pd()
        turtle.fd(40)
        turtle.rt(50)
        turtle.fd(60)
        turtle.pu()
        turtle.bk(60)
        turtle.rt(130)
        turtle.fd(220)
        turtle.pd()
        _cxhh_programmer()
        turtle.pu()
        turtle.seth(105)
        turtle.fd(120)
        _cxhh_questionmark(30)
        turtle.seth(40)
        turtle.fd(30)
        _cxhh_questionmark(15)
        turtle.seth(1)
        turtle.fd(30)
        _cxhh_questionmark(1)
        turtle.seth(145)
        turtle.fd(135)
        turtle.seth(90)
        turtle.fd(80)
        turtle.pd()
        turtle.pencolor('black')
        turtle.write('Python还能画画？？', move=False, align="left", font=("华文彩云", 23, 'normal'))
        turtle.pu()
        turtle.hideturtle()
        turtle.update()
        turtle.sleep(1)
        turtle.seth(270)
        turtle.fd(60)
        turtle.pd()
        turtle.write('当然可以！！', move=False, align="left", font=("华文彩云", 40, 'normal'))
        stop()
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


#####################################
###############彩蛋#################
#####################################
def egg():
    try:
        turtle.screensize(700, 700)
        x = random.randint(-250, 250)
        y = random.randint(-250, 250)
        size = random.randint(10, 50)
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)

        turtle.color(rgb(r, g, b), rgb(r, g, b))
        turtle.begin_fill()
        turtle.penup()
        turtle.goto(x, y - size)
        turtle.pendown()
        turtle.circle(size)
        turtle.end_fill()
        turtle.goto(x, y - size * 0.36)

        turtle.color('white')
        ybc = ['Y', 'B', 'C']
        turtle.write(random.choice(ybc), align='center', font=('Arial', size, 'normal'))
        __flush()
    except Exception as e:
        raise InternalError(e, 'ybc_tuya')


def __checkout_color(method_name, color):
    if not isinstance(color, str):
        raise ParameterTypeError(method_name, "'color'")


if __name__ == '__main__':
    # canvas()
    # pen_speed(6)

    # logo()
    # xzpq()
    # Doraemon
    # shield()
    # screw()
    # flappy()
    # car()
    # yqcr()
    # programmer()
    # for i in range(10):
    #     egg()
    turtle.speed(0)
    # robot()
    # logo()
    turtle.goto(0, 50)
    turtle.goto(50, 50)
    draw_circle(0, 0, 50)
    fill_circle(50, 50, 50)
    turtle.done()
