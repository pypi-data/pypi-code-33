import logging
from logging.config import fileConfig
from enum import Enum
import os.path

class LogconfigSections(Enum):
    """
      The enumeration class, holding the sections of Log configuration file. 
      
    """
    LOGGERS = 'loggers'
    HANDLERS = 'handlers'
    FORMATTERS = 'formatters'
    LOGGER_ITEM = 'logger_'
    HANDLER_ITEM = 'handler_'
    FORMATTER_ITEM = 'formatter_'
    
    @staticmethod
    def is_section(section, test_string:str, item:str = None):
        """
          Return if test_string denotes the beginning of the section.
        
          :param section: The section to be tested.
          :type section: LogconfigSections.
          :param test_string: The string to be tested.
          :type test_string: str
          :param item: the item described in the section.
          :type item: str
          :returns: True if test_string denotes the beginning of the section.
          :rtype: bool
          
        """
        if item is None:
            return test_string == ''.join(['[', section.value, ']'])
        else:
            return test_string == ''.join(['[', section.value, item, ']'])

class LogconfigFactory:
    """
      This class contains helper methods write the default fileConfig.
    
    """
    
    def __init__(self, file_name, logger_name, log_level=logging.INFO):
        """Constructor
          :param file_name: the log file name.
          :type file_name: str
          :parm logger_name: the name of a logger itself.
          :type logger_name: str
          :param log_level: level at which to log (i.e. INFO, DEBUG, etc.)
          :type log_level: int
          
        """
        self._success=True
        ##Validate the file and if file is not valid, generate the default one.
        try:
            logging.config.fileConfig(file_name)
            next = None
            with open(file_name, 'r') as fle_in:
                for line in fle_in:
                    line = line.strip()
                    if LogconfigSections.is_section(LogconfigSections.LOGGERS, line):
                        next = LogconfigSections.LOGGERS
                    elif next == LogconfigSections.LOGGERS and line != '':
                        if logger_name not in line:
                            raise ValueError('Invalid log file nneds to be regenerated.')
                        else:
                            break #The logger name found, the file is valid.
        except:
            #Generate default file
            try:
                with open(file_name, 'w') as fleOut:
                    log_level_str = logging.getLevelName(log_level)
                    #The list the loggers described in the file.
                    logger_list = ["root", logger_name]
                    #Write the list of loggers.
                    self.__writeListSection(fleOut, LogconfigSections.LOGGERS.value, logger_list)
                    #Write the list of handlers. Handler defines how the lig strings will be saved.
                    self.__writeListSection(fleOut, LogconfigSections.HANDLERS.value, ["hand01"])
                    #Write the list of formatters mensioned in the file.
                    self.__writeListSection(fleOut, LogconfigSections.FORMATTERS.value, ["form01"])
                    #Write the description of root logger: match it with log level and handler.
                    self.__writeLoggerSection(fleOut, "root", log_level_str, "hand01")
                    #Write the description of this logger: match it with log level and handler.
                    self.__writeLoggerSection(fleOut, logger_name, log_level_str, "hand01")
                    #Write the description of the only handler in the file. Match it with formatter and handler debug level.
                    #Define the type of output(in this case use StreamHandler and write to sys.stdout).
                    self.__writeHandlerSection(fleOut, "hand01", "StreamHandler", "DEBUG", "form01", "sys.stdout")
                    #Write the formatter description. Define the defaild log string format.
                    self.__writeFormatterSection(fleOut, "form01", "logging.Formatter", 'F1 %(asctime)s %(levelname)s %(message)s')
            except:
                #file creation failed
                print("Failed to create configuration file {}".format(file_name))
                self._success=False
            
    def __writeListSection(self, file_handle, section_name, lst):
        """
          Write the property list into the config files at the section section_name.
          Example:
          [section]
          keys=lst[0], lst[1] ...

          :param file_handle: the file handle with the opened file top write the data to.
          :type file_handle: _io.TextIOWrapper
          :param section_name: - the name of a section to be written.
          :type section_name: str
          :param lst: - the list to be written as a values.
          :type lst: list
          
        """
        file_handle.write("[{}]\n".format(section_name))
        file_handle.write("keys={}\n\n".format(",".join(lst)))

    def __writeLoggerSection(self, file_handle, name, level, *handlers):
        """
          Write the logger section. 
          Example:
          [logger_root]
          level=WARNING
          handlers=hand01
        
          :param file_handle: - the file handle with the opened file top write the data to.
          :type file_handle:  _io.TextIOWrapper.
          :param name: - the name of a logger.
          :type name: str
          :param level: - log level.
          :type level: str
          :param *handlers - the log handlers of given logger.
          
        """
        file_handle.write("[logger_{}]\n".format(name))
        file_handle.write("level={}\n".format(level))
        if name!='root':
            file_handle.write("handlers={}\n".format(",".join(handlers)))
            file_handle.write("qualname={}\n".format(name))
            file_handle.write("propagate=0\n\n")
        else:
            file_handle.write("handlers={}\n\n".format(",".join(handlers)))
    
    def __writeHandlerSection(self, file_handle, name, handler_class, level, format, *args):
        """
          Write the handler section.
          Example:
          [handler_hand01]
          class=StreamHandler
          level=DEBUG
          formatter=form01
          args=(sys.stdout,)
        
          :param file_handle: the file handle with the opened file top write the data to.
          :type file_handle: _io.TextIOWrapper
          :param name: the name of a logger.
          :type name: str
          :param handler_class: one of python logger handler classes.
          :type handler_class: str
          :param name: the name of a formatter.
          :type name: str
          :param format: The name of formatter (see __writeFormatterSection).
          :type format: str
          
        """
        file_handle.write("[handler_{}]\n".format(name))
        file_handle.write("class={}\n".format(handler_class))
        file_handle.write("level={}\n".format(level))
        file_handle.write("formatter={}\n".format(format))
        if len(args)>0:
            file_handle.write("args=({},)\n\n".format(",".join(args)))
        else:
            file_handle.write("\n")

    def __writeFormatterSection(self, file_handle, name, formatter_class, format):
        """
          Write the formatter section.

          :param file_handle: the file handle with the opened file top write the data to.
          :type file_handle: _io.TextIOWrapper
          :param name: the name of a handler.
          :type name: str
          :param formatter_class: the name of formatter class for example logging.Formatter.
          :type formatter_class: str
          :param format: the format string.
          :type format: str
          
        """
        file_handle.write("[formatter_{}]\n".format(name))
        file_handle.write("format={}\n".format(format))
        file_handle.write("class={}\n\n".format(formatter_class))

    def getSuccess(self):
        """
          getSuccess returns True if the ini file was successfully created.
        
          :returns: True if the ini file was successfully created
          :rtype: bool
          
        """
        return self._success
