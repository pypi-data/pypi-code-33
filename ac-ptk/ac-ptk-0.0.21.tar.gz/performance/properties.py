import re
import os
import tempfile


class Properties:

    def __init__(self, file_name=None):
        self.file_name = file_name
        self.properties = {}
        if self.file_name is None:
            return
        try:
            fopen = open(self.file_name, 'r')
            for line in fopen:
                line = line.strip()
                if line.find('=') > 0 and not line.startswith('#'):
                    strs = line.split('=')
                    self.properties[strs[0].strip()] = strs[1].strip()
        except Exception as e:
            raise e
        else:
            fopen.close()

    def has_key(self, key):
        return key in self.properties

    def get(self, key, default_value=''):
        if key in self.properties:
            return self.properties[key]
        return default_value

    def get_bool(self, key, default_value=True):
        v = default_value
        try:
            value = self.get(key).strip()
            if value is None or value == '' or value == '0' or 'false' == value.lower():
                v = False
        finally:
            return v

    def get_int(self, key, default_value=0):
        value = default_value
        try:
            value = int(self.get(key))
        finally:
            return value

    def get_float(self, key, default=0.0):
        value = default
        try:
            value = float(self.get(key))
        finally:
            return value

    def get_arr(self, key):
        value = self.get(key, '').strip()
        assert isinstance(value, str)
        value = value.replace('[', '').replace(']', '')
        arr = value.split(',')
        for i in range(len(arr)):
            arr[i] = arr[i].strip()
        return arr

    def put(self, key, value):
        self.properties[key] = value
        replace_property(self.file_name, key + '=.*', key + '=' + value, True)


def parse(file_name):
    if not os.path.exists(file_name):
        return Properties()
    return Properties(file_name)


def replace_property(file_name, from_regex, to_str, append_on_not_exists=True):
    tmpfile = tempfile.TemporaryFile()

    if os.path.exists(file_name):
        r_open = open(file_name, 'r')
        pattern = re.compile(r'' + from_regex)
        found = None
        for line in r_open:
            if pattern.search(line) and not line.strip().startswith('#'):
                found = True
                line = re.sub(from_regex, to_str, line)
            tmpfile.write(line)
        if not found and append_on_not_exists:
            tmpfile.write('\n' + to_str)
        r_open.close()
        tmpfile.seek(0)

        content = tmpfile.read()

        if os.path.exists(file_name):
            os.remove(file_name)

        w_open = open(file_name, 'w')
        w_open.write(content)
        w_open.close()

        tmpfile.close()
    else:
        print("file %s not found" % file_name)
