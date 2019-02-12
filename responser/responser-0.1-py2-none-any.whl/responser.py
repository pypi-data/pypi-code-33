# CONSTANTS and GLOBAL_VARIABLES
DEBUG = True 

def exception_response(exception):
	'''
	Takes an exception and returns a JSON Response containing error details
	'''
	
	response = {}
	response['status_code'] = 500

	if DEBUG:
		response['data'] = {
			'exception_type': exception.__class__.__name__,
			'exception_message': str(exception),
			'exception_description': exception.__doc__
		}
	else:
		response['data'] = 'Error occured during execution.'

	return response


def regularize_response(response):
	'''
	Regularise different types of data returned under the common key data of a JSON Response
	'''

	ALLOWED_DATA_TYPES = (
		int,
		str,
		list,
		tuple,
		float,
	)

	if isinstance(response, ALLOWED_DATA_TYPES):
		response = {'data': response}

	if isinstance(response, dict):
		if 'status_code' not in response:
			if 'data' not in response:
				response = {'data': response}
			response['status_code'] = 200
	else:
		try:
			err_msg = "View returned %s, which is not convertable to JSON"
			assert isinstance(response, dict), err_msg % type(
				response).__name__
		except Exception as e:
			response = exception_response(e)

	return response


def JSONResponser(status_code=400, data=None, message=None, strict_mode=False):
	
	HTTP_MESSAGES = {
		"100" : "Continue",
		"101" : "Switching Protocols",
		"200" : "OK",
		"201" : "Created",
		"202" : "Accepted",
		"203" : "Non-Authoritative Information",
		"204" : "No Content",
		"205" : "Reset Content",
		"206" : "Partial Content",
		"300" : "Multiple Choices",
		"301" : "Moved Permanently",
		"302" : "Found",
		"303" : "See Other",
		"304" : "Not Modified",
		"305" : "Use Proxy",
		"307" : "Temporary Redirect",
		"400" : "Bad Request",
		"401" : "Unauthorized",
		"402" : "Payment Required",
		"403" : "Forbidden",
		"404" : "Not Found",
		"405" : "Method Not Allowed",
		"406" : "Not Acceptable",
		"407" : "Proxy Authentication Required",
		"408" : "Request Time-out",
		"409" : "Conflict",
		"410" : "Gone",
		"411" : "Length Required",
		"412" : "Precondition Failed",
		"413" : "Request Entity Too Large",
		"414" : "Request-URI Too Large",
		"415" : "Unsupported Media Type",
		"416" : "Requested range not satisfiable",
		"417" : "Expectation Failed",
		"500" : "Internal Server Error",
		"501" : "Not Implemented",
		"502" : "Bad Gateway",
		"503" : "Service Unavailable",
		"504" : "Gateway Time-out",
		"505" : "HTTP Version not supported",
	}

	if(data==None):
		data = ""

	if(message==None):
		message = ""

	response = {
		"status_code": "400",
		"data": HTTP_MESSAGES.get("400"),
		"message": message
	}

	try:
		if(str(status_code) in HTTP_MESSAGES):
			response = {
				"status_code": status_code,
				"data": HTTP_MESSAGES.get(str(status_code)),
				"message": HTTP_MESSAGES.get(str(status_code))
			}
		else:
			response = {
				"status_code": status_code,
				"data": "",
				"message": message
			}

		if(strict_mode):
			response["data"] = data
		else:
			if(data!=None and data):
				response["data"] = data

		if(message!=None and message):
			response["message"] = message

		return response


	except Exception as e:
		response = {
			"status_code": "500",
			"data": HTTP_MESSAGES.get("500"),
			"message": e
		}

		return response


def JSONResponserDecorator(view):
	'''
	Converts any data returned by a function into a JSON Response format.
	'''

	def wrapper(*args, **kwargs):

		try:
			response = view(*args, **kwargs)
		except Exception as e:
			response = exception_response(e)

		response = regularize_response(response)
		response = JSONResponser(response['status_code'], response['data'])
		return response

	return wrapper
