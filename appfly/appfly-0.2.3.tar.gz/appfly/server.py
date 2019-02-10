from jsonmerge import merge

class Server():
    def __init__(self, app, socketio=None):
        self.__app = app
        self.__socketio = socketio
        self.__config = {
                "server": {
                    "socket":"",
                    "ip":"0.0.0.0",
                    "port": 3000
                },
                "debug":False
            }

    def start(self, options=None):
        if options:
            self.__config = merge(self.__config, options)

        if self.__socketio:
            self.__socketio.run(self.__app, debug=self.__config["debug"], port=self.__config["server"]["port"], host=self.__config["server"]["ip"])
            print('\n[socketio] - API is running...')
        else:
            self.__app.run(debug=self.__config["debug"], port=self.__config["server"]["port"], host=self.__config["server"]["ip"])
            print('\n[app] - API is running...')