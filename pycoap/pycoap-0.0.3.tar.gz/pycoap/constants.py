
COAP_VERSION = 1

ACK_TIMEOUT_MIN = 2
ACK_MAX_RANDOM_FACTOR = 1.5
MAX_RETRANSMITS = 4
MESSAGE_MAX_TRANSMIT_WAIT = 30  # 30 Seconds - Max to continue retransmitting before giving up
MSG_EXCHANGE_LIFETIME = 300   # 300 Seconds - Time to remember message ids for duplicate detection

REQUEST_TIMEOUT = 46 # seconds request will wait for a 

COAP_DEFAULT_PORT = 5683
COAPS_DEFAULT_PORT = 5684
MAX_PAYLOAD_SIZE = 1024


# Coap Message Types
MESSAGE_TYPE_CON = 0
MESSAGE_TYPE_NONCON = 1
MESSAGE_TYPE_ACK = 2
MESSAGE_TYPE_RESET = 3

# Coap code values
CODE_CLASS_REQUEST = 0
CODE_CLASS_SUCCESS = 2
CODE_CLASS_CLIENT_ERROR = 4
CODE_CLASS_SERVER_ERROR = 5

# Coap code values
CODE_EMPTY = 0x00
CODE_GET = 0x01
CODE_POST = 0x02
CODE_PUT = 0x03
CODE_DELETE = 0x04

CODE_CREATED = 0x41
CODE_DELETED = 0x42
CODE_VALID = 0x43
CODE_CHANGED = 0x44
CODE_CONTENT = 0x45
CODE_CONTINUE = 0x5F

CODE_BAD_REQUEST = 0x80
CODE_UNAUTHORIZED = 0x81
CODE_BAD_OPTION = 0x82
CODE_FORBIDDEN = 0x83
CODE_NOT_FOUND = 0x84
CODE_METHOD_NOT_ALLOWED = 0x85
CODE_NOT_ACCEPTABLE = 0x86
CODE_PRECONDITION_FAILED = 0x8C
CODE_REQUEST_ENTITY_TOO_LARGE = 0x8D
CODE_UNSUPPORTED_CONTENT_FORMAT = 0x8F

CODE_INTERNAL_ERROR = 0xA0
CODE_NOT_IMPLIMENTED = 0xA1
CODE_BAD_GATEWAY = 0xA2
CODE_SERVICE_UNAVAILABLE = 0xA3
CODE_GATEWAY_TIMEOUT = 0xA4
CODE_PROXYING_NOT_SUPPORTED = 0xA5


CODE_ERROR_DNS = 0xC1  # NOT A STANDARD COAP CODE
CODE_ERROR_TIMEOUT = 0xC2  # NOT A STANDARD COAP CODE
CODE_ERROR_PACKET_ORDER = 0xC3  # NOT A STANDARD COAP CODE
CODE_ERROR_RESET = 0xC4 # NOT A STANDARD COAP CODE
CODE_ERROR_MAX_RETRY = 0xC5 # NOT A STANDARD COAP CODE

CODE__MAP = {
    CODE_EMPTY:"Ping",
    CODE_GET:"GET Request",
    CODE_POST:"POST Request",
    CODE_PUT:"PUT Request",
    CODE_DELETE:"DELETE Request",

    CODE_CREATED:"Success - Created",
    CODE_DELETED:"Success - Deleted",
    CODE_VALID:"Success - Valid",
    CODE_CHANGED:"Success - Changed",
    CODE_CONTENT:"Success - Content",
    CODE_CONTINUE:"Continue",

    CODE_BAD_REQUEST:"Client Error - Bad Request",
    CODE_UNAUTHORIZED:"Client Error - Unauthorized",
    CODE_BAD_OPTION:"Client Error - Bad Option",
    CODE_FORBIDDEN:"Client Error - Forbidden",
    CODE_NOT_FOUND:"Client Error - Not Found",
    CODE_METHOD_NOT_ALLOWED:"Client Error - Method Not Allowed",
    CODE_NOT_ACCEPTABLE:"Client Error - Not Acceptable",
    CODE_PRECONDITION_FAILED:"Client Error - Precondition Failed",
    CODE_REQUEST_ENTITY_TOO_LARGE:"Client Error - Request Entity Too Large",
    CODE_UNSUPPORTED_CONTENT_FORMAT:"Client Error - Unsupported Content-Format",

    CODE_INTERNAL_ERROR:"Server Error - Internal Server Error",
    CODE_NOT_IMPLIMENTED:"Server Error - Not Implemented",
    CODE_BAD_GATEWAY:"Server Error - Bad Gateway",
    CODE_SERVICE_UNAVAILABLE:"Server Error - Service Unavailable",
    CODE_GATEWAY_TIMEOUT:"Server Error - Gateway Timeout",
    CODE_PROXYING_NOT_SUPPORTED:"Server Error - Proxying Not Supported",

    CODE_ERROR_DNS:"Connection Error - DNS Failed",
    CODE_ERROR_TIMEOUT:"Connection Error - Timed Out",
    CODE_ERROR_PACKET_ORDER:"Connection Error - Packets arrived out of order",
    CODE_ERROR_RESET:"Connection Error - RESET Packet Received",
    CODE_ERROR_MAX_RETRY:"Connection Error - Max retries reached without receiving Ack"
    }


#Error Messages
ERROR_DNS = 1
ERROR_TIMEOUT = 2
ERROR_PACKET_ORDER = 3
ERROR_RESET = 4
ERROR_MAX_RETRY = 5

ERROR_MAP = {
    ERROR_DNS:"DNS resolution error",
    ERROR_TIMEOUT:"Response timeout error",
    ERROR_PACKET_ORDER:"Packets arrived out of order",
    ERROR_RESET:"RESET packet received",
    ERROR_MAX_RETRY:"Maximum retry count exceeded"
}


# Alternative constant for Code requests
METHOD_GET = CODE_GET
METHOD_POST = CODE_POST
METHOD_PUT = CODE_PUT
METHOD_DELETE = CODE_DELETE

# Coap Option Numbers
OPTION_NUMBER_URI_HOST = 3
OPTION_NUMBER_ETAG = 4
OPTION_NUMBER_OBSERVE = 6
OPTION_NUMBER_URI_PORT = 7
OPTION_NUMBER_URI_PATH = 11
OPTION_NUMBER_CONTENT_FORMAT = 12
OPTION_NUMBER_URI_QUERY = 15
OPTION_NUMBER_ACCEPT_FORMAT = 17
OPTION_NUMBER_BLOCK2 = 23
OPTION_NUMBER_BLOCK1 = 27

# Coap Content formats
FORMAT_TEXT = 0         # 0x00
FORMAT_LINK = 40        # 0x28
FORMAT_XML = 41         # 0x29
FORMAT_OCTECT = 42      # 0x2A
FORMAT_EXI = 47         # 0x2F
FORMAT_JSON = 50        # 0x32

FORMAT__MAP = {
    FORMAT_TEXT:"text/plain charset=utf-8",
    FORMAT_LINK:"application/link-format",
    FORMAT_XML:"application/xml",
    FORMAT_OCTECT:"application/octet-stream",
    FORMAT_EXI:"application/exi",
    FORMAT_JSON:"application/json",
    }


OBSERVE_REGISTER = 0
OBSERVE_DEREGISTER = 1