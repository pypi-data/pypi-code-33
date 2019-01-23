

class Response(object):

    def __init__(self, code, payload, options):
        self.code = code
        self.payload = payload
        self.options = options.toDict()


    def __str__(self):
            return "<Response - Code:{} Payoad:{} Options: {}>".format(self.code, self.payload, self.options)
