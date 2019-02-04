from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .exceptions import bitbucket_service_exception_to_api
from .projects import BitbucketProjects
from .repos import BitbucketRepos


class BitbucketProjectsView(APIView):
    get_request_serializer_class = serializers.BitbucketProjectsRequest
    get_response_serializer_class = serializers.BitbucketProjectsResponse

    def get(self, request):
        request_params = request.query_params.dict()

        serializer = self.get_request_serializer_class(data=request_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        with bitbucket_service_exception_to_api():
            resp = BitbucketProjects(**validated_data).get_projects()

        return Response(data=self.get_response_serializer_class(resp).data)


class BitbucketReposView(APIView):
    get_request_serializer_class = serializers.BitbucketReposRequest
    get_response_serializer_class = serializers.BitbucketReposResponse

    def get(self, request, project_id):
        request_params = request.query_params.dict()
        request_params['project_id'] = project_id

        serializer = self.get_request_serializer_class(data=request_params)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        with bitbucket_service_exception_to_api():
            resp = BitbucketRepos(**validated_data).get_repos()

        return Response(data=self.get_response_serializer_class(resp).data)


class BitbucketRepoView(APIView):
    def get(self, request, project_id, repo_name=None):
        # TODO implement view to retrieve specific repo information
        return Response()
