import bombfuse
import datetime
import OpenSSL
import random
import select
import socket
import sockets
import amncore.sync as sync
import amncore.xcepts as xcepts

class SecureSock(object):

    class CertProv(object):
        @classmethod
        def ssl_generate_subject(self):
            import paynspray.rando
            nom = OpenSSL.crypto.X509Name(OpenSSL.crypto.X509().get_subject())

            st = str(paynspray.rando.rand_state())
            loc = str(paynspray.rando.rand_name()).capitalize()
            org = str(paynspray.rando.rand_name()).capitalize()
            cn = str(paynspray.rando.rand_hostname())

            nom.C = "US"
            nom.ST = st
            nom.L = loc
            nom.O = org
            nom.CN = cn
            return nom

        @classmethod
        def ssl_generate_issuer(self):
            import paynspray.rando
            nom = OpenSSL.crypto.X509Name(OpenSSL.crypto.X509().get_issuer())

            org = str(paynspray.rando.rand_name()).capitalize()
            cn = str(paynspray.rando.rand_name()).capitalize() + " " + str(paynspray.rando.rand_name()).capitalize()

            nom.C = "US"
            nom.O = org
            nom.CN = cn
            return nom
        
        @classmethod
        def ssl_generate_certificate(self):
            yr = 24 * 3600 * 365
            vf = datetime.datetime.now() - datetime.timedelta(seconds = (random.randrange(yr * 3) + yr))
            vt = vf + datetime.timedelta(seconds = ((random.randrange(9) + 1) * yr))
            vf = vf.strftime("%Y%m%d%H%M%SZ")
            vt = vt.strftime("%Y%m%d%H%M%SZ")
            subject = self.ssl_generate_subject()
            issuer = self.ssl_generate_issuer()
            key = OpenSSL.crypto.PKey()
            key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
            cert = OpenSSL.crypto.X509()
            cert.set_version(2)
            cert.set_serial_number((random.randrange(0xFFFFFFFF) << 32) + random.randrange(0xFFFFFFFF))
            cert.set_subject(subject)
            cert.set_issuer(issuer)
            cert.set_notBefore(vf)
            cert.set_notAfter(vt)
            cert.set_pubkey(key)
        
            ef = OpenSSL.crypto.X509Extension
            cert.add_extensions([ef("basicConstraints", True, "CA:FALSE")])
        
            cert.sign(key, 'sha256')
        
            return [key, cert, None]

    cert_prov = CertProv

    def __init__(self, *args, **kwargs):
        if hasattr(self, "sock") == False:
            self.sock = None
        return super(SecureSock, self).__init__(*args, **kwargs)

    @property
    def cert_provider(self):
        return self.cert_prov

    @cert_provider.setter
    def cert_provider(self, val):
        self.cert_prov = val

    @classmethod
    def ssl_parse_pem(self, ssl_cert):
        import x509
        return x509.X509Cert.parse_pem(ssl_cert)

    @classmethod
    def ssl_generate_subject(self):
        return self.cert_prov.ssl_generate_subject()

    @classmethod
    def ssl_generate_issuer(self):
        return self.cert_prov.ssl_generate_issuer()

    @classmethod
    def ssl_generate_certificate(self):
        return self.cert_prov.ssl_generate_certificate()

    def makessl(self, params):
        import paynspray.rando
        if hasattr(params, "ssl_cert") == True and params.ssl_cert is not None:
            key, cert, chain = self.ssl_parse_pem(params.ssl_cert)
        else:
            key, cert, chain = self.ssl_generate_certificate()

        ctx = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_2_METHOD)
        
        if key is not None:
            ctx.use_privatekey(key)
        if cert is not None:
            ctx.use_certificate(cert)
        if chain is not None and chain != []:
            ctx.add_extra_chain_cert(chain)

        ctx.set_options(0)
        
        if hasattr(params, "ssl_cipher") == True:
            if params.ssl_cipher is not None:
                ctx.set_cipher_list(params.ssl_cipher)

        if hasattr(OpenSSL.SSL, "OP_NO_COMPRESSION") == True:
            if hasattr(params, "ssl_compression") == True:
                if params.ssl_compression is not None and params.ssl_compression == False:
                    ctx.set_options(OpenSSL.SSL.OP_NO_COMPRESSION)

        ctx.set_session_id(paynspray.rando.rand_text(16))
        
        return ctx

    def allow_nonblock(self, sock = None):
        import amncore.compat
        if sock is None:
            if hasattr(self, "sock") == True:
                sock = self.sock
        avail = hasattr(sock, "setblocking")
        if avail == True and amncore.compat.is_windows() == True:
            return True
        return False
        
class SslTcpSock(sockets.TcpSock):
    def __init__(self, *args, **kwargs):
        if hasattr(self, "ssl_negotiated_version") == False:
            self.ssl_negotiated_version = None
        if hasattr(self, "sslsock") == False:
            self.sslsock = None
        if hasattr(self, "sslctx") == False:
            self.sslctx = None
        return super(SslTcpSock, self).__init__(*args, **kwargs)

    @classmethod
    def create(self, **kwargs):
        kwargs['SSL'] = True
        return self.create_param(sockets.SocketParams.from_kwargs(**kwargs))
    
    @classmethod
    def create_param(self, param):
        param.ssl = True
        return super(SslTcpSock, self).create_param(param)

    def initsock(self, params = None):
        super(SslTcpSock, self).initsock(params)

        SSLv2 = 1
        SSLv3 = 2
        SSLv23 = 3
        TLSv1 = 4
        TLSv1_1 = 5
        TLSv1_2 = 6

        version = OpenSSL.SSL.SSLv23_METHOD

        if params is not None and params.ssl_version is not None:
            if params.ssl_version == 'SSL2' or params.ssl_version == SSLv2:
                version = OpenSSL.SSL.SSLv2_METHOD
            elif params.ssl_version == 'SSL23' or params.ssl_version == SSLv23 or params.ssl_version == 'TLS' or params.ssl_version == 'Auto':
                version = OpenSSL.SSL.SSLv23_METHOD
            elif params.ssl_version == 'SSL3' or params.ssl_version == SSLv3:
                version = OpenSSL.SSL.SSLv3_METHOD
            elif params.ssl_version == 'TLS1' or params.ssl_version == 'TLS1.0' or params.ssl_version == TLSv1:
                version = OpenSSL.SSL.TLSv1_METHOD
            elif params.ssl_version == 'TLS1.1' or params.ssl_version == TLSv1_1:
                version = OpenSSL.SSL.TLSv1_1_METHOD
            elif params.ssl_version == 'TLS1.2' or params.ssl_version == TLSv1_2:
                version = OpenSSL.SSL.TLSv1_2_METHOD

        self.initsock_with_ssl_version(params, version)

        self.ssl_negotiated_version = version

        return self.ssl_negotiated_version

    def initsock_with_ssl_version(self, params, version):
        self.sslctx = OpenSSL.SSL.Context(version)

        if params is not None and params.ssl_client_cert is not None:
            tmp_cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, params.ssl_client_cert)
            self.sslctx.use_certificate(tmp_cert)
            
        if params is not None and params.ssl_client_key is not None:
            tmp_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, params.ssl_client_key)
            self.sslctx.use_privatekey(tmp_key)

        if params is not None and params.ssl_verify_mode is not None:
            verify_mode = getattr(OpenSSL.SSL, "VERIFY_{}".format(params.ssl_verify_mode))
        else:
            verify_mode = OpenSSL.SSL.VERIFY_PEER
            
        self.sslctx.set_verify(verify_mode, verify_cb)
        
        self.sslctx.set_options(OpenSSL.SSL.OP_ALL)

        if hasattr(params, "ssl_cipher") == True:
            if params.ssl_cipher is not None:
                self.sslctx.set_cipher_list(params.ssl_cipher)
            
        self.sslsock = OpenSSL.SSL.Connection(self.sslctx, self.sock)
        self.sslsock.set_connect_state()
        self.sslsock.set_tlsext_host_name(params.peerhost)
        
        def nonblock_handshake_proc():
            while True:
                try:
                    self.sslsock.do_handshake()
                    break
                except OpenSSL.SSL.WantReadError as e:
                    select.select([self.sslsock], [], [], 0.10)
                    continue
                except OpenSSL.SSL.WantWriteError as e:
                    select.select([], [self.sslsock], [], 0.10)
                    continue
                except Exception as e:
                    raise e

        if self.allow_nonblock() == False:
            try:
                self.sslsock.do_handshake()
            except socket.timeout as e:
                raise xcepts.ConnectionTimeout(params.peerhost, params.peerport)
        else:
            self.sslsock.setblocking(0)
            try:
                bombfuse.timeout(params.timeout, nonblock_handshake_proc)
            except bombfuse.TimeoutError as e:
                raise xcepts.ConnectionTimeout(params.peerhost, params.peerport)

    def write(self, buf, **kwargs):
        if self.allow_nonblock() == False:
            self.sslsock.setblocking(1)
            return self.sslsock.send(buf)

        total_sent = 0
        total_length = len(buf)
        block_size = 16384
        retry_time = 0.5
        
        self.sslsock.setblocking(0)
        while True:
            try:
                while (total_sent < total_length):
                    s = sync.select_s([], [self.sslsock], [], 0.25)
                    if s == ([],[],[]) or self.sslsock not in s[1]:
                        continue
                    data = buf[total_sent:block_size]
                    sent = self.sslsock.send(data)
                    if sent > 0:
                        total_sent += sent
                break
            except IOError as e:
                return None
            except OpenSSL.SSL.WantReadError as e:
                select.select([self.sslsock], [], [], retry_time)
                continue
            except OpenSSL.SSL.WantWriteError as e:
                select.select([], [self.sslsock], [], retry_time)
                continue
            except OpenSSL.SSL.Error as e:
                return None
            except Exception as e:
                raise e

        return total_sent

    def read(self, length = None, **kwargs):
        if self.allow_nonblock() == False:
            self.sslsock.setblocking(1)
            if length is None:
                length = 16384
            try:
                return self.sslsock.recv(length)
            except (IOError, OpenSSL.SSL.Error) as e:
                return None
            return

        self.sslsock.setblocking(0)
        while True:
            try:
                s = sync.select_s([self.sslsock], [], [], 0.10)
                if (s == ([],[],[]) or self.sslsock not in s[0]):
                    continue
                return self.sslsock.recv(length)
            except IOError as e:
                return None
            except OpenSSL.SSL.WantReadError as e:
                select.select([self.sslsock], [], [], 0.5)
                continue
            except OpenSSL.SSL.WantWriteError as e:
                select.select([], [self.sslsock], [], 0.5)
                continue
            except OpenSSL.SSL.Error as e:
                return None
            except Exception as e:
                raise e
                
    def close(self):
        try:
            self.sslsock.close()
        except Exception as e:
            pass
        return super(SslTcpSock, self).close()

    def shutdown(how = socket.SHUT_RDWR):
        pass

    @property
    def peer_cert(self):
        if self.sslsock is not None:
            return self.sslsock.get_peer_certificate()

    @property
    def peer_cert_chain(self):
        if self.sslsock is not None:
            return self.sslsock.get_peer_cert_chain()

    def recv(self, *args, **kwargs):
        raise RuntimeError("Invalid recv() call on SSL socket")

    def send(self, *args, **kwargs):
        raise RuntimeError("Invalid send() call on SSL socket")

    def allow_nonblock(self):
        import amncore.compat
        avail = (hasattr(self.sslsock, "setblocking") == True)
        if avail == True and amncore.compat.is_windows() == True:
            return True
        return False
        
class SslTcpServer(sockets.TcpServer, SecureSock):
    def __init__(self, *args, **kwargs):
        if hasattr(self, "sslctx") == False:
            self.sslctx = None
        return super(SslTcpServer, self).__init__(*args, **kwargs)

    @classmethod
    def create(self, **kwargs):
        kwargs['Proto'] = 'tcp'
        kwargs['Server'] = True
        kwargs['SSL'] = True
        return self.create_param(sockets.SocketParams.from_kwargs(**kwargs))

    @classmethod
    def create_param(self, param):
        param.proto = 'tcp'
        param.server = True
        param.ssl = True
        return sockets.create_param(param)

    def initsock(self, params = None):
        if params is not None and params.sslctx is not None and params.sslctx.__class__ == OpenSSL.SSL.Context:
            self.sslctx = params.sslctx
        else:
            self.sslctx = self.makessl(params)
        return super(SslTcpServer, self).initsock(params)

    def accept(self, **kwargs):
        try:
            r, _, _ = select.select([self.sock],[],[],0.5)
            if self.sock in r:
                _sock, addr = self.sock.accept()
            else:
                _sock = None
        except socket.error as e:
            _sock = None

        if _sock is None:
            return None

        try:
            ssl = OpenSSL.SSL.Connection(self.sslctx, _sock)
            ssl.set_accept_state()

            if self.allow_nonblock(ssl) == False:
                try:
                    ssl.setblocking(1)
                    ssl.do_handshake()
                except socket.timeout as e:
                    _sock.close()
                    raise OpenSSL.SSL.Error
            else:
                while True:
                    try:
                        ssl.setblocking(0)
                        ssl.do_handshake()
                        break
                    except OpenSSL.SSL.WantReadError as e:
                        select.select([ssl], [], [], 0.10)
                        continue
                    except OpenSSL.SSL.WantWriteError as e:
                        select.select([], [ssl], [], 0.10)
                        continue
                    except Exception as e:
                        raise e
    
            cls = SslTcpSock
            sock = cls(sock = _sock, sslsock = ssl)
            sock.sslctx = self.sslctx
            
            return sock
        except OpenSSL.SSL.Error as e:
            _sock.close()
            return None
            
def verify_cb(conn, cert, errno, depth, result):
    return True
