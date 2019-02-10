from datetime import datetime, timedelta

class Logger:

    ##
    # Func: LogInfo
    # Description: To log Information
    ##
    @staticmethod
    def LogInfo(message):
        Logger.LogMessage(message, "INFO")

    ##
    # Func: LogWarn
    # Description: To log Warning
    ##
    @staticmethod
    def LogWarn(message):
        Logger.LogMessage(message, "WARN")

    ##
    # Func: LogError
    # Description: To log Error
    ##
    @staticmethod
    def LogError(message):
        Logger.LogMessage(message, "ERROR")
    
    ##
    # Func: LogDebug
    # Description: To log debug information
    ##
    @staticmethod
    def LogDebug(message):
        Logger.LogMessage(message, "DEBUG")

    ##
    # Func: LogMessage
    # Description: To log Message with any tag
    ##  
    @staticmethod
    def LogMessage(message, tag):
        currentDateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        finalMessage = "[{currentDateTime}] {tag} : {message}".format(currentDateTime = currentDateTime, tag = tag, message = message)
        print (finalMessage)