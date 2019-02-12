from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature, BadData
from functools import wraps
from flask import request, g
import rsa
import base64

from exceptions import std_res

class payloadIllegalError(Exception):
    def __init__(self, err="illegal payload inside. Secrete key may have been disclosed!"):
        Exception.__init__(self, err)

def token_verify(token, secret_key, salt=None):
    # token decoding
    s = Serializer(
        secret_key=secret_key,
        salt=salt
    )
    try:
        data = s.loads(token)
    # 触发SignatureExpired token过期
    except BadSignature as e:
        encoded_payload = e.payload
        if encoded_payload:
            s.load_payload(encoded_payload) # 触发BadData token被篡改
        raise BadSignature # payload不完整
    if 'id' not in data \
            or 'permission' not in data:
        raise payloadIllegalError
    return data

def generate_key(pubkey_file, privkey_file):
    """
    生成密钥对
    :return: (公钥对象, 私钥对象)
    """
    # 生成密钥
    pubkey, privkey = rsa.newkeys(1024)
    # 保存密钥
    with open(pubkey_file,'w+') as f:
        f.write(pubkey.save_pkcs1().decode())

    with open(privkey_file,'w+') as f:
        f.write(privkey.save_pkcs1().decode())

    return pubkey, privkey

def signature(msg, privkey):
    """
    签名生成
    :param msg: 签名内容
    :param privkey: 私钥字符串
    :return: 签名字符串
    """
    privkey = rsa.PrivateKey.load_pkcs1(privkey)
    return rsa.sign(msg.encode(), privkey, 'SHA-1')

def verify(msg, sign, pubkey, decode_base64=False):
    """
    签名验证

    request中传递sign是经过base64编码的，使用decode_base64选项解码
    :return:
    """
    if decode_base64:
        sign = base64.b64decode(sign.encode())
    if isinstance(sign, str):
        sign = bytes(sign, encoding='utf-8')
    try:
        rsa.verify(msg, sign, rsa.PublicKey.load_pkcs1(pubkey))
        return True
    except rsa.pkcs1.VerificationError:
        return False

def JWT_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        Authorization = request.headers['Authorization'].split(' ')
        if Authorization[0] is not 'JWT':
            return std_res('400', 'JWT is required')
        sign = request.args.get('signature')
        if sign is None:
            return std_res('400', 'Server signature is required')
        try:
            token_payload = token_verify(Authorization[1], sign, sign[:4])
            g.payload = token_payload
        except:
            return std_res('403', 'JWT illegal')
        return f(*args, **kwargs)
    return wrapper