from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ccc.social_media.facebook.models import AccessToken
from ccc.social_media.social.utils import check_schedule_date_pass_test


class CreatePostAPIView(APIView):
    post_object_data = {}
    access_token = ''
    target_id = ''

    def initial(self, request, *args, **kwargs):
        media = list()
        # Collect all media files
        for key, item in self.request.FILES.items():
            media.append(item)
        self.post_object_data['title'] = self.request.data.get('title', None)
        self.post_object_data['message'] = self.request.data.get('message', None)
        self.post_object_data['location'] = self.request.data.get('location', None)
        self.post_object_data['schedule_date'] = self.request.data.get('schedule_date', None)

        # Check if the schedule date is in UNIX milliseconds
        if not check_schedule_date_pass_test(self.post_object_data['schedule_date']):
            return Response({'error': {'data': 'Invalid schedule date, date needs to be in UNIX milliseconds format!'}},
                            status=status.HTTP_400_BAD_REQUEST)

        self.post_object_data['link'] = self.request.data.get('link', None)
        self.post_object_data['media'] = media if not isinstance(media, list) else list(media)
        target_platform = self.request.data.get('target_platform', None)

        if target_platform is None:
            return Response({'error': {'data': 'You need to specify at least one target platform!'}},
                            status=status.HTTP_400_BAD_REQUEST)

        target_platform = target_platform.split('|')

        self.target_id = target_platform[1]
        # If no token was supplied from the front end, slot the user saved access token
        alt_token = AccessToken.objects.get(user=self.request.user)
        self.access_token = target_platform[2] if target_platform[2] else alt_token.token

        super(CreatePostAPIView, self).initial(request, *args, **kwargs)
