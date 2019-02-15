# -*- coding: utf-8 -*-
"""
定义各种网络层
"""
import tensorflow as tf


class Layer(object):

    def __init__(self, hp):
        self._object = "This is Layer's father!"
        self._hp = hp

    def __str__(self):
        return self._object


class BaseLayer(Layer):

    def __init__(self, hp):
        super(BaseLayer, self).__init__(hp=hp)
        self._object = "This is base layer!"

    def __str__(self):
        return self._object

    def embedding(self, inputs, vocab_size, num_units, zero_pad=True, scope="embedding", reuse=None):
        """ 词嵌入层

        Args:
          inputs: 为词序的 tensor
          vocab_size: An int. 词表大小.
          num_units: An int. 隐藏层结点数目.
          zero_pad: A boolean. 如果为真embed矩阵行为0的向量用零向量替换，默认为True
          scope: 层命名
          reuse: Boolean, 同名层可被覆盖

        Returns: (N, seq_len, num_units)
        """
        with tf.variable_scope(scope, reuse=reuse):
            lookup_table = tf.get_variable('lookup_table',
                                           dtype=tf.float32,
                                           shape=[vocab_size, num_units],
                                           initializer=tf.truncated_normal_initializer(mean=0.0, stddev=0.01))
            if zero_pad:
                lookup_table = tf.concat((tf.zeros(shape=[1, num_units]),
                                          lookup_table[1:, :]), 0)
        return tf.nn.embedding_lookup(lookup_table, inputs)

    def bn(self, inputs, is_training=True, activation_fn=None, scope="bn", reuse=None):
        """ 批标准化层

        Args:
          inputs: 二维或者更高维的tensor, 第一个维度是 batch_size. 详细参数见tf.contrib.layers.batch_norm
          is_training: 是否可训练
          activation_fn: 激活函数
          scope: 层命名
          reuse: 同名层可被覆盖

        Returns: 正则后的inputs tensor
        """
        inputs_shape = inputs.get_shape()
        inputs_rank = inputs_shape.ndims

        # use fused batch norm if inputs_rank in [2, 3, 4] as it is much faster.
        # pay attention to the fact that fused_batch_norm requires shape to be rank 4 of NHWC.
        if inputs_rank in [2, 3, 4]:
            if inputs_rank == 2:
                inputs = tf.expand_dims(inputs, axis=1)
                inputs = tf.expand_dims(inputs, axis=2)
            elif inputs_rank == 3:
                inputs = tf.expand_dims(inputs, axis=1)
            outputs = tf.contrib.layers.batch_norm(
                inputs=inputs,
                center=True,
                scale=True,
                updates_collections=None,
                is_training=is_training,
                scope=scope,
                fused=True,
                reuse=reuse
            )
            # restore original shape
            if inputs_rank == 2:
                outputs = tf.squeeze(outputs, axis=[1, 2])
            elif inputs_rank == 3:
                outputs = tf.squeeze(outputs, axis=1)
        else:  # fallback to naive batch norm
            outputs = tf.contrib.layers.batch_norm(
                inputs=inputs,
                center=True,
                scale=True,
                updates_collections=None,
                is_training=is_training,
                scope=scope,
                reuse=reuse,
                fused=False
            )
        if activation_fn is not None:
            outputs = activation_fn(outputs)
        return outputs

    def conv1d(self, inputs, filters=None, size=1, rate=1, padding="SAME",
               use_bias=False, activation_fn=None, scope="conv1d", reuse=None):
        """  1D 卷积层

        Args:
          inputs: A 3-D tensor with shape of [batch, time, depth].
          filters: An int. Number of outputs (=activation maps)
          size: An int. Filter size.
          rate: An int. Dilation rate.
          padding: Either `same` or `valid` or `causal` (case-insensitive).
          use_bias: A boolean.
          activation_fn: 激活函数
          scope: 层命名
          reuse: 同名层可被覆盖
        """
        with tf.variable_scope(scope):
            if padding.lower() == "causal":
                # pre-padding for causality
                pad_len = (size - 1) * rate  # padding size
                inputs = tf.pad(inputs, [[0, 0], [pad_len, 0], [0, 0]])
                padding = "valid"
            if filters is None:
                filters = inputs.get_shape().as_list[-1]
            params = {"inputs": inputs, "filters": filters, "kernel_size": size,
                      "dilation_rate": rate, "padding": padding, "activation": activation_fn,
                      "use_bias": use_bias, "reuse": reuse}
            outputs = tf.layers.conv1d(**params)
        return outputs

    def conv1d_banks(self, inputs, k=16, is_training=True, scope="conv1d_banks", reuse=None):
        """Applies a series of conv1d separately.

        Args:
          inputs: A 3d tensor with shape of [N, T, C]
          k: An int. The size of conv1d banks. That is,
            The `inputs` are convolved with K filters: 1, 2, ..., K.
          is_training: A boolean. This is passed to an argument of `bn`.
          scope: 层命名
          reuse: 同名层可被覆盖

        Returns:
          A 3d tensor with shape of [N, T, K*Hp.embed_size//2].
        """
        with tf.variable_scope(scope, reuse=reuse):
            outputs = self.conv1d(inputs, self._hp.embed_size // 2, 1)  # k=1
            for k in range(2, k + 1):  # k = 2...K
                with tf.variable_scope("num_{}".format(k)):
                    output = self.conv1d(inputs, self._hp.embed_size // 2, k)
                    outputs = tf.concat((outputs, output), -1)
            outputs = self.bn(outputs, is_training=is_training, activation_fn=tf.nn.relu)
        return outputs  # (N, T, Hp.embed_size//2*K)

    def gru(self, inputs, num_units=None, bidirection=False, scope="gru", reuse=None):
        """ GRU 层

        Args:
          inputs: A 3d tensor with shape of [N, T, C].
          num_units: An int. The number of hidden units.
          bidirection: A boolean. If True, bidirectional results
            are concatenated.
          scope: 层命名
          reuse: 同名层可被覆盖

        Returns:
          If bidirection is True, a 3d tensor with shape of [N, T, 2*num_units],
            otherwise [N, T, num_units].
        """
        with tf.variable_scope(scope, reuse=reuse):
            if num_units is None:
                num_units = inputs.get_shape().as_list[-1]
            cell = tf.contrib.rnn.GRUCell(num_units)
            if bidirection:
                cell_bw = tf.contrib.rnn.GRUCell(num_units)
                outputs, _ = tf.nn.bidirectional_dynamic_rnn(cell, cell_bw, inputs, dtype=tf.float32)
                return tf.concat(outputs, 2)
            else:
                outputs, _ = tf.nn.dynamic_rnn(cell, inputs, dtype=tf.float32)
                return outputs

    def lstm(self, inputs, keep_prob, num_units=None, bidirection=False, scope="lstm", reuse=None):
        """ LSTM 层

        Args:
          inputs: A 3d tensor with shape of [N, T, C].
          keep_prob: 保留结点比例
          num_units: 隐藏结点数
          bidirection: 是否启用双向 LSTM
          scope: 层命名
          reuse: 同名层可被覆盖

        Returns:
          If bidirection is True, a 3d tensor with shape of [N, T, 2*num_units],
            otherwise [N, T, num_units].
        """
        with tf.variable_scope(scope, reuse=reuse):
            if num_units is None:
                num_units = inputs.get_shape().as_list[-1]
            cell = tf.contrib.rnn.DropoutWrapper(tf.contrib.rnn.LSTMCell(num_units), output_keep_prob=keep_prob)
            if bidirection:
                cell_bw = tf.contrib.rnn.DropoutWrapper(tf.contrib.rnn.LSTMCell(num_units), output_keep_prob=keep_prob)
                outputs, _ = tf.nn.bidirectional_dynamic_rnn(cell, cell_bw, inputs, dtype=tf.float32)
                return tf.concat(outputs, 2)
            else:
                outputs, _ = tf.nn.dynamic_rnn(cell, inputs, dtype=tf.float32)
                return outputs

    def attention_decoder(self, inputs, memory, num_units=None, scope="attention_decoder", reuse=None):
        """ Attention 解码层
        Args:
          inputs: A 3d tensor with shape of [N, T', C']. Decoder inputs.
          memory: A 3d tensor with shape of [N, T, C]. Outputs of encoder network.
          num_units: 隐藏结点数目
          scope: 层命名
          reuse: 同名层可被覆盖

        Returns:
          A 3d tensor with shape of [N, T, num_units].
        """
        with tf.variable_scope(scope, reuse=reuse):
            if num_units is None:
                num_units = inputs.get_shape().as_list[-1]
            attention_mechanism = tf.contrib.seq2seq.BahdanauAttention(num_units, memory)
            decoder_cell = tf.contrib.rnn.GRUCell(num_units)
            cell_with_attention = tf.contrib.seq2seq.AttentionWrapper(decoder_cell, attention_mechanism, num_units,
                                                                      alignment_history=True)
            outputs, state = tf.nn.dynamic_rnn(cell_with_attention, inputs, dtype=tf.float32)  # ( N, T', 16)
        return outputs, state

    def prenet(self, inputs, num_units=None, is_training=True, scope="prenet", reuse=None):
        """  Prenet for Encoder and Decoder1.
        Args:
          inputs: A 2D or 3D tensor.
          num_units: A list of two integers. or None.
          is_training: 是否可训练
          scope: 层命名
          reuse: 同名层可被覆盖

        Returns:
          A 3D tensor of shape [N, T, num_units/2].
        """
        if num_units is None:
            num_units = [self._hp.embed_size, self._hp.embed_size // 2]

        with tf.variable_scope(scope, reuse=reuse):
            outputs = tf.layers.dense(inputs, units=num_units[0], activation=tf.nn.relu, name="dense1")
            outputs = tf.layers.dropout(outputs, rate=self._hp.dropout_rate, training=is_training, name="dropout1")
            outputs = tf.layers.dense(outputs, units=num_units[1], activation=tf.nn.relu, name="dense2")
            outputs = tf.layers.dropout(outputs, rate=self._hp.dropout_rate, training=is_training, name="dropout2")
        return outputs  # (N, ..., num_units[1])

    def highwaynet(self, inputs, num_units=None, scope="highwaynet", reuse=None):
        """  Highway networks,
           see https://arxiv.org/abs/1505.00387

        Args:
          inputs: A 3D tensor of shape [N, T, W].
          num_units: 隐藏结点数目
          scope: 层命名
          reuse: 同名层可被覆盖

        Returns:
          A 3D tensor of shape [N, T, W].
        """
        if not num_units:
            num_units = inputs.get_shape()[-1]

        with tf.variable_scope(scope, reuse=reuse):
            H = tf.layers.dense(inputs, units=num_units, activation=tf.nn.relu, name="dense1")
            T = tf.layers.dense(inputs, units=num_units, activation=tf.nn.sigmoid,
                                bias_initializer=tf.constant_initializer(-1.0), name="dense2")
            outputs = H * T + inputs * (1. - T)
        return outputs

    def mapping_vocab_net(self, inputs, num_units, scope="mapping_vocab_net", reuse=None):
        """ 解码映射词表层
        Args:
          inputs: 二维或者三维的tensor, 这里的输入作为翻译解码后做词表映射, 维度(N, seq_len, hidden_units)
          num_units: 隐藏结点数目，这里设置为映射词表大小
          scope: 层命名
          reuse: 同名层可被覆盖

        Returns:
          A 3D tensor of shape [N, seq_len, vocab_size].
        """
        if num_units is None:
            num_units = [self._hp.embed_size, self._hp.embed_size // 2]
        with tf.variable_scope(scope, reuse=reuse):
            outputs = tf.layers.dense(inputs, units=num_units, activation=None, name="nlp_decoder_logits")
        return outputs  # (N, ..., num_units[1])


class AdvantageLayer(BaseLayer):

    def __init__(self, hp):
        super(AdvantageLayer, self).__init__(hp=hp)
        self._object = "This is advantage layer!"

    def __str__(self):
        return self._object

    def nlp_encoder(self, inputs, keep_prob, is_training=True, scope="nlp_encoder", reuse=None):
        """
        Args:
          inputs: A 2d tensor with shape of [N, T_x, E], with dtype of int32. Encoder inputs.
          keep_prob: 保留结点比例
          is_training: Whether or not the layer is in training mode.
          scope: 层命名
          reuse: Boolean, whether to reuse the weights of a previous layer
            by the same name.

        Returns:
        """
        with tf.variable_scope(scope, reuse=reuse):
            # Bidirectional LSTM
            memory = self.lstm(inputs, keep_prob, num_units=self._hp.embed_size // 2, bidirection=True)  # (N, T_x, E)
        return memory

    def nlp_decoder(self, inputs, memory, is_training=True, scope="nlp_decoder", reuse=None):
        """
        Args:
          inputs: A 3d tensor with shape of [N, T_y/r, n_mels(*r)]. Shifted log melspectrogram of sound files.
          memory: A 3d tensor with shape of [N, T_x, E].
          is_training: Whether or not the layer is in training mode.
          scope: Optional scope for `variable_scope`
          reuse: Boolean, whether to reuse the weights of a previous layer
            by the same name.

        Returns
        """
        with tf.variable_scope(scope, reuse=reuse):
            # Attention RNN
            dec, state = self.attention_decoder(inputs, memory, num_units=self._hp.embed_size)  # (N, T_y/r, E)
            # for attention monitoring
            alignments = tf.transpose(state.alignment_history.stack(), [1, 2, 0])
            # Decoder RNNs with LSTM
            dec += self.lstm(dec, keep_prob=1, num_units=self._hp.embed_size, bidirection=False, scope="decoder_lstm")
            # (N, T_y/r, E)
        return dec, alignments

    def voice_encoder(self, inputs, is_training=True, scope="encoder", reuse=None):
        """
        Args:
          inputs: A 2d tensor with shape of [N, T_x, E], with dtype of int32. Encoder inputs.
          is_training: Whether or not the layer is in training mode.
          scope: 层命名
          reuse: Boolean, whether to reuse the weights of a previous layer
            by the same name.

        Returns:
          A collection of Hidden vectors. So-called memory. Has the shape of (N, T_x, E).
        """
        with tf.variable_scope(scope, reuse=reuse):
            # Encoder pre-net
            prenet_out = self.prenet(inputs, is_training=is_training)  # (N, T_x, E/2)
            # Encoder CBHG
            # Conv1D banks
            enc = self.conv1d_banks(prenet_out, k=self._hp.encoder_num_banks, is_training=is_training)  # (N, T_x, K*E/2)
            # Max pooling
            enc = tf.layers.max_pooling1d(enc, pool_size=2, strides=1, padding="same")  # (N, T_x, K*E/2)
            # Conv1D projections
            enc = self.conv1d(enc, filters=self._hp.embed_size // 2, size=3, scope="conv1d_1")  # (N, T_x, E/2)
            enc = self.bn(enc, is_training=is_training, activation_fn=tf.nn.relu, scope="conv1d_1")
            enc = self.conv1d(enc, filters=self._hp.embed_size // 2, size=3, scope="conv1d_2")  # (N, T_x, E/2)
            enc = self.bn(enc, is_training=is_training, scope="conv1d_2")
            enc += prenet_out  # (N, T_x, E/2) # residual connections
            # Highway Nets
            for i in range(self._hp.num_highwaynet_blocks):
                enc = self.highwaynet(enc, num_units=self._hp.embed_size // 2,
                                 scope='highwaynet_{}'.format(i))  # (N, T_x, E/2)
            # Bidirectional GRU
            memory = self.gru(enc, num_units=self._hp.embed_size // 2, bidirection=True)  # (N, T_x, E)
        return memory

    def voice_decoder_1(self, inputs, memory, is_training=True, scope="decoder1", reuse=None):
        """
        Args:
          inputs: A 3d tensor with shape of [N, T_y/r, n_mels(*r)]. Shifted log melspectrogram of sound files.
          memory: A 3d tensor with shape of [N, T_x, E].
          is_training: Whether or not the layer is in training mode.
          scope: 层命名
          reuse: Boolean, whether to reuse the weights of a previous layer
            by the same name.

        Returns
          Predicted log melspectrogram tensor with shape of [N, T_y/r, n_mels*r].
        """
        with tf.variable_scope(scope, reuse=reuse):
            # Decoder pre-net
            inputs = self.prenet(inputs, is_training=is_training)  # (N, T_y/r, E/2)
            # Attention RNN
            dec, state = self.attention_decoder(inputs, memory, num_units=self._hp.embed_size)  # (N, T_y/r, E)
            # for attention monitoring
            alignments = tf.transpose(state.alignment_history.stack(), [1, 2, 0])
            # Decoder RNNs
            dec += self.gru(dec, self._hp.embed_size, bidirection=False, scope="decoder_gru1")  # (N, T_y/r, E)
            dec += self.gru(dec, self._hp.embed_size, bidirection=False, scope="decoder_gru2")  # (N, T_y/r, E)
            # Outputs => (N, T_y/r, n_mels*r)
            mel_hats = tf.layers.dense(dec, self._hp.n_mels * self._hp.r)
        return mel_hats, alignments

    def voice_decoder_2(self, inputs, is_training=True, scope="decoder2", reuse=None):
        """Decoder Post-processing net = CBHG
        Args:
          inputs: A 3d tensor with shape of [N, T_y/r, n_mels*r]. Log magnitude spectrogram of sound files.
            It is recovered to its original shape.
          is_training: 是否可训练
          scope: 层命名
          reuse: 同名层可被覆盖

        Returns
          Predicted linear spectrogram tensor with shape of [N, T_y, 1+n_fft//2].
        """
        with tf.variable_scope(scope, reuse=reuse):
            # Restore shape -> (N, Ty, n_mels)
            inputs = tf.reshape(inputs, [tf.shape(inputs)[0], -1, self._hp.n_mels])
            # Conv1D bank
            dec = self.conv1d_banks(inputs, k=self._hp.decoder_num_banks, is_training=is_training)  # (N, T_y, E*K/2)
            # Max pooling
            dec = tf.layers.max_pooling1d(dec, pool_size=2, strides=1, padding="same")  # (N, T_y, E*K/2)
            # Conv1D projections
            dec = self.conv1d(dec, filters=self._hp.embed_size // 2, size=3, scope="conv1d_1")  # (N, T_x, E/2)
            dec = self.bn(dec, is_training=is_training, activation_fn=tf.nn.relu, scope="conv1d_1")
            dec = self.conv1d(dec, filters=self._hp.n_mels, size=3, scope="conv1d_2")  # (N, T_x, E/2)
            dec = self.bn(dec, is_training=is_training, scope="conv1d_2")
            # Extra affine transformation for dimensionality sync
            dec = tf.layers.dense(dec, self._hp.embed_size // 2)  # (N, T_y, E/2)
            # Highway Nets
            for i in range(4):
                dec = self.highwaynet(dec, num_units=self._hp.embed_size // 2, scope='highwaynet_{}'.format(i))
                # (N, T_y, E/2)
            # Bidirectional GRU
            dec = self.gru(dec, self._hp.embed_size // 2, bidirection=True)  # (N, T_y, E)
            # Outputs => (N, T_y, 1+n_fft//2)
            outputs = tf.layers.dense(dec, 1 + self._hp.n_fft // 2)
        return outputs
