from bson.objectid import ObjectId


class Find(object):
    def __init__(self, collection, query, klass):
        self.collection = collection
        self.query = query
        self.klass = klass
        self._sort = None
        self._skip = None
        self._limit = None

    def count(self):
        return self.collection.find(self.query).count()

    def filter(self, **kwargs):
        self.query.update(kwargs)
        return self

    def filter_raw(self, key, value):
        self.query.update({key: value})
        return self

    def sort(self, *args):
        self._sort = args
        return self

    def skip(self, skip):
        self._skip = skip
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def __iter__(self):
        q = self.collection.find(self.query)
        if self._sort is not None:
            sortq = []
            for item in self._sort:
                if item[0] == '-':
                    sortq.append((item[1:], -1))
                else:
                    sortq.append((item, 1))
            q = q.sort(sortq)

        if self._skip is not None:
            q = q.skip(self._skip)

        if self._limit is not None:
            q = q.limit(self._limit)

        return iter(map(lambda x: self.klass(**x), q))


class DocumentManager(object):
    def __init__(self, document_class):
        self.klass = document_class

    def all(self):
        return self.find()

    def insert(self, data):
        _id = self.klass.__collection__.insert_one(data).inserted_id
        data['_id'] = _id

    def update(self, data):
        ndata = {}
        ndata.update(data)
        _id = ndata.pop('_id')
        self.klass.__collection__.replace_one(dict(_id=_id), ndata)

    def delete(self, _id):
        self.klass.__collection__.delete_one(dict(_id=_id))

    def clear(self):
        self.klass.__collection__.remove()

    def find_one(self, **kwargs):
        if '_id' in kwargs:
            kwargs['_id'] = ObjectId(kwargs['_id'])

        res = self.klass.__collection__.find_one(kwargs)
        if res:
            return self.klass(**res)

        return None

    def find(self, **kwargs):
        if '_id' in kwargs:
            kwargs['_id'] = ObjectId(kwargs['_id'])

        return Find(
            self.klass.__collection__,
            kwargs,
            self.klass
        )

    def find_raw(self, *args, **kwargs):
        return self.klass.__collection__.find(*args, **kwargs)

    def migrate(self, migrations):
        for item in self.find():
            if item._data['__ver'] != self.klass.__version__:
                meth = migrations.get(
                    (item._data['__ver'], self.klass.__version__))
                if meth:
                    meth(item)
