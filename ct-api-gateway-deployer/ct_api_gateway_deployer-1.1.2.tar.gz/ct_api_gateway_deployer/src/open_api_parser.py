# -*- coding: utf-8 -*-
import json
import datetime

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

from ct_api_gateway_deployer.src.aws.aws_api_gateway import AWSApiGateway
from ct_api_gateway_deployer.src.common.utils import Utils


class OpenAPIParser():
    configuration = dict()

    def __init__(self, input_path: str, output_path: str, api_gateway: AWSApiGateway):
        """

        :param input_path: str
        :param output_path: str
        :param api_gateway: ct_api_gateway_deployer.src.aws.aws_api_gateway.AWSApiGateway
        """
        self._input_path = input_path
        self._output_path = output_path
        self._api_gateway = api_gateway
        self._configuration = {
            "openapi" : DoubleQuotedScalarString("3.0.1"),
            "info": {
                "title": DoubleQuotedScalarString(self._api_gateway.get_info_title()),
                "version": DoubleQuotedScalarString(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:SZ"))
            },
            "servers": [{
                "url": DoubleQuotedScalarString(self._api_gateway.get_servers_url()),
                "variables": {
                    "basePath": {
                        "default": DoubleQuotedScalarString(self._api_gateway.get_servers_url_variables_base_path_default())
                    }
                }
            }],
            "paths": {},
            "components": {
                "schemas": {
                    "Empty": {
                        "title": DoubleQuotedScalarString("Empty Schema"),
                        "type": DoubleQuotedScalarString("object")
                    }
                },
                "securitySchemes": {
                    "sigv4": {
                        "type": DoubleQuotedScalarString("apiKey"),
                        "name": DoubleQuotedScalarString("Authorization"),
                        "in": DoubleQuotedScalarString("header"),
                        "x-amazon-apigateway-authtype": DoubleQuotedScalarString("awsSigv4")
                    }
                }
            }
        }

    def get_configuration(self):
        return self._configuration

    def parse(self):
        with open(self._input_path, 'r') as routes_file:
            data = json.load(routes_file)

        for resource in data['blueprint']['resources']:
            for method in resource['methods']:
                # Add the method as a path in the configuration if it do not exists
                method_key = self.add_method(method=method)
                # Add Add actions to the method
                for action in method['actions']:
                    self.add_action(method_key=method_key, blueprint=data['blueprint'], method=method, action=action, cors=method['cors'])
                # Add method OPTION if CORS is enabled
                if method['cors']['enable']:
                    self.add_option_action(method_key=method_key, method=method)

    def add_method(self, method):
        key = Utils.mount_openapi_uri(method)
        key = DoubleQuotedScalarString(key)
        if key not in self._configuration['paths']:
            self._configuration['paths'].update({key: {}})
        return key

    def add_action(self, method_key, blueprint, method, action, cors):
        action_name = DoubleQuotedScalarString(action['type'].lower())

        # Add action
        self._configuration['paths'][method_key].update({action_name: {
            "responses": {
                200: {
                    "description": DoubleQuotedScalarString("200 response"),
                    "content": {
                        "application/json": {
                            "schema": {DoubleQuotedScalarString("$ref"): DoubleQuotedScalarString("#/components/schemas/Empty")}
                        }
                    }
                }
            },
            "security": []
        }})

        # Add authorization
        if action['authorization'] == 'AWS_IAM':
            self._configuration['paths'][method_key][action_name]["security"].append({"sigv4": []})

        # Add integration type for API Gateway
        self._configuration['paths'][method_key][action_name].update({
            'x-amazon-apigateway-integration': {
                'connectionId': DoubleQuotedScalarString(action['vpcLink']) if action['vpcLink'] is not None else '',
                'connectionType': DoubleQuotedScalarString(action['integration']),
                'httpMethod': DoubleQuotedScalarString(action['type']),
                'uri': DoubleQuotedScalarString(self._api_gateway.get_servers_url() + blueprint['name'] + method_key),
                'type': DoubleQuotedScalarString('HTTP_PROXY') if action['proxyIntegration'] else DoubleQuotedScalarString('HTTP'),
                'responses': {
                    DoubleQuotedScalarString("default"): {
                        "statusCode": "200",
                        "responseTemplates": {
                            "application/json": DoubleQuotedScalarString("#set ($root=$input.path('$')) { \"stage\": \"$root.name\", \"user-id\": \"$root.key\" }"),
                        }
                    }
                }
            }
        })

        if 'removeDefaultResponseTemplates' in cors and cors['removeDefaultResponseTemplates']:
            del(self._configuration['paths'][method_key][action_name]['x-amazon-apigateway-integration']['responses']['default']['responseTemplates'])

        # Add path parameters
        if method["queryParams"] and len(method["queryParams"]) > 0:
            self._configuration['paths'][method_key][action_name].update({'parameters': []})
            self._configuration['paths'][method_key][action_name]['x-amazon-apigateway-integration'].update({
                'requestParameters': {}
            })
            for parameter in method["queryParams"]:
                self._configuration['paths'][method_key][action_name]['parameters'].append(
                    {
                        'name': DoubleQuotedScalarString(parameter['name']),
                        'in': DoubleQuotedScalarString('path'),
                        'required': True,
                        'schema': {
                            'type': DoubleQuotedScalarString('string'),
                        }
                    })
                self._configuration['paths'][method_key][action_name]['x-amazon-apigateway-integration'][
                    'requestParameters'].update({
                    DoubleQuotedScalarString(
                        "integration.request.path." + parameter["name"]): DoubleQuotedScalarString(
                        "method.request.path." + parameter["name"])
                })

        if cors['enable']:
            self._configuration['paths'][method_key][action_name]['responses'][200].update({"headers": {
                "Access-Control-Allow-Origin": {
                    "schema": {
                        "type": DoubleQuotedScalarString("string")
                    }
                }
            }})
            self._configuration['paths'][method_key][action_name]['x-amazon-apigateway-integration']['responses']['default'].update({
                "responseParameters": {
                    "method.response.header.Access-Control-Allow-Origin": DoubleQuotedScalarString("'*'")
                }
            })

    def add_option_action(self, method_key, method):
        # Add allowHeaders
        allow_headers = "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"

        for header in method['cors']['allowHeaders']:
            allow_headers = allow_headers + ',' + header

        self._configuration['paths'][method_key].update({
            'options': {
                'summary': DoubleQuotedScalarString('CORS support'),
                'description': DoubleQuotedScalarString('Enable CORS by returning correct headers'),
                'tags': [DoubleQuotedScalarString('CORS')],
                'x-amazon-apigateway-integration': {
                    'type': DoubleQuotedScalarString('mock'),
                    'passthroughBehavior': DoubleQuotedScalarString("when_no_match"),
                    'requestTemplates': {
                        'application/json': DoubleQuotedScalarString("{\"statusCode\": 200}")
                    },
                    'responses': {
                        DoubleQuotedScalarString("default"): {
                            "statusCode": DoubleQuotedScalarString(200),
                            "responseParameters": {
                                "method.response.header.Access-Control-Allow-Headers" : DoubleQuotedScalarString("'"+allow_headers+"'"),
                                "method.response.header.Access-Control-Allow-Methods": DoubleQuotedScalarString("'*'"),
                                "method.response.header.Access-Control-Allow-Origin": DoubleQuotedScalarString("'*'"),
                            }
                        }
                    }
                },
                'responses': {
                    200: {
                        "description": DoubleQuotedScalarString("Default response for CORS method"),
                        "headers": {
                            "Access-Control-Allow-Origin": {
                                "schema": {
                                    "type": DoubleQuotedScalarString("string")
                                }
                            },
                            "Access-Control-Allow-Methods": {
                                "schema": {
                                    "type": DoubleQuotedScalarString("string")
                                }
                            },
                            "Access-Control-Allow-Headers": {
                                "schema": {
                                    "type": DoubleQuotedScalarString("string")
                                }
                            }
                        },
                        "content": {
                            "application/json": {
                                "schema": {DoubleQuotedScalarString("$ref"): DoubleQuotedScalarString("#/components/schemas/Empty")}
                            }
                        }
                    }
                }
            }
        })

    def flush(self):
        yaml = YAML()
        with open(self._output_path, 'w') as outfile:
            yaml.dump(self._configuration, outfile)
        return True
