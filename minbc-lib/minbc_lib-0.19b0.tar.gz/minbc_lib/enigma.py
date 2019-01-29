#coding: utf-8
# エニグマ暗号の暗号化，復号化

from pyenigma import enigma
from pyenigma import rotor

engine = None

def reset(key, plugs="AV BS CG"):
    """
    エニグマ暗号機をリセットする
    """
    global engine
    engine = enigma.Enigma(
        rotor.ROTOR_Reflector_A,
        rotor.ROTOR_I, rotor.ROTOR_II, rotor.ROTOR_III,
        key=key, plugs=plugs)


def encrypt_enigma(plaintext):
    """
    エニグマ暗号をかける
    """
    if not engine:
        raise Exception("reset()してから暗号化してください。")

    return engine.encipher(plaintext)