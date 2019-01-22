import socketserver


class SshHandler(socketserver.StreamRequestHandler):

    def _write_str(self, text: str):
        self.wfile.write(text.encode('UTF-8'))

    def handle(self):
        self._write_str('SSH-2.0-DEWI' + "\r\n")
        self.data = self.rfile.readline().strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # Likewise, self.wfile is a file-like object used to write back
        # to the client
        self.wfile.write(self.data.upper())
