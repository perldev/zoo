

class t(object):
    def __init__(self):
        self.data = {"test_attr":1}


    def __getattr__(self, name):



        if self.__dict__["data"].has_key(name):
            return self.data[name]


    def __setattr__(self, key, value):

        if self.data.has_key(key):
            self.data[key] = value
            return True

        object.__setattr__(self, key, value)