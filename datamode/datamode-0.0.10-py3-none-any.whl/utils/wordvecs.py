
from datamode.settings import DEFAULT_CONFIG_DIR

from .singleton import Singleton
from .yamlutils import load_yaml

# For FastText, Download the data from:
# https://fasttext.cc/docs/en/pretrained-vectors.html

from datamode.utils.utils import get_logger
log = get_logger(__name__)


RED = 31
RED_SEQ = f'\033[1;{RED}m'
RESET_SEQ = "\033[0m"

# Note:
# We can't use the gensim fasttext loader until this bug is fixed - https://github.com/RaRe-Technologies/gensim/issues/1261
# The official fastText python bindings are likely to be faster/more updated anyway.
@Singleton
class WordVecLoader():
  def __init__(self):
    self.ft_model = None

  def get_ft_model(self):
    path = self.get_config_path('fasttext')

    if self.ft_model is None:
      self.load_ft_model(path)
    else:
      log.info(f'WordVecLoader: Loaded model {path} from cache.')

    return self.ft_model

  def load_ft_model(self, path):
    try:
      import fastText
    except ImportError:
      raise Exception('fastText has not been installed. Please see the docs for how to enable it.')

    log.info(f'{RED_SEQ}WordVecLoader: Loading {path} into memory. Please be patient - this process can take 30s+ or more, depending on your hardware and available memory.{RESET_SEQ}')
    self.ft_model = fastText.load_model(path)
    return path

  def get_config_path(self, requested_name):
    yaml_filepath, yaml_config = load_yaml(DEFAULT_CONFIG_DIR)
    if yaml_config:
      word_vectors = yaml_config.get('word_vectors')
      if word_vectors:
        for name, config in word_vectors.items():
          if name == requested_name:
            return config.get('path')

    raise Exception('Please define the section word_vectors in your datamode.yml.')
