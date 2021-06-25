from http.server import HTTPServer, BaseHTTPRequestHandler


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except:
            file_to_open = "file not found. it's andrew's fault."
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

    def do_POST(self):
        if self.path == '/':
            self.path = '/index.html'
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except:
            file_to_open = "error sending content."
            self.send_response(404)
        content_length = int(self.headers['Content-Length'])
        data_input = bytes.decode(self.rfile.read(content_length))
        print(data_input)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))


httpd = HTTPServer(('0.0.0.0', 8080), Server)
httpd.serve_forever()
