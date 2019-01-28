#! /usr/bin/python3

import argparse
import json
import re

import docker

TEMP_TAG = 'temp'


def parse_args(sys_args: list = None):
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--file', help='Dockerfile to be built. [%(default)s]', default='Dockerfile')
    argparser.add_argument('-c', '--context', help='Docker build context directory. [%(default)s]', default='.')
    argparser.add_argument('-i', '--image', help='DEPRECATED: use --context instead', default='.', dest='context')
    argparser.add_argument('-n', '--name', help='Image base name', required=True)
    argparser.add_argument('-t', '--tags', nargs='+', help='Tags to add to built image.', default=[])
    argparser.add_argument('--no-cache', help='Don\'t use cache when building.', action='store_true')
    argparser.add_argument('--no-push', help='Don\'t push added tags to Docker Hub.', action='store_true')
    return argparser.parse_args(sys_args)


def build(client, args):
    print('\n==== BUILDING ====\n')

    # We're using the low-level API client to get a continuous stream of messages
    tag_name = f'{args.name}:{TEMP_TAG}'

    generator = client.build(
        path=args.context,
        dockerfile=args.file,
        tag=tag_name,
        rm=True,
        nocache=args.no_cache)

    while True:
        try:
            output = next(generator).rstrip()
            json_output = json.loads(output)
            if 'stream' in json_output:
                print(json_output['stream'].rstrip(), flush=True)
        except StopIteration:
            print('Docker image build complete.')
            break
        except ValueError:
            print(f'Error parsing output from docker image build: {output}')


def deploy(client, args):
    if args.tags:
        print('\n==== DEPLOYING ====\n')

    for tag in args.tags:
        # Filter out illegal tag characters
        tag = re.sub('[/_:]', '-', tag)
        print(f'Tagging {args.name}:{tag}')
        client.tag(f'{args.name}:{TEMP_TAG}', repository=args.name, tag=tag)

        if args.no_push:
            continue

        print(f'Pushing {args.name}:{tag}')
        for line in client.push(repository=args.name, tag=tag, stream=True):
            output = line.rstrip()
            json_output = json.loads(output)
            msg = ' '.join([str(v) for v in json_output.values()])
            print(msg, flush=True)


def main(sys_args: list = None):
    args = parse_args(sys_args)
    print('+'*20, 'Deploy Docker Image', '+'*20)
    print(args)
    docker_client = docker.APIClient()

    build(docker_client, args)
    deploy(docker_client, args)


if __name__ == '__main__':
    main()
