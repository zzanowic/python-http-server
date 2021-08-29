# http_server.py

import socket
from sys import argv
from os import system
import datetime
from tokenizer import tokenizer
from http_message import http_message

# Error constants to set web_server.err as
TIMEOUT = 1
INVALID_REQUEST = 2
INVALID_RESPONSE = 3

# Default 404 response
message_404 = b"<!DOCTYPE html><html><body>404 Not Found</body></html>"

# Invalid request response
message_invalid_reponse = b"HTTP Request could not be understood"

# The main class
# It creates a server and handles incoming connections
class web_server(socket.socket):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.err = 0
        self.timeout_s = .5
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.bind((host, port))

    # Used as main html folder
    def set_home_dir(self, home):
        self.home = home
 
    def serve_forever(self, queue_size):
        self.listen(queue_size)
        print(f"Serving HTTP from {self.host} on {self.port} ...")
        while (not self.err):
            try:
                (client, address) = self.accept()
                if client:
                    system("clear")
                    print(f"Client connection: {address}")
                    self._handle_client(client)
                    client.close()
            except Exception as e:
                print(f"Exception while listening for client: '{e}'")
            except KeyboardInterrupt:
                self.close()
                break
    
    def _handle_error(self):
        if self.err == TIMEOUT:
            print(f"Connection timed out. Timeout = {self.timeout_s}")
            self.err = 0
            return 1
        elif self.err == INVALID_REQUEST:
            print("Request message could not be understood")
            self.response.content = message_invalid_reponse
            self.err = 0
            return 0
        elif self.err == INVALID_RESPONSE:
            print("Invalid response")
            self.err = 0
            return 0

    request = http_message()
    response = http_message()
    
    # Receives, parse, then replies
    def _handle_client(self, client):
        client.settimeout(self.timeout_s)

        self.request.clear()
        self.response.clear()

        self._recv_request(client)
        if self._handle_error():
            return

        print(self.request)
        response_data = self._form_response()
        if self._handle_error():
            return

        client.sendall(response_data)

    # Receives request and fills internal request class
    def _recv_request(self, client):
        try:
            data = client.recv(1024)
        except socket.timeout:
            self.err = TIMEOUT
            return

        tokens = tokenizer(data)
        
        method = tokens(b"\n", b" ").decode("utf-8")
        url = tokens(b"\n", b" ").decode("utf-8")
        version = tokens(b"\n", b" ").decode("utf-8")

        self._read_headers(tokens)

        if method == "\n" or url == "\n" or version == "\n":
            self.err = INVALID_REQUEST
            return
        
        self.request["method"] = method
        self.request["url"] = url
        self.request["version"] = version

        self.request.content = tokens(b"", b"")
        if self.request["content-length"] and self.request.content:
            content_length = int(self.request["content-length"])
            while len(self.request.content) < content_length:
                try:
                    data = client.recv(1024)
                    self.request.content += data
                except Exception:
                    self.err = TIMEOUT
                    return

    # Reads request headers in request class
    def _read_headers(self, tokens):
        token = tokens(b"\n", b"\r")
        while token:
            if token == b"\n":
                if tokens.pv_token == b"\n":
                    break
            else:
                token_parts = token.decode("utf-8").partition(":")
                key = token_parts[0].lower()
                value = token_parts[2].strip()
                try:
                    self.request[key] = value
                except KeyError:
                    print("Unknown key: ", end="")
                    print(token)

            token = tokens(b"\n", b"\r")

    # Calls corresponding method function and returns a string http response holding the response
    def _form_response(self):
        self.response["server"] = "Python Server"
        # Tue, 24 Aug 2021 05:37:48 GMT
        # date = datetime.datetime.
        self.response["date"] = "today"
        self.response["version"] = "HTTP/1.1"
        method = self.request["method"].lower()
        if method == "get":
            self._method_get()
        elif method == "post":
            self._method_post()
            
        if not self.response["status-code"] or not self.response["status-string"]:
            self.err = INVALID_RESPONSE

        response_data = self.response["version"] + " "
        response_data += self.response["status-code"] + " " 
        response_data += self.response["status-string"] + "\r\n"
        response_data += "date: " + self.response["date"] + "\r\n"
        response_data += "server: " + self.response["server"] + "\r\n"
        response_data += "content-type: " + self.response["content-type"] + "\r\n"
        response_data += "content-length: " + self.response["content-length"] + "\r\n"
        response_data += "\r\n"
        response_data = response_data.encode()
        if self.response.content:
            response_data  += self.response.content

        return response_data

    def _method_get(self):
        url = self.request["url"]

        if url == "/":
            url = "/index.html"

        try:
            with open(self.home + url, "rb") as file:
                self.response.content = file.read()
                self.response["status-code"] = "200"
                self.response["status-string"] = "OK"
                period = url.rfind(".")
                if period != -1:
                    file_type = url[period+1 : ]
                    if file_type.lower() == "html":
                        self.response["content-type"] = "text/html"
                    else:
                        self.response["content-type"] = file_type

        except FileNotFoundError:
            print("could not find " + url)
            try:
                with open(self.home + "/404.html", "rb") as file:
                    self.response.content = file.read()
            except FileNotFoundError:
                self.response.content = message_404

            self.response["content-type"] = "text/html"
            self.response["status-code"] = "404"
            self.response["status-string"] = "NOT FOUND"

        self.response["content-length"] = str(len(self.response.content))

    def _method_post(self):
        self.response["status-code"] = "200"
        self.response["status-string"] = "OK"
        # TODO
        self.response.content = b"post"
        self.response["content-length"] = str(len(self.response.content))
        

def main():
    if len(argv) != 4:
        print("Usage:\n\thttp_server.py host_address host_port home_directory\n")
        return 1
    server = web_server(argv[1], int(argv[2]))
    server.set_home_dir(argv[3])
    server.serve_forever(5)

if __name__ == "__main__":
    main()