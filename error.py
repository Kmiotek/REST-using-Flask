class Error(Exception):
    def __init__(self, code, message):
        Exception.__init__(self)
        self.code = code
        self.message = message