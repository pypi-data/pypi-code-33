import base64
import json

from . import core

l = core.l


# Publish function from $Latest. If desired alias already exists, update its version. If not, create it.
# Assumes by default that the latest version of code is already in $latest via lambdev.test()
def publish(alias, description='', upload=False):
    if upload:
        core.upload_package()

    fn = core.get_function_name()

    pubresponse = l.publish_version(FunctionName=fn)

    if core.alias_exists(l.list_aliases(FunctionName=fn), alias):
        print('- Alias already exists. Updating version...')
        aliasresponse = l.update_alias(FunctionName=core.get_function_name(),
                                       Name=alias,
                                       FunctionVersion=pubresponse['Version'])
        print('- Alias {} updated to version {}'.format(aliasresponse['Name'],
                                                  aliasresponse['FunctionVersion']))
    else:
        print('- Creating new alias: {}...'.format(alias))
        l.create_alias(FunctionName=fn,
                       Name=alias,
                       FunctionVersion=pubresponse['Version'],
                       Description=description)


def test(test_object):
    core.upload_package()

    print("- Testing...")
    response = l.invoke(FunctionName=core.get_function_name(), InvocationType='RequestResponse',
                        LogType='Tail', Payload=json.dumps(test_object))

    print(u'- Function log:\n{}'.format(base64.b64decode(response['LogResult']).decode('utf-8')))

    if 'functionError' in response:
        raise(Exception('~~FUNCTION ERROR~~ {}'.format(json.loads(response['payload'].read().decode('utf-8')))))
    else:
        return json.loads(response['Payload'].read().decode('utf-8'))


def create_function(function_name=None, role=None, handler=None, description=None, runtime='python3.7'):
    x = core.ProjectFolder(core.workingDir)
    print('- Creating function...')
    response = l.create_function(FunctionName=function_name,
                                 Runtime=runtime,
                                 Role=role,
                                 Handler=handler,
                                 Code={'ZipFile': x.build_zip()},
                                 Description=description,
                                 Publish=False
                                 )

    with open(core.workingDir + '/function_name.txt', 'w') as f:
        f.write(response['FunctionArn'])

    print('- Function Created')
