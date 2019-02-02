#! TODO this was copied from lablackey.db.models, but much was deleted
# Named model, slug model, ordered model, tree model...
# review and decide which to keep

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField

from unrest.managers import RequestManager, UserRequestManager
import json

def as_json(self):
  out = { f: getattr(self,f) for f in self.json_fields }
  out.update(**out.pop("data",{}))
  for f in self.fk_json_fields:
    if getattr(self,f):
      out[f] = getattr(self,f).as_json
  for f in self.m2m_json_fields:
    out[f] = [i.as_json for i in getattr(self,f)]
  return out

class JsonMixin(object):
  json_fields = []
  filter_fields = []
  m2m_json_fields = []
  fk_json_fields = []
  as_json = property(as_json)

_hash = lambda data: hash(json.dumps(data,sort_keys=True))

class JsonModel(models.Model,JsonMixin):
  created = models.DateTimeField(auto_now_add=True)
  data_hash = models.BigIntegerField()
  data = JSONField(default=dict)
  objects = RequestManager()

  def save(self,*args,**kwargs):
    self.data_hash = _hash(self.data)
    super().save(*args,**kwargs)

  @classmethod
  def from_data(cls,data,request=None,**kwargs):
    data_hash = _hash(data)
    instance = cls.objects.filter(data=data).first()
    return instance or cls.objects.create(
      data=data,
      data_hash=data_hash,
      **kwargs
    )

  class Meta:
    abstract = True

class UserModel(JsonModel):
  user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
  objects = UserRequestManager()
  class Meta:
    abstract = True

  @classmethod
  def from_data(cls,data,request=None,**kwargs):
    kwargs['user'] = request.user
    return super().from_data(data,request=None,**kwargs)