

def read_to_str(path: str, encoding='utf-8'):
    with open(path, 'r', encoding=encoding) as file:
        return file.read()

