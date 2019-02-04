# encoding: utf-8
"""
@author: BrikerMan
@contact: eliyar917@gmail.com
@blog: https://eliyar.biz

@version: 1.0
@license: Apache Licence
@file: blstm_attention_model
@time: 2019-01-31

"""
import logging

from keras.layers import Bidirectional, LSTM, Embedding, Input
from keras.layers import Dense, Dropout, TimeDistributed, Activation
from keras.models import Model

from kashgari.tasks.seq_labeling.base_model import SequenceLabelingModel
from kashgari.utils.custom_layers import AttentionDecoder


class BLSTMAttentionModel(SequenceLabelingModel):
    __architect_name__ = 'BLSTMAttentionModel'
    __base_hyper_parameters__ = {}

    def build_model(self, loss_f=None, optimizer=None, metrics=None, **kwargs):
        encoder_input = self.embedding.model.output
        decoder_input = Input(shape=(self.embedding.sequence_length,))

        # encoder = Embedding(input_dict_size, 64, input_length=INPUT_LENGTH, mask_zero=True)(encoder_input)
        encoder = LSTM(64, return_sequences=True, unroll=True)(encoder_input)
        encoder_last = encoder[:, -1, :]

        print('encoder', encoder)
        print('encoder_last', encoder_last)

        decoder = Embedding(len(self.label2idx), 64, input_length=self.embedding.sequence_length, mask_zero=True)(decoder_input)
        decoder = LSTM(64, return_sequences=True, unroll=True)(decoder, initial_state=[encoder_last, encoder_last])
        from keras.layers import Activation, dot, concatenate

        # Equation (7) with 'dot' score from Section 3.1 in the paper.
        # Note that we reuse Softmax-activation layer instead of writing tensor calculation
        attention = dot([decoder, encoder], axes=[2, 2])
        attention = Activation('softmax', name='attention')(attention)
        print('attention', attention)

        context = dot([attention, encoder], axes=[2, 1])
        print('context', context)

        decoder_combined_context = concatenate([context, decoder])
        print('decoder_combined_context', decoder_combined_context)

        # Has another weight + tanh layer as described in equation (5) of the paper
        output = TimeDistributed(Dense(64, activation="tanh"))(decoder_combined_context)
        output = TimeDistributed(Dense(len(self.label2idx), activation="softmax"))(output)
        print('output', output)

        model = Model(inputs=[encoder_input, decoder_input], outputs=[output])
        model.compile(optimizer='adam', loss='categorical_crossentropy')
        self.model = model
        self.model.summary()

    # def build_model(self, loss_f=None, optimizer=None, metrics=None, **kwargs):
    #     """
    #     build model function
    #     :return:
    #     """
    #     if not loss_f:
    #         loss_f = 'categorical_crossentropy'
    #     if not optimizer:
    #         optimizer = 'adam'
    #     if not metrics:
    #         metrics = ['accuracy']
    #     embed_model = self.embedding.model
    #     encoder = Bidirectional(LSTM(64, return_sequences=True))(embed_model.output)
    #
    #     decoder = AttentionDecoder(32, output_dim=len(self.label2idx),
    #                                return_probabilities=True,
    #                                return_sequences=False)(encoder)
    #
    #     decoder = AttentionDecoder(32, output_dim=len(self.label2idx),
    #                                return_probabilities=True,
    #                                return_sequences=False)(encoder)
    #     time_distributed_layer = TimeDistributed(Dense(len(self.label2idx)))(decoder)
    #     activation = Activation('softmax')(time_distributed_layer)
    #
    #     model = Model(embed_model.inputs, activation)
    #     model.compile(loss=loss_f,
    #                   optimizer=optimizer,
    #                   metrics=metrics)
    #     self.model = model
    #     self.model.summary()


if __name__ == '__main__':
    import random
    from keras.callbacks import ModelCheckpoint
    from kashgari.utils.logger import init_logger
    from kashgari.corpus import ChinaPeoplesDailyNerCorpus

    init_logger()
    x_train, y_train = ChinaPeoplesDailyNerCorpus.get_sequence_tagging_data()
    x_validate, y_validate = ChinaPeoplesDailyNerCorpus.get_sequence_tagging_data(data_type='validate')
    x_test, y_test = ChinaPeoplesDailyNerCorpus.get_sequence_tagging_data(data_type='test')

    # embedding = WordEmbeddings('sgns.weibo.bigram', sequence_length=100)
    m = BLSTMAttentionModel()

    check = ModelCheckpoint('./model.model',
                            monitor='acc',
                            verbose=1,
                            save_best_only=False,
                            save_weights_only=False,
                            mode='auto',
                            period=1)
    m.fit(x_train[:1000],
          y_train[:1000],
          class_weight=True,
          epochs=1,
          y_validate=y_validate,
          x_validate=x_validate,
          labels_weight=False)

    sample_queries = random.sample(list(range(len(x_train))), 10)
    for i in sample_queries:
        text = x_train[i]
        logging.info('-------- sample {} --------'.format(i))
        logging.info('x: {}'.format(text))
        logging.info('y_true: {}'.format(y_train[i]))
        logging.info('y_pred: {}'.format(m.predict(text)))
    logging.info(m.predict(list('总统特朗普今天在美国会见了朝鲜领导金正恩'), debug_info=True))
    m.evaluate(x_test, y_test, debug_info=True)
