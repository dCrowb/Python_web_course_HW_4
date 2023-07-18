from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
from collections import UserDict
import json
import datetime
import socket
from threading import Thread


class UserMessages(UserDict):
    def __init__(self):
        self.data = {}

    def add_data(self, new_message):
        data_parse = urllib.parse.unquote_plus(new_message.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        timestamp = datetime.datetime.now()
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.data.update({timestamp: data_dict})

    def load_messages_db(self, file):
        if pathlib.Path(file).is_file():
            with open(file, 'r') as json_file:
                self.data = json.load(json_file)
        else:
            self.data = {}

    def save_messages_db(self, file):
        with open(file, 'w') as json_file:
            json.dump(self.data, json_file)


JSON_DATA_STORE = './storage/data.json'
IP = '127.0.0.1'
PORT = 5000

def run_server(ip, port):
    print('server')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    while True:
        print('server')
        data, address = sock.recvfrom(1024)
        user_messages_db.add_data(data)
        user_messages_db.save_messages_db(JSON_DATA_STORE)
    sock.close()

def run_client(user_message):
    print('client')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(user_message, (IP, PORT))
    sock.close()

class HttpGetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_path = urllib.parse.urlparse(self.path)
        if url_path.path == '/':
            self.send_html_file('index.html')
        elif url_path.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(url_path.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())
                  
    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        run_client(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
        
    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as html_file:
            self.wfile.write(html_file.read())


def run(server_class=HTTPServer, handler_class=HttpGetHandler):
    print(user_messages_db)
    server_address = ('127.0.0.1', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

    
if __name__ == '__main__':
    user_messages_db = UserMessages()
    user_messages_db.load_messages_db(JSON_DATA_STORE)
    http_server = Thread(target=run)
    http_server.start()
    sock_server = Thread(target=run_server(IP, PORT))
    sock_server.start()
    print('end')