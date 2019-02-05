import socket
import sys
import _thread

class ServerSocket():
    ''' Recieves connections, parses the request and ships it off to a handler
    '''
    def __init__(self, address, handler=None):
        ''' Creates a server socket and defines a handler for the server
        '''
        self.socket = socket.socket()
        self.socket.bind(address)
        if handler:
            self.handler = handler
        else:
            self.handler = Handler

    def initialise(self, open_connections=5):
        ''' Initilises the server socket and has it listen for connections
        '''
        self.socket.listen(open_connections)
        self.listen()

    def parse(self, data):
        ''' Splits a packet into the request, the headers (which includes the request), and contents
        '''
        stringed = str(data, 'utf-8')
        split = stringed.split('\r\n\r\n')
        headers = split[0]
        if len(split) > 1:
            content = split[1]
        else:
            content = []
        request = headers.split(' ')[0]

        return request, headers, content

    def handle(self, client, address):
        ''' Parses the data and handles the request. It then closes the connection
        '''
        data = client.recv(1024)
        parsed = self.parse(data)
        handler = self.handler()
        handler.handle(client, parsed, address)
        client.close()

    def listen(self):
        ''' Listens until a keyboard interrupt and handles each connection in a 
                new thread
        '''
        try:
            while True:
                client_data = self.socket.accept()
                _thread.start_new_thread(self.handle, client_data)
        except KeyboardInterrupt:
            self.socket.close()
            

class Handler():
    ''' Handles requests from the Server Socket
    '''
    def status(self, code, message):
        ''' Used to add a status line:
                - 'HTTP/1.1 200 OK' or 'HTTP/1.1 404 Not Found', etc...
        '''
        self.reply_headers = [f'HTTP/1.1 {code} {message}']

    def set_header(self, header, content):
        ''' Defines a custom header and adds it to the response
        '''
        self.reply_headers += [f'{header}: {content}']

    def response(self, content):
        ''' Adds to the content of the response
        '''
        if type(content) == str:
            self.reply_content += content.split('\n')
        else:
            self.reply_content += [content]

    def calculate_content_length(self):
        ''' Calculates the content length and adds it to the header
        '''
        length = len(self.reply_content) * 2
        lengths = [len(line) for line in self.reply_content]
        length += sum(lengths)
        self.set_header('Content-Length', length)

    def send_file(self, file_name):
        with open(file_name, 'rb') as file:
            file_contents = file.read()
        self.response(file_contents)

    def get_address(self):
        return self.address

    def reply(self):
        ''' Assembles the response and sends it to the client
        '''
        if self.reply_headers[0][0:4] != "HTTP":
            self.status(200, 'OK')
            self.set_header('Content-Type', 'text/html')
            self.reply_content = ['<p>Response Status unspecified</p>']

        self.calculate_content_length()

        message =  '\r\n'.join(self.reply_headers)
        message += '\r\n\r\n'
        try:
            message += '\r\n'.join(self.reply_content)
            message += '\r\n'
        except TypeError:
            message = bytes(message, 'utf-8')
            message += b'\r\n'.join(self.reply_content)
            message += b'\r\n'

        try:    
            if type(message) == str:
                self.client.send(bytes(message, 'utf-8'))
            else:
                self.client.send(message)
        except:
            pass

    def handle(self, client, parsed_data, address):
        ''' Initialises variables and case-switches the request type to
                determine the handler function
        '''
        self.client = client
        self.address = address
        self.reply_headers = []
        self.reply_content = []
        self.headers = True
        request = parsed_data[0]
        headers = parsed_data[1].split('\r\n')
        contents = parsed_data[2]

        if request == "GET":
            func = self.get
        elif request == "POST":
            func = self.post
        elif request == "HEAD":
            func = self.head
        elif request == "PUT":
            func = self.put
        elif request == "DELETE":
            func = self.delete
        elif request == "CONNECT":
            func = self.connect
        elif request == "OPTIONS":
            func = self.options
        elif request == "TRACE":
            func = self.trace
        elif request == "PATCH":
            func = self.patch
        else:
            func = self.default

        func(headers, contents)
        self.reply()

    def default(self, headers, contents):
        ''' If the request is not known, defaults to this
        '''
        self.status(200, 'OK')
        self.set_header('Content-Type', 'text/html')
        self.response('''<p>Unknown Request Type</p>''')

    def get(self, headers, contents):
        ''' Overwrite to customly handle GET requests
        '''
        self.status(200, 'OK')
        self.set_header('Content-Type', 'text/html')
        self.response('''<p>Successfully got a GET Request</p>''')

    def post(self, headers, contents):
        ''' Overwrite to customly handle POST requests
        '''
        self.status(200, 'OK')
        self.set_header('Content-Type', 'text/html')
        self.response('''<p>Successfully got a POST Request</p>''')

    def head(self, headers, contents):
        ''' Overwrite to customly handle HEAD requests
        '''
        self.status(200, 'OK')
        self.set_header('Content-Type', 'text/html')
        self.response('''<p>Successfully got a HEAD Request</p>''')

    def put(self, headers, contents):
        ''' Overwrite to customly handle PUT requests
        '''
        self.status(200, 'OK')
        self.set_header('Content-Type', 'text/html')
        self.response('''<p>Successfully got a PUT Request</p>''')

    def delete(self, headers, contents):
        ''' Overwrite to customly handle DELETE requests
        '''
        self.status(200, 'OK')
        self.set_header('Content-Type', 'text/html')
        self.response('''<p>Successfully got a DELETE Request</p>''')

    def connect(self, headers, contents):
        ''' Overwrite to customly handle CONNECT requests
        '''
        self.status(200, 'OK')
        self.set_header('Content-Type', 'text/html')
        self.response('''<p>Successfully got a CONNECT Request</p>''')

    def options(self, headers, contents):
        ''' Overwrite to customly handle OPTIONS requests
        '''
        self.status(200, 'OK')
        self.set_header('Content-Type', 'text/html')
        self.response('''<p>Successfully got an OPTIONS Request</p>''')

    def trace(self, headers, contents):
        ''' Overwrite to customly handle TRACE requests
        '''
        self.status(200, 'OK')
        self.set_header('Content-Type', 'text/html')
        self.response('''<p>Successfully got a TRACE Request</p>''')

    def patch(self, headers, contents):
        ''' Overwrite to customly handle PATCH requests
        '''
        self.status(200, 'OK')
        self.set_header('Content-Type', 'text/html')
        self.response('''<p>Successfully got a PATCH Request</p>''')


# =======================================================================

if __name__ == "__main__":
    import os

    class CustomHandler(Handler):
        def _generate_response(self, headers):
            directory = headers.split(' ')[1]
            self.set_header('Content-Type', 'text/html')
            response = f'<title>{directory}</title>'
            for thing in os.listdir():
                response += f'<br><a href="./{directory}/{thing}">{thing}</a>'

            return response

        def get(self, headers, contents):
            self.status(200, 'OK')
            self.response(self._generate_response(headers))

    def log(text, show=False, mode='a'):
        if show:
            print(text)
        with open('server.log', mode) as logfile:
            logfile.write(f'{text}\n')

    def run():
        log('[+] Starting server', True, 'w')

        if len(sys.argv) > 1:    
            address = ('0.0.0.0', int(sys.argv[1]))
        else:
            address = ('0.0.0.0', 80)

        try:
            http_server = ServerSocket(address, CustomHandler) 
            log('[+] Running server', True)
            http_server.initialise()
        except OSError as e:
            log(f'[+] Retry with sudo: OS Error: {e}', True)
        except Exception as e:
            log(f'[+] Exception: {e}', True)
    

    run()
