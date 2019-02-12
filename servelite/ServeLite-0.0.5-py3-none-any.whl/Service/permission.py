from flask_restless import ProcessingException
from flask import request, g

from auth import token_verify

def token_check(*args, **kwargs):
    """
    jwt token校验
    该方法会在接受请求时首先执行,并将拥有权限的字段通过g传递下去
    """
    from models import get_session, Tables, Fields

    authorization = request.headers.get('Authorization')
    if authorization.split(' ')[0] is not   'JWT':
        raise ProcessingException('JWT is required')
    token = authorization.split(' ')[-1]
    sign = request.values.get('signature')
    if not sign:
        raise ProcessingException('signature is required')
    try:
        data = token_verify(token, sign, sign[:4])
    except Exception as e:
        raise ProcessingException(str(e))

    session = get_session()
    g.available_fields = []
    table = request.path.split('/')[2] # 这是使用/query作为prefix的情况
    table = session.query(Tables).filter_by(name=table).first() #type: Tables
    # 验证表最低权限
    if table.sensitivity > data['permission']:
        raise ProcessingException('no permission')
    # 验证字段权限
    for filed in table.fields:
        if filed.sensitivity < data['permission']:
            g.available_fields.append(filed.name)


def handel_res(result=None, **kw):
    """
    隐藏结果中的高敏感数据
    作用于：GET GET_MANY
    """
    if result is None:
        return
    for item in result:
        if item not in g.available_fields:
            result[item] = '<no permission>'

