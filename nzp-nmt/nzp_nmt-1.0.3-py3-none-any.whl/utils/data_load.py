# -*- coding: utf-8 -*-
"""
定义加载数据
"""

from __future__ import print_function

import re
import os
import jieba
import codecs
import nltk
import unicodedata
import numpy as np
import tensorflow as tf
from pickle import load, dump
from utils.tools import load_spectrograms


class DataProcessing(object):

    def __init__(self, hp, **kwargs):
        self._object = "This is data processing!"
        self._hp = hp
        self.char2idx = {}
        self.idx2char = {}
        self.english2no = {}
        self.no2english = {}
        self.chinese2no = {}
        self.no2chinese = {}
        if hp.train_type == "nmt":
            self._load_vocab(kwargs["mode"], kwargs["model_path"])
        if hp.train_type == "tts":
            self._load_char_vocab()
        if hp.train_type == "nmt2tts":
            self._load_vocab(kwargs["mode"], kwargs["model_path"])
            self._load_char_vocab()

    def __str__(self):
        return self._object

    def _load_vocab(self, mode, model_path):
        """  加载词表
             english2no 英文词序表
             no2english 英文反转词序表
             chinese2no 中文词序表
             no2chinese 中文反转词序表
        :return: char2idx, idx2char, english2no, no2english, chinese2no, no2chinese
        """
        if mode == "train":
            special_vec = ["_pad_", "_unk_", "_go_", "_eos_"]
            # 加载中文词表
            with open(self._hp.chinese_vocab, 'r', encoding="utf-8") as f:
                self.chinese2no = {k.replace("\n", ""): v for v, k in enumerate(special_vec + list(set(f.readlines())))}
            self.no2chinese = {v: k for k, v in self.chinese2no.items()}
            # 加载英文词表
            with open(self._hp.english_vocab, 'r') as f:
                self.english2no = {k.replace("\n", ""): v for v, k in enumerate(special_vec + list(set(f.readlines())))}
            self.no2english = {v: k for k, v in self.english2no.items()}
        elif mode == "predict":
            # 加载中文词表
            with open(model_path + "chinese2no.pkl", "rb") as f:
                self.chinese2no = load(f)
            self.no2chinese = {v: k for k, v in self.chinese2no.items()}
            # 加载英文词表
            with open(model_path + "english2no.pkl", "rb") as f:
                self.english2no = load(f)
            self.no2english = {v: k for k, v in self.english2no.items()}

    def _load_char_vocab(self):
        """ 加载英文字符词表
            char2idx 英文字符词表
            idx2char 英文字符反转词表
        :return:
        """
        self.char2idx = {char: idx for idx, char in enumerate(self._hp.vocab)}
        self.idx2char = {idx: char for idx, char in enumerate(self._hp.vocab)}

    def text_normalize(self, text):
        """  文本归一化

        :param text: 传入文本
        :return: 处理后的文本
        """
        text = ''.join(char for char in unicodedata.normalize('NFD', text) if unicodedata.category(char) != 'Mn')
        text = text.lower()
        text = re.sub("[^{}]".format(self._hp.vocab), " ", text)
        text = re.sub("[ ]+", " ", text)
        return text

    def load_data(self, mode="train"):
        """

        :param mode: 训练模式，预测模式
        :return: wav_paths 音频文件路径
                  seq_length 文本序列长度
                  chinese_text 中文文本
                  input_chinese 输入的中文文本序列 eg：[19, 10, 10, 1, 2, 3]
                  input_english 输入的英文文本序列 eg: [0, 1, 2, 3, 4]   0 表示 _go_ 向量
                  output_english 输出的英文文本序列 eg: [1, 2, 3, 4, 5]  5 表示 _eos_ 向量
        """
        if mode in ("train", "eval"):
            # # Parse
            wav_paths, seq_length, english_char, input_chinese, input_english, output_english = [], [], [], [], [], []
            transcript = os.path.join(self._hp.text_data, self._hp.train_data_file)
            lines = codecs.open(transcript, 'r', 'utf-8').readlines()
            if mode == "train":
                lines = lines[1:]
            else:  # We attack only one sample!
                lines = lines[:1]
            wno, chinese_text, english_text = None, None, None
            if self._hp.train_type == "nmt":
                for line in lines:
                    try:
                        wno, chinese_text, english_text = line.strip().split(" | ")
                    except Exception as e:
                        print("The {} has some problem like {}".format(wno, str(e)))
                    # 翻译模型的输入 ----> 序列转换为字符编码
                    chinese_text_seq = [self.chinese2no[word] if self.chinese2no.get(word) else self.chinese2no["_unk_"]
                                        for word in jieba.lcut(chinese_text)]
                    seq_length.append(len(chinese_text_seq))
                    input_chinese.append(np.array(chinese_text_seq, np.int32).tostring())
                    # 单词统一转换为小写表示
                    input_english.append(np.array(
                        [self.english2no["_go_"]] +
                        [self.english2no[word.lower()] if self.english2no.get(word.lower()) else self.english2no["_unk_"]
                         for word in nltk.word_tokenize(english_text)], np.int32).tostring())
                    output_english.append(np.array(
                        [self.english2no[word.lower()] if self.english2no.get(word.lower()) else self.english2no["_unk_"]
                         for word in nltk.word_tokenize(english_text)] +
                        [self.english2no["_eos_"]], np.int32).tostring())
                return seq_length, input_chinese, input_english, output_english
            if self._hp.train_type == "tts":
                for line in lines:
                    try:
                        wno, chinese_text, english_text = line.strip().split(" | ")
                    except Exception as e:
                        print("The {} has some problem like {}".format(wno, str(e)))
                    # 音频文件的输入
                    text = self.text_normalize(english_text)
                    wav_path = os.path.join(self._hp.voice_data, "wavs", wno + ".wav")
                    wav_paths.append(wav_path)
                    # 英文字符输入
                    text = [self.char2idx[char] for char in text]
                    seq_length.append(len(text))
                    english_char.append(np.array(text, np.int32).tostring())
                return wav_paths, seq_length, english_char
            if self._hp.train_type == "nmt2tts":
                for line in lines:
                    try:
                        wno, chinese_text, english_text = line.strip().split(" | ")
                    except Exception as e:
                        print("The {} has some problem like {}".format(wno, str(e)))
                    # 音频文件的输入
                    # 翻译模型的输入 ----> 序列转换为字符编码
                    chinese_text_seq = [self.chinese2no[word] if self.chinese2no.get(word) else self.chinese2no["_unk_"]
                                        for word in jieba.lcut(chinese_text)]
                    seq_length.append(len(chinese_text_seq))
                    input_chinese.append(np.array(chinese_text_seq, np.int32).tostring())
                    input_english.append(np.array(
                        [self.english2no["_go_"]] +
                        [self.english2no[word] if self.english2no.get(word) else self.english2no["_unk_"]
                         for word in nltk.word_tokenize(english_text)], np.int32).tostring())
                    output_english.append(np.array(
                        [self.english2no[word] if self.english2no.get(word) else self.english2no["_unk_"]
                         for word in nltk.word_tokenize(english_text)] +
                        [self.english2no["_eos_"]], np.int32).tostring())
                    # 音频文件的输入
                    wav_path = os.path.join(self._hp.voice_data, "wavs", wno + ".wav")
                    wav_paths.append(wav_path)
                return wav_paths, seq_length, input_chinese, input_english, output_english

    def get_batch(self) -> object:
        """ 加载数据到队列
        :return:  tensor by fpaths, text_lengths, texts, InputChinese, InputEnglish, OutputEnglish
        """
        with tf.device('/cpu:0'):
            if self._hp.train_type == "nmt":
                seq_length, input_chinese, input_english, output_english = self.load_data()
                max_len, min_len = max(seq_length), min(seq_length)
                # Calc total batch count
                num_batch = len(seq_length) // self._hp.batch_size
                tensor_seq_length = tf.convert_to_tensor(seq_length)
                tensor_input_chinese = tf.convert_to_tensor(input_chinese)
                tensor_input_english = tf.convert_to_tensor(input_english)
                tensor_output_english = tf.convert_to_tensor(output_english)
                # 将各个tensor放置于列队
                _seq_length, _input_chinese, _input_english, _output_english = \
                    tf.train.slice_input_producer(
                        [tensor_seq_length,
                         tensor_input_chinese, tensor_input_english, tensor_output_english], shuffle=True)
                # 字符编码转换为序列
                _input_chinese = tf.decode_raw(_input_chinese, tf.int32)
                _input_english = tf.decode_raw(_input_english, tf.int32)
                _output_english = tf.decode_raw(_output_english, tf.int32)
                # 设定tensor shape
                _input_chinese.set_shape((None,))
                _input_english.set_shape((None,))
                _output_english.set_shape((None,))
                # Batching
                _, (b_input_chinese, b_input_english, b_output_english) = \
                    tf.contrib.training.bucket_by_sequence_length(
                        input_length=_seq_length,
                        tensors=[_input_chinese, _input_english, _output_english],
                        batch_size=self._hp.batch_size,
                        bucket_boundaries=[i for i in range(min_len + 1, max_len - 1, 20)],
                        num_threads=16,
                        capacity=self._hp.batch_size * 4,
                        dynamic_pad=True)
                return num_batch, b_input_chinese, b_input_english, b_output_english

            if self._hp.train_type == "tts":
                wav_paths, seq_length, english_char = self.load_data()
                max_len, min_len = max(seq_length), min(seq_length)
                # Calc total batch count
                num_batch = len(wav_paths) // self._hp.batch_size
                tensor_wav_paths = tf.convert_to_tensor(wav_paths)
                tensor_english_char = tf.convert_to_tensor(english_char)
                tensor_seq_length = tf.convert_to_tensor(seq_length)
                # 将各个tensor放置于列队
                _wav_paths, _seq_length, _english_char = \
                    tf.train.slice_input_producer(
                        [tensor_wav_paths, tensor_seq_length, tensor_english_char], shuffle=True)
                # 字符编码转换为序列
                _english_char = tf.decode_raw(_english_char, tf.int32)
                # 设定tensor shape
                _english_char.set_shape((None,))
                f_name, mel, mag = tf.py_func(load_spectrograms, [_wav_paths], [tf.string, tf.float32, tf.float32])
                # (None, n_mels)
                # Add shape information
                f_name.set_shape(())
                mel.set_shape((None, self._hp.n_mels * self._hp.r))
                mag.set_shape((None, self._hp.n_fft // 2+1))
                # Batching
                _, (b_english_char, b_f_name, b_mel, b_mag) = \
                    tf.contrib.training.bucket_by_sequence_length(
                        input_length=_seq_length,
                        tensors=[_english_char, f_name, mel, mag],
                        batch_size=self._hp.batch_size,
                        bucket_boundaries=[i for i in range(min_len + 1, max_len - 1, 20)],
                        num_threads=16,
                        capacity=self._hp.batch_size * 4,
                        dynamic_pad=True)
                return num_batch, b_english_char, b_f_name, b_mel, b_mag

            if self._hp.train_type == "nmt2tts":
                wav_paths, seq_length, input_chinese, input_english, output_english = self.load_data()
                max_len, min_len = max(seq_length), min(seq_length)
                # Calc total batch count
                num_batch = len(wav_paths) // self._hp.batch_size
                tensor_wav_paths = tf.convert_to_tensor(wav_paths)
                tensor_seq_length = tf.convert_to_tensor(seq_length)
                tensor_input_chinese = tf.convert_to_tensor(input_chinese)
                tensor_input_english = tf.convert_to_tensor(input_english)
                tensor_output_english = tf.convert_to_tensor(output_english)
                # 将各个tensor放置于列队
                _wav_paths, _seq_length, _input_chinese, _input_english, _output_english = \
                    tf.train.slice_input_producer(
                        [tensor_wav_paths, tensor_seq_length,
                         tensor_input_chinese, tensor_input_english, tensor_output_english], shuffle=True)
                # 字符编码转换为序列
                _input_chinese = tf.decode_raw(_input_chinese, tf.int32)
                _input_english = tf.decode_raw(_input_english, tf.int32)
                _output_english = tf.decode_raw(_output_english, tf.int32)
                # 设定tensor shape
                _input_chinese.set_shape((None,))
                _input_english.set_shape((None,))
                _output_english.set_shape((None,))
                f_name, mel, mag = tf.py_func(load_spectrograms, [_wav_paths], [tf.string, tf.float32, tf.float32])
                # (None, n_mels)
                # Add shape information
                f_name.set_shape(())
                mel.set_shape((None, self._hp.n_mels * self._hp.r))
                mag.set_shape((None, self._hp.n_fft // 2+1))
                # Batching
                _, (b_input_chinese, b_input_english, b_output_english, b_f_name, b_mel, b_mag) = \
                    tf.contrib.training.bucket_by_sequence_length(
                        input_length=_seq_length,
                        tensors=[_input_chinese, _input_english, _output_english, f_name, mel, mag],
                        batch_size=self._hp.batch_size,
                        bucket_boundaries=[i for i in range(min_len + 1, max_len - 1, 20)],
                        num_threads=16,
                        capacity=self._hp.batch_size * 4,
                        dynamic_pad=True)
                return num_batch, b_input_chinese, b_input_english, b_output_english, b_f_name, b_mel, b_mag
