import os
from skitai import was as the_was
from hashlib import md5
from aquests.protocols.http import http_util
import base64

class AuthorizedUser:
    def __init__ (self, user, realm, info = None):
        self.name = user
        self.realm = realm
        self.info = info
    
    def __str__ (self):
        return self.name
        

class WWWAuth:
    realm = "App"
    users = {}    
    opaque = None
    
    # high level API with skitai----------------------------------------------    
    def get_www_authenticate (self, authenticate, error = None):
        if authenticate == "bearer":
            return 'Bearer realm="{}"{}'.format (self.realm, error and ', error="%s"' % error or '')        
        elif authenticate == "basic":
            return 'Basic realm="%s"' % self.realm
        else:    
            if self.opaque is None:
                self.opaque = md5 (self.realm.encode ("utf8")).hexdigest ()
            return 'Digest realm="%s", qop="auth", nonce="%s", opaque="%s"' % (
                self.realm, http_util.md5uniqid (), self.opaque
            )
            
    def get_user (self, username):
        # return string password, bool encrypted, object userinfo 
        handler = self._decos.get ("auth_handler")
        if handler:
            info = handler (the_was._get (), username)
        else:        
            info = self.users.get (username)
        if not info:
            return None, 0, None # passwrod, encrypted
        return type (info) is str and (info, 0, None) or info
                
    def authorize (self, auth, method, uri, authenticate):
        if auth is None:
            return self.get_www_authenticate (authenticate)
        
        # check validate: https://evertpot.com/223/
        amethod, authinfo = auth.split (" ", 1)
        if amethod.lower () != authenticate:
            return self.get_www_authenticate (authenticate)
        
        if authenticate == "bearer":
            was = the_was._get ()
            error = self._decos ["bearer_handler"] (was, authinfo)
            if error:
                return self.get_www_authenticate (authenticate, error)
            try:
                return was.request.user
            except AttributeError:
                return "authorized-anon"
            
        elif authenticate == "basic":
            basic = base64.decodestring (authinfo.encode ("utf8")).decode ("utf8")
            current_user, current_password = basic.split (":", 1)
            password, encrypted, userinfo = self.get_user (current_user)
            if not password:
                return self.get_www_authenticate (authenticate)
            if encrypted:
                raise AssertionError ("Basic authorization can't handle encrypted password")
            if password ==  current_password:
                return AuthorizedUser (current_user, self.realm, userinfo)
                
        elif authenticate == "digest":
            method = method.upper ()
            infod = {}
            for info in authinfo.split (","):
                k, v = info.strip ().split ("=", 1)
                if not v: return self.get_www_authenticate (authenticate)
                if v[0] == '"': v = v [1:-1]
                infod [k]     = v
            
            current_user = infod.get ("username")
            if not current_user:
                return self.get_www_authenticate (authenticate)
            
            password, encrypted, userinfo = self.get_user (current_user)
            if not password:
                return self.get_www_authenticate (authenticate)
                
            try:
                if uri != infod ["uri"]:                    
                    return self.get_www_authenticate (authenticate)
                if encrypted:    
                    A1 = password
                else:
                    A1 = md5 (("%s:%s:%s" % (infod ["username"], self.realm, password)).encode ("utf8")).hexdigest ()
                A2 = md5 (("%s:%s" % (method, infod ["uri"])).encode ("utf8")).hexdigest ()
                Hash = md5 (("%s:%s:%s:%s:%s:%s" % (
                    A1, 
                    infod ["nonce"],
                    infod ["nc"],
                    infod ["cnonce"],
                    infod ["qop"],
                    A2
                    )).encode ("utf8")
                ).hexdigest ()

                if Hash == infod ["response"]:
                    return AuthorizedUser (current_user, self.realm, userinfo)
                    
            except KeyError:
                pass
            
        return self.get_www_authenticate (authenticate)
    
    def is_allowed_origin (self, request, allowed_origins):
        origin = request.get_header ('Origin')
        if not origin:
            return True
        if not allowed_origins:
            allowed_origins = ["%s://%s" % (request.get_scheme (), request.get_header ("host", ""))]
        elif "*" in allowed_origins:
            return True    
        if origin in allowed_origins:
            return True
        return False
        
    def is_authorized (self, request, authenticate):
        if not authenticate:
            return True
        www_authenticate = self.authorize (request.get_header ("Authorization"), request.command, request.uri, authenticate)
        if type (www_authenticate) is str:
            request.response.set_header ('WWW-Authenticate', www_authenticate)
            return False
        elif www_authenticate:
            request.user = www_authenticate                
        return True
    
    