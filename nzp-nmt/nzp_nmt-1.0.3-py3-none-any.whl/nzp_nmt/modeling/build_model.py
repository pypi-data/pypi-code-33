# -*- coding: utf-8 -*-
"""
定义模型
"""
import numpy as np
import tensorflow as tf
from modeling.create_layers import AdvantageLayer
from utils.tools import spectrogram2wav


class BaseModel(AdvantageLayer):

    def __init__(self, hp, mode, data_processing):
        """

        :param hp:
        :param mode:
        :param data_processing:
        """
        AdvantageLayer.__init__(self, hp)
        self.chinese2no = data_processing.chinese2no
        self.english2no = data_processing.english2no
        self.no2chinese = data_processing.no2chinese
        self.no2english = data_processing.no2english
        self.char2idx = data_processing.char2idx
        self.text_normalize = data_processing.text_normalize
        if mode == "train":
            if hp.train_type == "nmt":
                self._num_batch, self._input_chinese, \
                self._input_english, self._output_english = data_processing.get_batch()
                self._keep_prob = self._hp.keep_prob
            if hp.train_type == "tts":
                self._num_batch, self._english_char, self._f_name, self._mel, self._mag = data_processing.get_batch()
            if hp.train_type == "nmt2tts":
                self._num_batch, self._input_chinese, self._input_english, self._output_english, \
                self._f_name, self._mel, self._mag = data_processing.get_batch()
                self._keep_prob = self._hp.keep_prob
        elif mode == "test":
            if hp.predict_type == "nmt":
                self._input_chinese = tf.placeholder(tf.int32, shape=(None, None))
                self._input_english = tf.placeholder(tf.int32, shape=(None, None))
                self._keep_prob = 1.0
            if hp.predict_type == "tts":
                self._english_char = tf.placeholder(tf.int32, shape=(None, None))
                self._mel = tf.placeholder(tf.float32, shape=(None, None, hp.n_mels * hp.r))
            if hp.predict_type == "nmt2tts":
                self._input_chinese = tf.placeholder(tf.int32, shape=(None, None))
                self._input_english = tf.placeholder(tf.int32, shape=(None, None))
                self._keep_prob = 1.0
                self._mel = tf.placeholder(tf.float32, shape=(None, None, hp.n_mels * hp.r))

    @property
    def num_batch(self):
        return self._num_batch


class TranslateModel(BaseModel):

    def __init__(self, hp, **kwargs):
        super(TranslateModel, self).__init__(hp=hp, mode=kwargs["mode"], data_processing=kwargs["data_processing"])
        self._object = "This is translate model!"
        # 定义翻译模型
        with tf.variable_scope("nmt_net"):
            # 中文词序输入词嵌入层
            self._mnt_encoder_inputs = \
                self.embedding(
                    self._input_chinese,
                    len(self.chinese2no) + 1,
                    self._hp.embed_size,
                    scope="mnt-encoder-embedding"
                )
            # 英文词序输入词嵌入层
            self._mnt_decoder_inputs = \
                self.embedding(
                    self._input_english,
                    len(self.english2no) + 1,
                    self._hp.embed_size,
                    scope="mnt-decoder-embedding"
                )
            # 目标输入层
            if kwargs["mode"] == "train":
                self._mnt_decoder_target = self._output_english
            # 翻译模型编码层
            self._mnt_memory = \
                self.nlp_encoder(self._mnt_encoder_inputs, self._keep_prob, is_training=kwargs["is_training"])
            # 翻译模型解码层
            self._decoder_outputs, self._nmt_alignments = \
                self.nlp_decoder(self._mnt_decoder_inputs, self._mnt_memory, is_training=kwargs["is_training"])
            # 翻译模型词表映射层
            self._mapping_vocab = \
                self.mapping_vocab_net(self._decoder_outputs, num_units=len(self.english2no))
            tf.logging.info("mapping_vocab shape:{}".format(self._mapping_vocab.shape))
            # 贪心查找最大概率的出现的词
            self._arg_max_mapping_vocab = tf.argmax(self._mapping_vocab, 2)
            tf.logging.info("arg_max_mapping_vocab shape:{}".format(self._arg_max_mapping_vocab.shape))
            # 定义损失函数
            if kwargs["mode"] == "train":
                self._nmt_loss = tf.reduce_mean(
                    tf.nn.softmax_cross_entropy_with_logits(
                        labels=tf.one_hot(self._mnt_decoder_target, depth=len(self.english2no), dtype=tf.float32),
                        logits=self._mapping_vocab
                    )
                )
        # 输出翻译文本
        if kwargs["mode"] == "train":
            self.chinese_text_output = \
                tf.py_func(self._rebuild_chinese_text_to_show, [self._input_chinese[0]], tf.string)
            self.english_text_output = \
                tf.py_func(self._rebuild_english_text_to_show, [self._output_english[0]], tf.string)
            self.english_text_predict = \
                tf.py_func(self._rebuild_english_text_to_show, [self._arg_max_mapping_vocab[0]], tf.string)
            # summary tensor_board
            tf.summary.scalar('{}/nmt_loss'.format(kwargs["mode"]), self._nmt_loss)
            tf.summary.text('{}/chinese_text_output'.format(kwargs["mode"]), self.chinese_text_output)
            tf.summary.text('{}/english_text_output'.format(kwargs["mode"]), self.english_text_output)
            tf.summary.text('{}/english_text_predict'.format(kwargs["mode"]), self.english_text_predict)

    def __str__(self):
        return self._object

    def _rebuild_chinese_text_to_show(self, input_data):
        """

        :param input_data: 输入中文tensor
        :return: numpy.array
        """
        return "".join([self.no2chinese[index]
                        for index in input_data if self.no2chinese.get(index) and index != 0])

    def _rebuild_english_text_to_show(self, input_data):
        """

        :param input_data: 输入英文tensor
        :return: numpy.array
        """
        return " ".join([self.no2english[index]
                         for index in input_data if self.no2english.get(index) and index != 0])

    @property
    def input_chinese(self):
        return self._input_chinese

    @property
    def input_english(self):
        return self._input_english

    @property
    def nmt_alignments(self):
        return self._nmt_alignments

    @property
    def decoder_outputs(self):
        return self._decoder_outputs

    @property
    def arg_max_mapping_vocab(self):
        return self._arg_max_mapping_vocab

    @property
    def nmt_loss(self):
        return self._nmt_loss


class TacoTron(BaseModel):

    def __init__(self, hp, **kwargs):
        super(TacoTron, self).__init__(hp, mode=kwargs["mode"], data_processing=kwargs["data_processing"])
        self._object = "This is TacoTron!"
        if hp.train_type == "nmt2tts" or hp.predict_type == "nmt2tts":
            self._translate_model = TranslateModel(
                hp, mode=kwargs["mode"], is_training=kwargs["is_training"], data_processing=kwargs["data_processing"]
            )
        # 定义语音模型
        with tf.variable_scope("tts_net"):
            # 英文字符序列嵌入层 （来自翻译模型解码结果）
            if kwargs["train_type"] == "single":
                self._tts_encoder_inputs = \
                    self.embedding(
                        self._english_char,
                        len(self._hp.vocab),
                        self._hp.embed_size,
                        scope="tts-encoder-embedding"
                    )  # (N, T_x, E)
            elif kwargs["train_type"] == "union":
                self._rebuild_text = \
                    tf.py_func(self._rebuild_text_to_embedding, [self._translate_model.arg_max_mapping_vocab], tf.int32)
                self._rebuild_text.set_shape((None, None))
                self._tts_encoder_inputs = \
                    self.embedding(
                        self._rebuild_text,
                        len(self._hp.vocab),
                        self._hp.embed_size,
                        scope="tts-encoder-embedding"
                    )  # (N, T_x, E)
            # 语音输入层
            tts_decoder_inputs \
                = tf.concat((tf.zeros_like(self._mel[:, :1, :]), self._mel[:, :-1, :]), 1)  # (N, Ty/r, n_mels*r)
            self._tts_decoder_inputs = tts_decoder_inputs[:, :, -hp.n_mels:]  # feed last frames only (N, Ty/r, n_mels)
            # 目标输入层
            if kwargs["mode"] == "train":
                self._tts_decoder_mal = self._mel
                self._tts_decoder_mag = self._mag
            # 语音模型编码层
            self._tts_memory = \
                self.voice_encoder(self._tts_encoder_inputs, is_training=kwargs["is_training"])  # (N, T_x, E)
            # 语音模型第一次解码
            self._y_hat, self._tts_alignments = \
                self.voice_decoder_1(
                    self._tts_decoder_inputs, self._tts_memory, is_training=kwargs["is_training"]
                )  # (N, T_y//r, n_mels*r)
            # 语音模型第二次解码
            self._z_hat = \
                self.voice_decoder_2(
                    self._y_hat, is_training=kwargs["is_training"]
            )  # (N, T_y//r, (1+n_fft//2)*r)
            if kwargs["mode"] == "train":
                # 定义损失函数
                self._mel_loss = tf.reduce_mean(tf.abs(self._y_hat - self._tts_decoder_mal))
                self._mag_loss = tf.reduce_mean(tf.abs(self._z_hat - self._tts_decoder_mag))
                self._tts_loss = self._mel_loss + self._mag_loss

                # 加入翻译模型损失
                if kwargs["train_type"] == "union":
                    self._total_loss = self._translate_model.nmt_loss + self._tts_loss
        if kwargs["mode"] == "train":
            # 输出的语音
            # self.english_input =
            self.audio = tf.py_func(spectrogram2wav, [self._z_hat[0]], tf.float32)
            # summary tensor_board
            tf.summary.scalar('{}/tts_loss'.format(kwargs["mode"]), self._tts_loss)
            if kwargs["train_type"] == "union":
                tf.summary.scalar('{}/total_loss'.format(kwargs["mode"]), self.total_loss)
            tf.summary.scalar('{}/lr'.format(kwargs["mode"]), hp.lr)
            # tf.summary.text('{}/english_input'.format(kwargs["mode"]), self.english_input)
            tf.summary.audio("{}/sample".format(kwargs["mode"]), tf.expand_dims(self.audio, 0), hp.sr)

    def __str__(self):
        return self._object

    def _rebuild_text_to_embedding(self, input_data):
        """

        :param input_data:
        :return:
        """
        returns = []
        for text_in in input_data:
            text_english = ''
            for single_text in text_in:
                text_english += self.no2english[single_text] + ' ' if self.no2english.get(single_text) else ""
            text = self.text_normalize(text_english.strip(' ')) + "E"
            text = [self.char2idx[char] for char in text]
            returns.append(text)
        max_len = max([len(x) for x in returns])
        padding_zeros = np.zeros(shape=[len(returns), max_len], dtype=np.int32)
        for i, seq in enumerate(returns):
            for j, element in enumerate(seq):
                padding_zeros[i, j] = element
        return padding_zeros

    @property
    def tts_alignments(self):
        return self._tts_alignments

    @property
    def nmt_loss(self):
        return self._translate_model.nmt_loss

    @property
    def tts_loss(self):
        return self._tts_loss
        
    @property
    def total_loss(self):
        return self._total_loss

    @property
    def english_char(self):
        return self._english_char

    @property
    def input_mel(self):
        return self._mel

    @property
    def y_hat(self):
        return self._y_hat

    @property
    def z_hat(self):
        return self._z_hat
