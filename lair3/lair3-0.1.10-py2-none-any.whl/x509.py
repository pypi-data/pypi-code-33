import OpenSSL, re

class X509Cert(object):
    def __init__(self):
        pass
        
    @classmethod
    def parse_pem(self, ssl_cert):
        cert = None
        key = None
        chain = None
        
        certs = []
        
        mach = re.findall(r'-----BEGIN\s*[^\-]+-----+\r?\n[^\-]*-----END\s*[^\-]+-----\r?\n?', ssl_cert)
        if mach is not None:
            for pem in mach:
                mach2 = re.search(r'PRIVATE KEY', pem)
                mach3 = re.search(r'CERTIFICATE', pem)
                
                if mach2 is not None:
                    key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, pem)
                elif mach3 is not None:
                    certs.append(OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pem))
        
        if len(certs) > 0:
            cert = certs.pop(0)
            chain = certs
            
        return [key, cert, chain]
        
    @classmethod
    def parse_pem_file(self, ssl_cert_file):
        data = ''
        fd = open(ssl_cert_file, 'rb')
        data = fd.read()
        fd.close()
        
        return self.parse_pem(data)

    @classmethod
    def get_cert_hash(self, ssl_cert):
        hcert = self.parse_pem(ssl_cert)
        
        if hcert is None or hcert[0] is None or hcert[1] is None:
            raise TypeError("Could not parse a private key and certificate")
            
        return hcert[1].digest('sha1')
        
    @classmethod
    def get_cert_file_hash(self, ssl_cert_file):
        data = ''
        fd = open(ssl_cert_file, 'rb')
        data = fd.read()
        fd.close()
        
        return self.get_cert_hash(data)