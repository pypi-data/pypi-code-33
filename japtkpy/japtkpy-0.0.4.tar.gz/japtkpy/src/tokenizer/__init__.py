from rakutenma import RakutenMA


class Tokenizer:
    __instance = None
    __FILE_PATH_MODEL = '../../res/model_ja.min.json'

    def __init__(self):
        self.__rma = RakutenMA()
        self.__load_model()
        pass

    def tokenize(self, sentence):
        return [w for w, t in self.__rma.tokenize(sentence)]

    def __load_model(self):
        self.__rma.load(self.__FILE_PATH_MODEL)

    @classmethod
    def initialize(cls):
        if cls.__instance is None:
            cls.__instance = Tokenizer()
        return cls.__instance
