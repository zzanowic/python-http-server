# tokenizer.py

# A class that parses the request and returns a token when asked
class tokenizer(object):
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.pv_token = None
        self.token = None

    def __call__(self, sep, delim):
        start = self.pos
        token = None
        try:
            for i in range(start, len(self.data)):
                if self.data[i] in sep:
                    if i != start:
                        self.pos = i
                        token = self.data[start : i]
                        break
                    else:
                        self.pos = i + 1
                        token = self.data[start : start + 1]
                        break

                elif self.data[i] in delim:
                    if i != start:
                        self.pos = i + 1
                        token = self.data[start : i]
                        break
                    else:
                        start = i + 1
                        
            if not token:
                self.pos = len(self.data)
                token = self.data[start :]

            self.pv_token = self.token
            self.token = token
            return token
        except TypeError:
            raise TypeError("Seperator or delimiter type does not match data type")