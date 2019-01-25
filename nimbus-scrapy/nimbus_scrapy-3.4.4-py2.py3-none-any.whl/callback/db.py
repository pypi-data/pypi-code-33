# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
import traceback
import logging
from scrapy.exceptions import DropItem
from .item import SpiderItemCallback
from ..models import BaseModel


class SpiderDBItemCallback(SpiderItemCallback):
    _db_session = None
    models_mapping = {
    }

    def init_db_session(self, item=None, spider=None):
        raise NotImplementedError

    def get_model_cls(self, item=None, spider=None):
        raise NotImplementedError

    def get_model_kwargs(self, item=None, spider=None):
        raise NotImplementedError

    def process_item_model(self, item=None, spider=None):
        model_cls = self.get_model_cls(item, spider)
        model_kwargs = self.get_model_kwargs(item, spider) or {}
        model = model_cls.save(item, **model_kwargs) if model_cls and issubclass(model_cls, BaseModel) else None
        if model is None:
            raise DropItem("db model is none, item -> {}".format(item))
        return model

    def process_item(self, item, spider=None, *args, **kwargs):
        db = self.get_db_session(item, spider)
        if not db:
            raise DropItem("db session is none, item -> {}".format(item))
        model = self.process_item_model(item, spider)
        try:
            db.add(model)
            db.commit()
        except Exception as e:
            db.rollback()
            error = traceback.format_exc()
            spider.log(error, level=logging.ERROR)
            raise DropItem("db commit error, item -> {}".format(item))
        return item

    def get_db_session(self, item=None, spider=None):
        if self._db_session:
            return self._db_session
        self._db_session = self.init_db_session(item=item, spider=spider)
        return self._db_session



