import os
import logging
import logging.handlers


class Logger:
    _shared_state = {}

    def __new__(cls) -> 'Logger':
        """
        This class uses the borg pattern. See: http://design-patterns-ebook.readthedocs.io/en/latest/creational/borg/.
        :return: a shared instance from the borg.
        """
        inst = super().__new__(cls)  # Uses the super class implementation of __new__() to create an instance.
        inst.__dict__ = cls._shared_state  # Assigns the shared state to the instance.
        if not cls._shared_state:
            # We create the instance once, when the shared state is empty.
            inst.app_logger = None

        return inst

    def __getattr__(self, item):
        if self.app_logger is not None:
            return getattr(self.app_logger, item)
        else:
            raise AttributeError()

    def setup_app_logger(self, log_dir: str, level, name='app', max_bytes=20 * 1024 * 1024, backups=1):
        self.app_logger = logging.getLogger(name)
        self.app_logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Console handler:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        self.app_logger.addHandler(ch)

        # File handler:
        os.makedirs(log_dir, exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(os.path.join(log_dir, '{}.log'.format(name)), maxBytes=max_bytes,
                                                  backupCount=backups, encoding='utf-8')
        fh.setLevel(level)
        fh.setFormatter(formatter)
        self.app_logger.addHandler(fh)

    def setup_flask_logger(self, log_dir: str, level, max_bytes=20 * 1024 * 1024, backups=1):
        os.makedirs(log_dir, exist_ok=True)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler = logging.handlers.RotatingFileHandler(os.path.join(log_dir, 'requests.log'), maxBytes=max_bytes,
                                                       backupCount=backups, encoding='utf-8')
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logging.getLogger('werkzeug').addHandler(handler)
