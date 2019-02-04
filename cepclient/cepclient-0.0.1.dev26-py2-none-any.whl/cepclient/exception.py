class CepException(Exception):
    '''Base exception class'''
    message = "An unknown exception occurred {content}"
    code = 500
    
    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs
        
        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass
        
        if not message:
            message = self.message.format(content = kwargs)
            
        super(CepException,self).__init__(message)
        
class UnsupportedService(CepException):
    '''Occurs if unsupported openstack service was requested.'''
    message = "Unsupported service requested."
    code = 406
    
class EPNotFound(CepException):
    '''Occurs if specific experiment precis not found.'''
    message = "Experiment precis not found."
    code = 404
    
class NoUniqueMatch(CepException):
    """Occurs if there are more than one appropriate eps."""
    message = "There is no unique requested ep."
    code = 409
    
class AuthenticationFailure(CepException):
    '''Occurs if authentication failed.'''
    message = "Unauthorized."
    code = 401
    
class InsufficientAuthInfomation(CepException):
    """Occurs if the auth info passed to cep client is insufficient."""
    message = "The passed arguments are insufficient for the authentication."
    code = 400
    
class UnsupportedArgument(CepException):
    '''Occurs if command line argument is unsupported.'''
    message = "Unsupported command line argument. Use '--help' for usage information."
    code = 406
