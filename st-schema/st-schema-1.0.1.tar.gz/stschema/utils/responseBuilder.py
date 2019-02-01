#
#	Copyright 2019 SmartThings
#
#	Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
#	in compliance with the License. You may obtain a copy of the License at:
#
#		http://www.apache.org/licenses/LICENSE-2.0
#
#	Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
#	on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License
#	for the specific language governing permissions and limitations under the License.
#

import json, ast
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def response(statusCode, payload = {}):
    response = ast.literal_eval(payload)
    logger.info('Response: {}'.format(payload))
    return response

def error(requestId, message, statusCode = 500, code = "InternalServiceError"):
    response = {
        "statusCode": statusCode,
        "body": {
            "requestId": requestId,
            "error": {
                "code": code,
                "message": message
            }
        }
    }
    return response

def badParamError(badParam, requestId):
    responseMessage = "Path or query parameter " + badParam + " is missing or empty"
    return badRequest(requestId, responseMessage)

def badRequest(requestId, message):
    return error(requestId, message, 400, "Bad Request")
