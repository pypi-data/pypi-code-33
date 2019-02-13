import copy
import enum
import HTMLParser
import json
import paynspray.compression
import paynspray.encoding
import paynspray.rando
import random
import re
import urlparse
from bs4 import BeautifulSoup
from collections import Mapping

DefaultProtocol = '1.1'

class HttpPacketHeader(Mapping):
    def __init__(self):
        self._dict = {}
        self.dcase_hash = {}
        self.junk_headers = None
        self.cmd_string = None
        self.fold = None
        
        self.reset()

    def __iter__(self):
        return iter(self._dict)
        
    def __len__(self):
        return len(self._dict)
        
    def __getitem__(self, key):
        try:
            rv = self._dict[key]
        except KeyError:
            rv = None
            
        if rv is None:
            try:
                rv = self.dcase_hash[str(key).lower()]
            except KeyError:
                rv = None
                
        return rv

    def __setitem__(self, key, value):
        stored = False
        for k in self._dict.keys():
            if (str(k).lower() == str(key).lower()):
                self._dict.update({k: value})
                stored = True
                
        if (stored == False):
            self._dict.update({key: value})
            
        self.dcase_hash.update({key.lower(): value})

    def __contains__(self, key):
        return self.__getitem__(key) is not None

    def __str__(self, prefix = ''):
        string = prefix
        
        if self.junk_headers and self.junk_headers == True:
            while len(string) < 4096:
                if self.fold and self.fold == True:
                    string += "X-{}:\r\n\t{}\r\n".format(paynspray.rando.rand_text_alphanumeric(random.randrange(30) + 5), paynspray.rando.rand_text_alphanumeric(random.randrange(1024) + 1))
                else:
                    string += "X-{}: {}\r\n".format(paynspray.rando.rand_text_alphanumeric(random.randrange(30) + 5), paynspray.rando.rand_text_alphanumeric(random.randrange(1024) + 1))
        
        for var, val in self._dict.iteritems():
            if self.fold and self.fold == True:
                string += "{}:\r\n\t{}\r\n".format(var, val)
            else:
                string += "{}: {}\r\n".format(var, val)
                
        string += "\r\n"
        
        return string

    def from_str(self, header):
        self.reset()
        
        if (len(header) > 0 and re.search(r'\r\n', header) is None):
            header += "\r\n"
        
        header = re.sub(r'([^\r])\n', '\1' + "\r\n", header)
        
        header = re.sub(r':\s*\r\n\s+', ': ', header, flags = re.M | re.I)
        
        serch = re.search(r'.+\r\n', header)
        if (serch is not None):
            self.cmd_string = serch.group(0)
            header.replace(self.cmd_string, "", 1)
        
            
        for string in re.split(r'\r\n', header, flags = re.M):
            md = re.search(r'^(.+?)\s*:\s*(.+?)\s*$', string)
            if (md is not None):
                if md.group(1) in self._dict:
                    self._dict.update({md.group(1):self._dict[md.group(1)] + ", " + md.group(2)})
                else:
                    self._dict.update({md.group(1):md.group(2)})

    def from_list(self, lst):
        for e in lst:
            self._dict.update({e[0]:e[1]})
        return self

    def reset(self):
        self.cmd_string = ''
        self._dict.clear()
        self.dcase_hash.clear()
        return self

class ParseCode(enum.Enum):
    Completed = 1
    Partial = 2
    Error = 3

class ParseState(enum.Enum):
    ProcessingHeader = 1
    ProcessingBody = 2
    Completed = 3

class HttpPacket(object):
    def __init__(self):
        self.headers = HttpPacketHeader()
        self.auto_cl = True
        self.chunk_max_size = 1
        self.chunk_min_size = 1000
        self.body_bytes_left = 0
        self.compress = None
        self.error = None
        self.state = ParseState.ProcessingHeader
        self.incomplete = None
        self.transfer_chunked = False
        self.inside_chunk = False
        self._body = ''
        self.bufq = ''
        self.max_data = None

        self.reset()

    def __getitem__(self, key):
        if key in self.headers:
            return self.headers[key]
            
        for k, v in self.headers.iteritems():
            if (str(k).lower() == str(key).lower()):
                return v
        
        return None
        
    def __setitem__(self, key, value):
        self.headers[key] = value
    
    def __contains__(self, key):
        return key in self.headers

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, string):
        self._body = string

    def parse(self, buf):
        self.bufq += str(buf)
        try:
            if (self.state == ParseState.ProcessingHeader):
                self.parse_header()
            
            if (self.state == ParseState.ProcessingBody):
                if (self.body_bytes_left == 0 and not self.transfer_chunked):
                    self.state = ParseState.Completed
                else:
                    self.parse_body()
        except Exception as e:
            self.error = e
            return ParseCode.Error

        if (self.state == ParseState.Completed):
            return ParseCode.Completed
        else:
            return ParseCode.Partial

    def reset(self):
        self.state = ParseState.ProcessingHeader
        self.transfer_chunked = False
        self.inside_chunk = False
        self.headers.reset()
        self.bufq = ''
        self.body = ''

    def reset_except_queue(self):
        self.state = ParseState.ProcessingHeader
        self.transfer_chunked = False
        self.inside_chunk = False
        self.headers.reset()
        self.body = ''

    @property
    def completed(self):
        if self.state == ParseState.Completed:
            return True

        if (self.state == ParseState.ProcessingBody and self.body_bytes_left < 0):
            return True

        return False

    def chunk(self, string, min_size = 1, max_size = 1000):
        chunked = ''
        
        if (min_size < 1):
            min_size = 1
            
        if (max_size < min_size):
            max_size = min_size
            
        while (len(string) > 0):
            chunk = string[0: random.randrange(max_size - min_size) + min_size]
            string = string[len(chunk):]
            chunked += (("%x" % len(chunk)) + "\r\n" + chunk + "\r\n")
        
        chunked += "0\r\n\r\n"
        return chunked

    def __str__(self):
        if self.body is None:
            content = None
        else:
            content = copy.copy(str(self.body))
        
        if content is not None:
            if self.compress is not None:
                if self.compress == 'gzip':
                    self.headers['Content-Encoding'] = 'gzip'
                    content = paynspray.compression.gzip(content)
                elif self.compress == 'deflate':
                    self.headers['Content-Encoding'] = 'deflate'
                    content = paynspray.compression.zlib_deflate(content)
                elif self.compress == 'none':
                    pass
                else:
                    raise RuntimeError("Invalid Content-Encoding")
                    
            if (self.auto_cl == True and self.transfer_chunked == True):
                raise RuntimeError("'Content-Length' and 'Transfer-Encoding: chunked' are incompatible")
            elif (self.auto_cl == True):
                self.headers['Content-Length'] = len(content)
            elif (self.transfer_chunked == True):
                if self.proto != '1.1':
                    raise RuntimeError("Chunked encoding is only available via HTTP 1.1")
                self.headers['Transfer-Encoding'] = 'chunked'
                content = self.chunk(content, self.chunk_min_size, self.chunk_max_size)
        
        string = self.headers.__str__(self.cmd_string)
        if content is not None:
            string += content
            
        return string

    def from_str(self, string):
        self.reset()
        return self.parse(string)

    @property            
    def cmd_string(self):
        try:
            return self.headers.cmd_string
        except AttributeError:
            return None

    def update_cmd_parts(self, string):
        pass

    def parse_header(self):
        head, data = re.split(r'\r?\n\r?\n', self.bufq, 1)
        
        if data is None:
            return
            
        self.headers.from_str(head)
        if data is not None:
            self.bufq = data
        else:
            self.bufq = ""
            
        self.body_bytes_left = -1
        if 'Content-Length' in self.headers and self.headers['Content-Length'] is not None:
            self.body_bytes_left = int(self.headers['Content-Length'])
            
        if ('Transfer-Encoding' in self.headers and str(self.headers['Transfer-Encoding']).lower() == 'chunked'):
            self.transfer_chunked = True
            self.auto_cl = False
            
        if (self.body_bytes_left == -1):
            if (self.transfer_chunked == False):
                if ('Connection' in self.headers and 'keep-alive' in str(self.headers['Connection']).lower()):
                    self.body_bytes_left = len(self.bufq)
                elif ('Content-Length' not in self.headers and re.search(r'HttpRequest', str(self.__class__)) is not None):
                    self.body_bytes_left = 0
        
        if self.headers.cmd_string is None:
            raise RuntimeError("Invalid command string")
            
        self.state = ParseState.ProcessingBody
        self.update_cmd_parts(self.headers.cmd_string)

    def parse_body(self):
        if len(self.bufq) == 0:
            return
            
        if self.transfer_chunked == True and self.inside_chunk != 1 and len(self.bufq) != 0:
            self.bufq = self.bufq.lstrip()
            
            if '\n' not in self.bufq:
                return
                
            clen = None
            serch = re.search(r'^[a-fA-F0-9]+\r?\n', self.bufq)
            if serch is not None:
                clen = serch.group(0)
                self.bufq.replace(clen, "", 1)
                
            if clen is not None:
                clen = clen.rstrip()
                
            if clen is None and len(self.bufq) == 0:
                return
                
            if clen is None:
                self.state = ParseState.Completed
                return
                
            self.body_bytes_left = int(clen, 16)
            
            if (self.body_bytes_left == 0):
                self.bufq = re.sub(r'^\r?\n(?s)', '', self.bufq)
                self.state = ParseState.Completed
                self.check_100()
                return
                
            self.inside_chunk = 1
        
        if self.body_bytes_left > 0:
            part = self.bufq[0:self.body_bytes_left]
            self.bufq = self.bufq[len(part):]
            self.body = self.body + part
            self.body_bytes_left -= len(part)
        else:
            self.body = self.body + self.bufq
            self.bufq = ''
            
        if (self.transfer_chunked == True and self.body_bytes_left == 0):
            self.inside_chunk = 0
            self.parse_body()
            return
            
        if (self.transfer_chunked == False and self.body_bytes_left == 0):
            self.state = ParseState.Completed
            self.check_100()
            return

    def check_100(self):
        pass

class HttpRequest(HttpPacket):

    PostRequests = ['POST', 'SEARCH']

    def __init__(self, method = 'GET', uri = '/', proto = DefaultProtocol):
        super(HttpRequest, self).__init__()
        self.method = method
        self.raw_uri = uri
        self.uri_parts = {}
        if proto is not None:
            self.proto = proto
        else:
            self.proto = DefaultProtocol
        self.chunk_min_size = 1
        self.chunk_max_size = 10
        self.uri_encode_mode = 'hex-normal'
        self.relative_resource = None
        self.junk_directories = None
        self.junk_slashes = None
        self.junk_self_referring_directories = None
        self.junk_params = None
        self.junk_end_of_url = None
        self.junk_pipeline = None
        self.junk_param_start = None

        self.update_uri_parts()

    def update_cmd_parts(self, string):
        parser = HTMLParser.HTMLParser()
        md = re.search(r'^(.+?)\s+(.+?)\s+HTTP\/(.+?)\r?\n?$', string)
        if md is not None:
            self.method = md.group(1)
            self.raw_uri = parser.unescape(md.group(2))
            self.proto = md.group(3)

            return self.update_uri_parts()
        else:
            raise RuntimeError("Invalid request command string")


    def update_uri_parts(self):
        if self.raw_uri is not None:
            mach = re.search(r'(.+?)\?(.*)$', self.raw_uri)
            if mach is not None:
                self.uri_parts.update({'QueryString':self.parse_cgi_qstring(mach.group(2))})
                self.uri_parts.update({'Resource':mach.group(1)})
            else:
                self.uri_parts.update({'QueryString':{}})
                self.uri_parts.update({'Resource':self.raw_uri})
                
        normalized = self.resource
        normalized = re.sub(r'(\/\.\/|\/\w+\/\.\.\/|\/\/)', '/', normalized)
        self.resource = normalized
        # self.uri_parts.update({'Resource':normalized})
        self.relative_resource = self.resource

    @property
    def uri(self):
        def junk_dirs_block():
            dirs = ''
            for i in range(0, random.randrange(5) + 5):
                dirs += '/' + paynspray.rando.rand_text_alpha(random.randrange(5) + 1) + '/..'
            return dirs + '/'

        if 'Resource' in self.uri_parts:
            string = copy.copy(self.uri_parts['Resource'])
        else:
            string = '/'

        if self.junk_self_referring_directories:
            string = re.sub(r'\/', '/.' * (random.randrange(3) + 1) + '/', string)
        
        if self.junk_param_start:
            string = re.sub(r'\/', '/%3f' + paynspray.rando.rand_text_alpha(random.randrange(5) + 1) + '=' + paynspray.rando.rand_text_alpha(random.randrange(10) + 1) + '/../', string)
        
        if self.junk_directories:
            string = re.sub(r'\/', self.junk_dirs_block(), string)

        if self.junk_slashes:
            string = re.sub(r'\/', '/' * (random.randrange(3) + 2), string)
            string = re.sub(r'^[\/]+', '/', string)

        if self.junk_end_of_url:
            string = re.sub(r'^\/', '/%20HTTP/1.0%0d%0a/../../', string)

        string = paynspray.encoding.uri_encode(string, self.uri_encode_mode)

        if self.method in self.PostRequests:
            if len(self.param_string) > 0:
                string += '?' + self.param_string

        return string
    
    @property
    def param_string(self):
        params = []
        for param, value in self.uri_parts['QueryString'].iteritems():
            if self.junk_params:
                for i in range(0, random.randrange(10) + 5):
                    params.append(paynspray.rando.rand_text_alpha(random.randrange(16) + 5) + '=' + paynspray.rando.rand_text_alpha(random.randrange(10) + 1))
            if type(value) == list:
                for subvalue in value:
                    params.append(paynspray.encoding.uri_encode(param, self.uri_encode_mode) + '=' + paynspray.encoding.uri_encode(subvalue, self.uri_encode_mode))
            else:
                if value is not None:
                    params.append(paynspray.encoding.uri_encode(param, self.uri_encode_mode) + '=' + paynspray.encoding.uri_encode(value, self.uri_encode_mode))
                else:
                    params.append(paynspray.encoding.uri_encode(param, self.uri_encode_mode))

        if self.junk_params:
            for i in range(0, random.randrange(10) + 5):
                params.append(paynspray.rando.rand_text_alpha(random.randrange(32) + 5) + '=' + paynspray.rando.rand_text_alpha(random.randrange(64) + 5))

        return '&'.join(params)

    @uri.setter
    def uri(self, string):
        self.raw_uri = string
        self.update_uri_parts()

    def __str__(self):
        string = ''
        if self.junk_pipeline:
            host = ''
            if 'Host' in self.headers:
                host = "Host: {}\r\n".format(self.headers['Host'])
            string += "GET / HTTP/1.1\r\n{}Connection: Keep-Alive\r\n\r\n" * self.junk_pipeline
            self.headers['Connection'] = 'Closed'
        return string + super(HttpRequest, self).__str__()

    @property
    def body(self):
        string = super(HttpRequest, self).body
        if string is None:
            string = ''

        if len(string) > 0:
            return string

        if self.method in self.PostRequests:
            return self.param_string

        return ''

    @body.setter
    def body(self, string):
        self._body = string

    @property
    def cmd_string(self):
        if re.compile(r'^\d').match(self.proto) is not None:
            proto_str = "HTTP/{}".format(self.proto)
        else:
            proto_str = self.proto
    
        return "{} {} {}\r\n".format(self.method, self.uri, proto_str)

    @property
    def resource(self):
        try:
            return self.uri_parts['Resource']
        except KeyError as e:
            return None

    @resource.setter
    def resource(self, rsrc):
        self.uri_parts.update({'Resource':rsrc})

    @property
    def qstring(self):
        try:
            return self.uri_parts['QueryString']
        except KeyError as e:
            return None

    def parse_cgi_qstring(self, string):
        qstring = {}
        
        for vv in re.split(r'[;&]', string):
            var = vv
            val = ''
            
            mach = re.search(r'(.+?)=(.*)', string)
            if mach is not None:
                var = mach.group(1)
                val = mach.group(2)
                
            if var in qstring:
                if (type(qstring[val]) == list):
                    qstring[val].append(val)
                else:
                    curr = self.qstring[var]
                    qstring.update({var: [curr, val]})
            else:
                qstring.update({var: val})
                
        return qstring


class HttpGetRequest(HttpRequest):
    def __init__(self, uri = '/', proto = DefaultProtocol):
        super(HttpGetRequest, self).__init__("GET", uri, proto)

class HttpPostRequest(HttpRequest):
    def __init__(self, uri = '/', proto = DefaultProtocol):
        super(HttpPostRequest, self).__init__("POST", uri, proto)

class HttpPutRequest(HttpRequest):
    def __init__(self, uri = '/', proto = DefaultProtocol):
        super(HttpPutRequest, self).__init__("PUT", uri, proto)
        
class HttpResponse(HttpPacket):
    def __init__(self, code = 200, message = 'OK', proto = DefaultProtocol):
        super(HttpResponse, self).__init__()
        self.code = int(code)
        self.message = message
        self.proto = proto
        self.auto_cl = True
        self.chunk_min_size = 1
        self.chunk_max_size = 10
        self.count_100 = 0
        self.request = None

    def get_cookies(self):
        cookies = ""
        
        if 'Set-Cookie' in self.headers:
            set_cookies = self.headers['Set-Cookie']
            if set_cookies is None:
                return cookies

            mach = re.findall(r'\s?([^, ;]+?)=([^, ;]*?)[;,]', set_cookies)

            if mach is not None:
                key_vals = dict(mach)
                for k, v in key_vals.iteritems():
                    name = str(k).lower()
                    if name == 'path':
                        continue
                    if name == 'expires':
                        continue
                    if name == 'domain':
                        continue
                    if name == 'max-age':
                        continue
                    cookies += "{}={}; ".format(k, v)
            else:
                return cookies
                
        return cookies.strip()
        
    def get_html_document(self):
        return BeautifulSoup(self.body, 'html.parser')
        
    def get_xml_document(self):
        return BeautifulSoup(self.body, 'xml')

    def get_json_document(self):
        _json = {}
        
        try:
            _json = json.loads(self.body)
        except Exception as e:
            pass

        return _json
        
    def get_html_meta_elements(self):
        bs = self.get_html_document()
        return bs.find_all("meta")

    def update_cmd_parts(self, string):
        mach = re.search(r'HTTP\/(.+?)\s+(\d+)\s?(.+?)\r?\n?$', string)
        if mach is not None:
            self.message = re.sub(r'\r', '', mach.group(3))
            self.code = int(mach.group(2))
            self.proto = mach.group(1)
        else:
            raise RuntimeError("Invalid response command string")

        self.check_100()

    def check_100(self):
        if self.code == 100 and (self.body_bytes_left == -1 or self.body_bytes_left == 0) and self.count_100 < 5:
            self.reset_except_queue()
            self.count_100 += 1

    @property
    def redirect(self):
        return self.code in [301, 302, 303, 307, 308]

    @property
    def cmd_string(self):
        if self.message is not None and len(self.message) > 0:
            return "HTTP/{} {}{}\r\n".format(self.proto, self.code, ' ' + self.message)
        else:
            return "HTTP/{} {}{}\r\n".format(self.proto, self.code, '')

    @property
    def redirection(self):
        try:
            return urlparse.urlsplit(self.headers['Location'])
        except Exception:
            return None

class HttpOKResponse(HttpResponse):
    def __init__(self, message = 'OK', proto = DefaultProtocol):
        super(HttpOKResponse, self).__init__(200, message, proto)

class HttpE404Response(HttpResponse):
    def __init__(self, message = 'Not Found', proto = DefaultProtocol):
        return super(HttpE404Response, self).__init__(404, message, proto)

