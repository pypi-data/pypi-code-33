import pyaudio
import requests
import webrtcvad
import ybc_config
import ybc_speech
from ybc_exception import *
from random import choice
import collections
import sys
import time
import wave
import pypinyin
import turtle
import ybc_tuya
import ybc_browser
from array import array
from struct import pack

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

__PREFIX = ybc_config.config['prefix']
__IDIOM_URL = __PREFIX + ybc_config.uri + '/bot'


def listen(filename=''):
    if not isinstance(filename, str):
        raise ParameterTypeError(function_name=sys._getframe().f_code.co_name, error_msg="'filename'")
    if filename == '':
        raise ParameterValueError(function_name=sys._getframe().f_code.co_name, error_msg="'filename'")

    try:
        __FORMAT = pyaudio.paInt16
        __CHANNELS = 1
        __RATE = 16000
        __CHUNK_DURATION_MS = 30  # supports 10, 20 and 30 (ms)
        __PADDING_DURATION_MS = 1500  # 1 sec judgement
        __CHUNK_SIZE = int(__RATE * __CHUNK_DURATION_MS / 1000)  # chunk to read
        __CHUNK_BYTES = __CHUNK_SIZE * 2  # 16bit = 2 bytes, PCM
        __NUM_PADDING_CHUNKS = int(__PADDING_DURATION_MS / __CHUNK_DURATION_MS)
        __NUM_WINDOW_CHUNKS = int(400 / __CHUNK_DURATION_MS)  # 400 ms/ 30ms  ge
        __NUM_WINDOW_CHUNKS_END = __NUM_WINDOW_CHUNKS * 2
        __START_OFFSET = int(__NUM_WINDOW_CHUNKS * __CHUNK_DURATION_MS * 0.5 * __RATE)

        def _record_to_file(path, data, sample_width):
            """Records from the microphone and outputs the resulting data to 'path'"""
            data = pack('<' + ('h' * len(data)), *data)
            wf = wave.open(path, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(sample_width)
            wf.setframerate(__RATE)
            wf.writeframes(data)
            wf.close()

        def _normalize(snd_data):
            """Average the volume out"""
            maximum = 32767  # 16384
            times = float(maximum) / max(abs(i) for i in snd_data)
            r = array('h')
            for i in snd_data:
                r.append(int(i * times))
            return r

        vad = webrtcvad.Vad(1)
        pa = pyaudio.PyAudio()
        stream = pa.open(format=__FORMAT, channels=__CHANNELS, rate=__RATE, input=True, start=False,
                         frames_per_buffer=__CHUNK_SIZE)
        got_a_sentence = False
        leave = False

        while not leave:
            ring_buffer = collections.deque(maxlen=__NUM_PADDING_CHUNKS)
            triggered = False
            ring_buffer_flags = [0] * __NUM_WINDOW_CHUNKS
            ring_buffer_index = 0
            ring_buffer_flags_end = [0] * __NUM_WINDOW_CHUNKS_END
            ring_buffer_index_end = 0
            raw_data = array('h')
            index = 0
            start_point = 0
            start_time = time.time()
            print("请说话")
            stream.start_stream()
            while not got_a_sentence and not leave:
                chunk = stream.read(__CHUNK_SIZE)
                # add WangS
                raw_data.extend(array('h', chunk))
                index += __CHUNK_SIZE
                time_use = time.time() - start_time
                active = vad.is_speech(chunk, __RATE)
                ring_buffer_flags[ring_buffer_index] = 1 if active else 0
                ring_buffer_index += 1
                ring_buffer_index %= __NUM_WINDOW_CHUNKS
                ring_buffer_flags_end[ring_buffer_index_end] = 1 if active else 0
                ring_buffer_index_end += 1
                ring_buffer_index_end %= __NUM_WINDOW_CHUNKS_END

                # start point detection
                if not triggered:
                    ring_buffer.append(chunk)
                    num_voiced = sum(ring_buffer_flags)
                    if num_voiced > 0.80 * __NUM_WINDOW_CHUNKS:
                        print("正在录音...")
                        triggered = True
                        start_point = index - __CHUNK_SIZE * 20  # start point
                        ring_buffer.clear()
                # end point detection
                else:
                    ring_buffer.append(chunk)
                    num_unvoiced = __NUM_WINDOW_CHUNKS_END - sum(ring_buffer_flags_end)
                    if num_unvoiced > 0.85 * __NUM_WINDOW_CHUNKS_END or time_use > 15:
                        print("录音完成，正在提交声音")
                        triggered = False
                        got_a_sentence = True
                # sys.stdout.flush()
            stream.stop_stream()
            got_a_sentence = False

            # write to file
            raw_data.reverse()
            for index in range(start_point):
                raw_data.pop()
            raw_data.reverse()
            raw_data = _normalize(raw_data)
            _record_to_file(filename, raw_data, 2)
            print("声音已提交")
            leave = True
        stream.close()

        return filename
    except Exception as e:
        raise InternalError(e, 'ybc_bot')


def answer_voice(filename=''):
    if not isinstance(filename, str):
        raise ParameterTypeError(function_name=sys._getframe().f_code.co_name, error_msg="'filename'")
    if filename == '':
        raise ParameterValueError(function_name=sys._getframe().f_code.co_name, error_msg="'filename'")

    try:
        print("机器人正在分析音频")
        text = ybc_speech.voice2text(filename)
        return chat(text)
    except Exception as e:
        raise InternalError(e, 'ybc_bot')


def chat(text=''):
    """
    功能：与小猿机器人对话聊天

    参数 text: 聊天内容

    返回: 小猿机器人的回复内容
    """
    error_msg = "'text'"
    if not isinstance(text, str):
        raise ParameterTypeError(function_name=sys._getframe().f_code.co_name, error_msg=error_msg)
    if text == '':
        raise ParameterValueError(function_name=sys._getframe().f_code.co_name, error_msg=error_msg)
    try:
        data = {
            'text': text
        }
        url = __IDIOM_URL
        for i in range(3):
            r = requests.post(url, data=data)
            if r.status_code == 200:
                res = r.json()
                if res['results']:
                    if 'text' in res['results'][0]['values'].keys():
                        res = res['results'][0]['values']['text']
                    else:
                        res = res['results'][1]['values']['text'] + " " + res['results'][0]['values']['url']
                    return res

        raise ConnectionError('获取机器人对话失败', r._content)

    except Exception as e:
        raise InternalError(e, 'ybc_bot')


def drawing():
    """
    功能：录制一段语音，打开语音指定的 ybc_tuya 方法

    参数：无

    返回：若正常调用ybc_tuya命令则返回 0，否则返回-1
    """
    try:
        command = _get_command()
        if command == -1:
            return command

        res = ''.join(pypinyin.lazy_pinyin(command))
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

        print('没有识别到可执行的命令，送你一幅画吧')
        ybc_tuya.programmer()
        return -1
    except Exception as e:
        raise InternalError(e, 'ybc_bot')


def website():
    """
    功能：录制一段语音，打开语音指定的网址

    参数：无

    返回：若正常打开网页则返回 0，否则返回-1
    """
    try:
        command = _get_command()
        if command == -1:
            return command

        if ybc_browser.open_browser(command) != -1:
            return 0
        else:
            return -1

    except Exception as e:
        raise InternalError(e, 'ybc_bot')


def _get_command():
    filename = ybc_speech.record("tmp.wav", 4)
    if not filename:
        print("没有接收到指令")
        return -1
    print("正在识别，请稍等..")
    return ybc_speech.voice2text(filename)


def main():
    filename = "test.wav"
    listen(filename)
    print("回答: ", answer_voice(filename))


if __name__ == '__main__':
    main()
