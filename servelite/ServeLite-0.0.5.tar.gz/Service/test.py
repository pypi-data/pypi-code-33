from service import Service
from models import Base

from sqlalchemy import Column, Integer, String, ForeignKey
import json

class test(Base):
    __tablename__ = 'test'
    __table_args__ = ({'comment': '{"sensitivity": 6, "description": "test"}'})

    id = Column(Integer, ForeignKey('tables.id'), primary_key=True, autoincrement=True, comment='{"sensitivity": 6, "description": "test"}')
    t = Column(String(64))

def test_():
    s = Service()
    for table in s.Base.metadata.sorted_tables:
        print([i.name for i in table.primary_key.columns_autoinc_first])
        for c in table.columns._all_columns:
            info = json.loads(c.comment if c.comment else '{}')
            print(info.get('sensitivity'))

def error_test():
    from exceptions import WrongTypeInfoComment
    raise WrongTypeInfoComment('table', 'col')

class decorator_test:
    def __init__(self):
        self.test()
        self.wrapped_func()

    def wrapper(self, func):
        def wrapped(*args, **kwargs):
            print('wrapped')
            return func(*args, **kwargs)
        return wrapped

    def test(self):
        @self.wrapper
        def wrapped_func():
            print('wrapped_func')
        self.__setattr__('wrapped_func', wrapped_func)

from flask import Flask, url_for

app = Flask(__name__)

def test_add(info1, info2):
    def decorator(f):
        for endpoint in app.view_functions:
            if app.view_functions[endpoint] is f:
                app.config['SERVER_NAME'] = ''
                with app.app_context():
                    print(url_for(endpoint))
        return f
    return decorator

@test_add('1', '2')
@app.route('/', endpoint='test_end')
def test_f():
    pass

def test_server():
    # app = Flask(__name__)
    app.run()
    a = 1

import threading
class thread_test:
    class thread(threading.Thread):
        def __init__(self, flask_app):
            self.var = 'thread'
            self.flask_app = flask_app
            threading.Thread.__init__(self)
        def run(self):
            self.flask_app.run()

    def __init__(self):
        self.var = 'test'
        self.test_app = Flask(__name__)
        self.test_app.add_url_rule('/', view_func=self.test)
        th = self.thread(self.test_app)
        th.start()

    def test(self):
        from flask import jsonify
        print(self.var)
        return jsonify({})

def multi_update():
    pos = '1.2'.split('.')
    data = 'test'

    info = {
        '1': {
            '2': 2,
            '3': 3,
        }
    }
    temp = data
    for i in range(1, len(pos)):
        temp = {pos[-i]: temp}

    info[pos[0]] = {**info[pos[0]], **temp}
    print(info)

if __name__ == '__main__':
    # error_test()
    # test_()
    # decorator_test()
    # test_server()
    # from models import APIs
    # api = APIs()
    # print(api.info())
    # t = thread_test()
    multi_update()