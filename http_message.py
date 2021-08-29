# http_message.py

# A class that holds the headers and content for either a response or request
class http_message(object):
    def __init__(self):
        self._dict = {
            "method" : "",
            "url" : "",
            "version" : "",
            "status-code" : "",
            "status-string" : "",
            "host" : "",
            "upgrade-insecure-requests" : "",
            "accept" : "",
            "user-agent" : "",
            "content-type" : "",
            "content-length" : "",
            "content-disposition" : "",
            "origin" : "",
            "accept-language" : "",
            "accept-encoding" : "",
            "connection" : "",
            "referer" : "",
            "dnt" : "",
            "pragma" : "",
            "cache-control" : "",
            "date" : "",
            "server" : "",
        }

        self.content = ""

    def __getitem__(self, key):
        if key in self._dict:
            return self._dict[key]

        raise KeyError

    def __setitem__(self, key, value):
        if key in self._dict:
            self._dict[key] = value
        else:
            raise KeyError
            
    def __str__(self):
        r = ""
        first = 1
        for key in self._dict:
            if not self._dict[key]:
                continue

            if not first:
                r += "\n"

            first = 0
            r += key + ": "
            if isinstance(self[key], str):
                r += self[key]
            else:
                r += f"{self[key]._dict} {self[key]._list}"

        return r

    def clear(self):
        for key in self._dict:
            self._dict[key] = ""
