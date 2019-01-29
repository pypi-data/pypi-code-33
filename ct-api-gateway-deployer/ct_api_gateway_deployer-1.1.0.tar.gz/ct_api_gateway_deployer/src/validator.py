# -*- coding: utf-8 -*-
import argparse


class Validator:

    @staticmethod
    def args_validator():
        parser = argparse.ArgumentParser("ct-api-gateway-deployer")
        parser.add_argument("--routes", nargs=1, type=str, required=True,
                            help="JSON file with the Flask resources routes")
        parser.add_argument("--aws-config", nargs=1, type=str, required=True,
                            help="JSON file with the AWS configurations")
        parser.add_argument("--output-openapifile-path", nargs=1, type=str, required=False, default=['swagger.yml'],
                            help="Path to export the OpenAPI file created in the processs. "
                                 "By default, the processe will create the 'swagger.yml' file.",
                            )
        parser.add_argument("--keep-output-openapifile", nargs=1, type=bool, required=False, default=False,
                            help="Boolean flag to keep the OpenAPI file generated in the process. "
                                 "By default, the file is erased at the end of the process.",
                            )
        return parser.parse_args()