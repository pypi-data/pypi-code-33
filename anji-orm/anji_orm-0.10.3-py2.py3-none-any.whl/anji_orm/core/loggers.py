import logging

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.10.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ["abstraction_ignore_log", "abstraction_emulation_log"]

abstraction_ignore_log = logging.getLogger("anji_orm.abstraction.ignore")
abstraction_emulation_log = logging.getLogger("anji_orm.abstraction.emulation")
