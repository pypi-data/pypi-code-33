import string, random

def generate(size:int):
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(size))

def generate_letters(size:int):
    return ''.join(random.SystemRandom().choice(string.ascii_letters) for _ in range(size))

def generate_email(size:int,hostSize:int=None):
    return '{}@{}.{}'.format(generate(size), generate(hostSize), generate_letters(3))

def generate_number(size:int):
    return ''.join(random.SystemRandom().choice(string.digits) for _ in range(size))