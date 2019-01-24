import json
import urllib

class Travis(GitHubAuthentication):

    def __init__(self, token):
        super(Travis, self).__init__(None, token)

    def _getNextURL(self, resp):
        jsonResp = json.loads(resp.text)
        if (not '@pagination' in jsonResp):
            return None
        if (not 'next' in jsonResp['@pagination']):
            return None
        if (not '@href' in jsonResp['@pagination']['next']):
            return None
        return jsonResp['@pagination']['next']['href']

    def _processResp(self, resp):   
        if (resp is None):
            return None
        return json.loads(resp)

    def getBuilds(self, repoSlug):
        encodedSlug = urllib.quote_plus(repoSlug)
        return self.genericApiCall("api.travis-ci.com", "/repos/" + encodedSlug + "/builds")
