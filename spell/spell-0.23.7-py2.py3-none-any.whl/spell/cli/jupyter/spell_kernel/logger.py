import logging


class SpellKernelLogger(logging.Logger):
    FMT = "\033[94m[%(levelname)1.1s %(asctime)s.%(msecs).03d %(name)s]\033[m %(message)s"
    DATEFMT = "%H:%M:%S"

    def __init__(self, name, level=logging.NOTSET):
        super(SpellKernelLogger, self).__init__(name, level)

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt=self.FMT, datefmt=self.DATEFMT))
        self.addHandler(handler)
