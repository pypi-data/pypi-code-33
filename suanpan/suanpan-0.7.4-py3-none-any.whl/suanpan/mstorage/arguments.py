# coding=utf-8
from __future__ import print_function

from suanpan.arguments import Arg
from suanpan.mstorage import mstorage
from suanpan.utils import json, npy, pickle


class Pickle(Arg):
    def load(self, args):
        self.value = super(Pickle, self).load(args)
        return self.value

    def format(self, context):
        if self.value:
            self.value = pickle.loads(mstorage.get(self.value))
        return self.value

    def save(self, context, result):
        obj = result.value
        mstorage.set(self.value, pickle.dumps(obj))
        return self.value


class Any(Pickle):
    pass


class Npy(Arg):
    def load(self, args):
        self.value = super(Npy, self).load(args)
        return self.value

    def format(self, context):
        if self.value:
            self.value = self.getnpy()
        return self.value

    def save(self, context, result):
        obj = result.value
        self.setnpy(obj)
        return self.value

    def setnpy(self, obj):
        params = npy.dumps(obj)
        npybytes = params.pop("data")
        data = {"md": json.dumps(params), "data": npybytes}
        return mstorage.mset(self.value, data)

    def getnpy(self):
        data = npy.loads(mstorage.mget(self.value))
        params = json.loads(data["md"])
        params["data"] = data["data"]
        return npy.loads(params)
