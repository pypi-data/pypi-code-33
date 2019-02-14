"""
operatorcourier.courier_api module

This module implements the api that should be imported when using the operator-courier package
"""

from operatorcourier.build import BuildCmd
from operatorcourier.validate import ValidateCmd
from operatorcourier.push import PushCmd
import os
import yaml

def build_and_verify(source_dir="", files=""):
    """Build and verify constructs an operator bundle from a set of files then verifies it for usefulness and accuracy.
    It returns the bundle as a string.

    :param source_dir: Path to local directory of yaml files to be read.
    :param files: Comma delimited string of files to create bundle with.
    """

    yamls = []

    for filename in os.listdir(source_dir):
        if filename.endswith(".yaml"):
            with open(source_dir + "/" + filename) as f:
                yamls.append(f.read())
    

    bundle = BuildCmd().build_bundle(yamls)

    #ValidateCmd().validate()

    #TODO: This return statement should return the bundle.
    return bundle

def build_verify_and_push(namespace, repository, revision, token, source_dir="", files=""):
    """Build verify and push constructs the operator bundle, verifies it, and pushes it to an external app registry.
    Currently the only supported app registry is the one located at Quay.io (https://quay.io/cnr/api/v1/packages/)

    :param namespace: Quay namespace where the repository we are pushing the bundle is located.
    :param repository: Application repository name the application is bundled for.
    :param revision: Release version of the bundle.
    :param source_dir: Path to local directory of yaml files to be read
    :param files: Comma delimited string of files to create bundle with
    """
    
    bundle = build_and_verify(source_dir, files)

    if not os.path.exists("./tempdir"):
        os.makedirs("./tempdir")

    with open('./tempdir/bundle.0.0.1.yaml', 'w') as outfile:
        yaml.dump(bundle, outfile, default_flow_style=False)

    PushCmd().push("./tempdir", namespace, repository, revision, get_token())

    



























def get_token():
    return "basic YWdyZWVuZTpIdXNraWVzMjAxNSE="