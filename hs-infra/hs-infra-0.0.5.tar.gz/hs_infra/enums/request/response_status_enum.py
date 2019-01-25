from enum import Enum


class ResponseStatusPacket:
    def __init__(self, code, message: str, status: str = "error"):
        super().__init__()
        self.code = code
        self.status = status
        self.message = message

    def __str__(self):
        str_ = "code: " + str(self.code) + ", status: " + str(self.status) + ", message: " + str(self.message)
        return str_


class ResponseStatusEnum(Enum):
    code_100 = ResponseStatusPacket(100, 'continue')
    code_101 = ResponseStatusPacket(101, 'switching_protocols')
    code_200 = ResponseStatusPacket(200, 'ok')
    code_201 = ResponseStatusPacket(201, 'created')
    code_202 = ResponseStatusPacket(202, 'accepted')
    code_203 = ResponseStatusPacket(203, 'non authoritative information')
    code_204 = ResponseStatusPacket(204, 'no content')
    code_205 = ResponseStatusPacket(205, 'reset content')
    code_206 = ResponseStatusPacket(206, 'partial content')
    code_207 = ResponseStatusPacket(207, 'multi status')
    code_300 = ResponseStatusPacket(300, 'multiple choices')
    code_301 = ResponseStatusPacket(301, 'moved permanently')
    code_302 = ResponseStatusPacket(302, 'found')
    code_303 = ResponseStatusPacket(303, 'see other')
    code_304 = ResponseStatusPacket(304, 'not modified')
    code_305 = ResponseStatusPacket(305, 'use proxy')
    code_306 = ResponseStatusPacket(306, 'reserved')
    code_307 = ResponseStatusPacket(307, 'temporary redirect')
    code_400 = ResponseStatusPacket(400, 'bad request')
    code_401 = ResponseStatusPacket(401, 'unauthorized')
    code_402 = ResponseStatusPacket(402, 'payment required')
    code_403 = ResponseStatusPacket(403, 'forbidden')
    code_404 = ResponseStatusPacket(404, 'not found')
    code_405 = ResponseStatusPacket(405, 'method not allowed')
    code_406 = ResponseStatusPacket(406, 'not acceptable')
    code_407 = ResponseStatusPacket(407, 'proxy authentication required')
    code_408 = ResponseStatusPacket(408, 'request timeout')
    code_409 = ResponseStatusPacket(409, 'conflict')
    code_410 = ResponseStatusPacket(410, 'gone')
    code_411 = ResponseStatusPacket(411, 'length required')
    code_412 = ResponseStatusPacket(412, 'precondition failed')
    code_413 = ResponseStatusPacket(413, 'request entity too large')
    code_414 = ResponseStatusPacket(414, 'request uri too long')
    code_415 = ResponseStatusPacket(415, 'unsupported media type')
    code_416 = ResponseStatusPacket(416, 'requested range_not satisfiable')
    code_417 = ResponseStatusPacket(417, 'expectation ailed')
    code_422 = ResponseStatusPacket(422, 'unprocessable entity')
    code_423 = ResponseStatusPacket(423, 'locked')
    code_424 = ResponseStatusPacket(424, 'failed dependency')
    code_428 = ResponseStatusPacket(428, 'precondition required')
    code_429 = ResponseStatusPacket(429, 'too many requests')
    code_431 = ResponseStatusPacket(431, 'request header fields too large')
    code_451 = ResponseStatusPacket(451, 'unavailable for legal reasons')
    code_500 = ResponseStatusPacket(500, 'internal server error')
    code_501 = ResponseStatusPacket(501, 'not implemented')
    code_502 = ResponseStatusPacket(502, 'bad gateway')
    code_503 = ResponseStatusPacket(503, 'service unavailable')
    code_504 = ResponseStatusPacket(504, 'gateway timeout')
    code_505 = ResponseStatusPacket(505, 'http version not supported')
    code_507 = ResponseStatusPacket(507, 'insufficient storage')
    code_511 = ResponseStatusPacket(511, 'network authentication required')
