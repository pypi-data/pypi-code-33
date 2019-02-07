from fn import F
from configparser import ConfigParser
from os import path
import os
import logging

def loadHandlerNames():
    def work(config_name, section_name):
        if not path.exists(config_name):
            print('config is not found at {}/{}.'.format(os.getcwd(), config_name))
            return []

        config = ConfigParser(allow_no_value=True)
        config.read(config_name)

        if len(config.sections()) == 0:
            print('no settings in section {}'.format(section_name))
            return []

        return dict(config[section_name])

    return work("slogger.cfg", "handlers")

def getValidNames(all_handler_names):
    def buildObj(name, val, reg_rexp):
        import re
        return {
            'name': re.match(reg_rexp, name).group(1),
            'level': re.match(reg_rexp, name).group(2),
            'filters': [] if val == '' or val == None else [(lambda s:s.strip())(s) for s in val.split(',')]
        }
    return [buildObj(name, all_handler_names[name], '''([\w\_\d]+)_(\w+)''') for name in all_handler_names]        

def loadHandlers(logger, category):


    def buildHandlers(handler_names):
        def dummy(handler_dict, handler_name_key, type_of_interval, handler_key, get_file_name):
            from logging.handlers import TimedRotatingFileHandler

            def buildWithCategory():
                return TimedRotatingFileHandler(get_file_name(handler_dict[handler_name_key]), type_of_interval) if \
                    len(handler_dict["filters"]) == 0 or \
                    ("!" in handler_dict["filters"] and category not in handler_dict["filters"]) or \
                    ("!" not in handler_dict["filters"] and category in handler_dict["filters"])  else None

            def buildWithLevel(handler):
                def setlevel(level_dict, level_key):
                    if level_key not in level_dict:
                        raise ValueError("level {} is not correct".format(level_key))
                    handler.setLevel(level_dict[level_key])

                    return handler

                return setlevel({
                    "all": 0,
                    "notset": 0,
                    "debug": 10,
                    "info": 20,
                    "warning": 30,
                    "error": 40,
                    "critical": 50
                }, handler_dict["level"].lower()) if handler != None else handler

            def setFormatter(handler):
                if not handler:
                    return handler
                
                handler.setFormatter(logging.Formatter('%(asctime)s %(name)s[line:%(lineno)d] %(levelname)s %(message)s'))
                return handler

            handler_dict[handler_key] = setFormatter(buildWithLevel(buildWithCategory()))

            return handler_dict

        return [dummy(handler_dict, "name", "D", "handler", lambda name: "{}.log".format(name)) for handler_dict in handler_names]

    def filterHandlers(handler_names):
        return [handler for handler in handler_names if handler["handler"] != None]


    def setHandlers(handler_names):
        if len(handler_names) == 0:
            print("no handlers are configured. the root logger will be used. Please run logging.basicConfig(level=?) to set the level, the default level is warning")
            logger.propagate = True
        else:
            print("Configured handlers will work")
            logging.root.setLevel(0)
            logger.propagate = False
            
        for handler_dict in handler_names:
            logger.addHandler(handler_dict["handler"])

    (F(loadHandlerNames) >> \
        F(getValidNames) >> \
        F(buildHandlers) >> \
        F(filterHandlers) >> \
        F(setHandlers))()
    
    return logger
