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

import json
import stschema.utils.responseBuilder as responseBuilder
import stschema.state.CommandResponse as CommandResponse
import stschema.state.StateRefreshResponse as StateRefreshResponse
import stschema.discovery.DiscoveryResponse as DiscoveryResponse

def createResponse(schema, version, interactionType, requestId):
    if interactionType == "discoveryRequest":
        return DiscoveryResponse.DiscoveryResponse(schema, version, requestId);
    elif interactionType == "stateRefreshRequest":
        return StateRefreshResponse.StateRefreshResponse(schema, version, requestId);
    elif interactionType ==  "commandRequest":
        return CommandResponse.CommandResponse(schema, version, requestId);
    elif interactionType ==  "callbackRequest":
        return debug("callbackRequest is not yet implemented");
    else:
        return debug(interactionType + " is invalid");

def generateHandler(opts):
    def handler(event, context):
        try:
            schema = event["headers"]["schema"]
            version = event["headers"]["version"]
            interactionType = event["headers"]["interactionType"]
            requestId = event["headers"]["requestId"]
        except:
            return responseBuilder.badRequest(
                "undefined",
                "Failed to parse POST body"
            )

        if interactionType not in opts: # Check if interactionType is available
            return responseBuilder.badRequest(
                requestId,
                interactionType + " has not been implemented"
            )

        response = createResponse(schema, version, interactionType, requestId)

        if not response:
            return responseBuilder.badRequest(
                requestId,
                "Invalid request " + interactionType
            )

        try:
            opts[interactionType](event, response)
        except Exception as e:
            return responseBuilder.error(
                requestId,
                500,
                str(e),
                "Failed to make the request"
            )

        return responseBuilder.response(200, json.dumps(response.__dict__));

    return handler
