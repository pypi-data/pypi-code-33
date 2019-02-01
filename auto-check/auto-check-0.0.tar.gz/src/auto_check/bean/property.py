class Property:
    properties = {}

    def __init__(self, file_path):
        try:
            config = open(file_path, 'r')
            for line in config:
                if line.find('=') > 0:
                    strs = line.replace('\n', '').split('=')
                    key, value = strs[0], strs[1]
                    self.properties[key] = value
                else:
                    raise Exception('config file format error')
        except Exception as e:
            print('配置文件读取出现问题')
            raise e
        else:
            config.close()
        #print(self.properties)

    def get_property(self, key):
        return self.properties[key]
