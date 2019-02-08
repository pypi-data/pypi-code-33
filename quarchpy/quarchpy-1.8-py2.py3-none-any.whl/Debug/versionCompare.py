import pkg_resources
import re

#LEGACY CODE
def versionCompare(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return cmp(normalize(version1), normalize(version2))

def getQuarchPyVersion ():
    return pkg_resources.get_distribution("quarchpy").version

def requiredQuarchpyVersion (requiredVersion):
    #for backwards compat with old scripts
    return True
    #return versionCompare (requiredVersion, getQuarchPyVersion())