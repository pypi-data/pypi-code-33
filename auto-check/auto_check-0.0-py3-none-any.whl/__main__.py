import threading
import os

from .checker.auto_checker import AutoChecker
from .bean.property import Property
from .common.parse_params import parse

def main(**kwargs):
    params = parse()
    configs = os.listdir(params.config_dir)
    os.chdir(params.config_dir)

    cnt = 0
    for config_name in configs:
        if config_name.__contains__('config_'+params.suffix):
            print(config_name)
            t = threading.Thread(target=AutoChecker(Property(config_name), params.test, not(params.immediately)).check, name=config_name)
            t.start()
            cnt += 1
    print('There are ' + str(cnt) + ' configuration file(s) satisfied. ')

if __name__ == '__main__':
    main()




