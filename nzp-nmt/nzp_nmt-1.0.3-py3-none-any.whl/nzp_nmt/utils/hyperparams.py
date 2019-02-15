# -*- coding: utf-8 -*-
"""
默认参数类
"""


class HyperParams(object):

    # device
    gpu = '0'

    # vocab dictionary
    vocab = "PE abcdefghijklmnopqrstuvwxyz'.?"  # P: 填充符号 E: 结束符号 注: 音频以字符级作为文本输入
    chinese_vocab = "dictionary/chinese2no.txt"
    english_vocab = "dictionary/english2no.txt"

    # data
    text_data = "data/text/"
    train_data_file = "tc.txt"
    voice_data = "data/voice/"
    test_data = 'harvard_sentences.txt'
    max_duration = 10.0

    # signal processing
    sr = 22050  # Sample rate.
    n_fft = 2048  # fft points (samples)
    frame_shift = 0.0125  # seconds
    frame_length = 0.05  # seconds
    hop_length = int(sr*frame_shift)  # samples.
    win_length = int(sr*frame_length)  # samples.
    n_mels = 80  # Number of Mel banks to generate
    power = 1.2  # Exponent for amplifying the predicted magnitude
    n_iter = 50  # Number of inversion iterations
    preemphasis = .97  # or None
    max_db = 100
    ref_db = 20

    # nmt model
    chinese_embed_size = 128
    english_embed_size = 128

    # tts model
    embed_size = 256  # alias = E
    encoder_num_banks = 16
    decoder_num_banks = 8
    num_highwaynet_blocks = 4
    r = 5  # Reduction factor. Paper => 2, 3, 5
    dropout_rate = .5

    # training scheme
    lr = 0.001  # Initial learning rate.
    train_num_steps = 1000
    model_dir = "model/"
    model_version = "000001/"
    sample_dir = 'samples/'
    batch_size = 32
    keep_prob = 0.75
    train_type = "nmt2tts"
    predict_type = "nmt2tts"
    gs = 1000
