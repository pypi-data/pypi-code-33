# FLASK_APP=d6tpipe/utils/flaskapi.py FLASK_DEBUG=1 flask run

cfg_token = None#'securetoken' # None to disable
from tinydb import TinyDB
from d6tpipe.utils import TinydbREST

import logging
import os
try:
    from flask import Flask
except:
    raise ModuleNotFoundError("Flask not found. Run `pip install flask`")
from flask import request, jsonify, Blueprint
from flask import current_app

cfg_db = os.environ.get('D6TFLASKDB','_db.json')
cfg_token = os.environ.get('D6TFLASKTOKEN')

flaskapi = Blueprint('simple_page', __name__)
@flaskapi.route('/')
def rte_root():
    return jsonify({"description":"d6tpipe API"})

@flaskapi.route('/wipeall', methods=['POST'])
def rte_wipeall():
    tdb = TinyDB(cfg_db)
    tdb.purge_tables()
    return jsonify({'status':'wiped','db':tdb.all()})

@flaskapi.route('/<path:path>', methods=['GET', 'POST','PUT','PATCH','DELETE'])
def rte_path(path):
    current_app.logger.info(path)
    if cfg_token is not None:
        if not request.headers.get('Authorization')=='Token {}'.format(cfg_token):
            return jsonify({'status':'unauthorized'}), 401
    method = request.method.lower()
    path = list(filter(None, path.split('/')))
    isdetail = len(path)>1
    try:
        if isdetail:
            if len(path)>2:
                tbl = '-'.join([path[0]]+path[2:])
            else:
                tbl = path[0]
            fun = TinydbREST(cfg_db, tbl, path[1]).__getattribute__(method)
        else:
            fun = TinydbREST(cfg_db, path[0]).__getattribute__(method)

        if method in ['post','patch','put']:
            r = fun(request_body=request.json)
        else:
            r = fun()

        if isdetail and r==[]:
            status = 404
        elif not isdetail and method=='post':
            status = 201
        else:
            status = 200
    except Exception as e:
        return jsonify({'status':'error', 'message':str(e)}), 500

    return jsonify(r[1]), status
