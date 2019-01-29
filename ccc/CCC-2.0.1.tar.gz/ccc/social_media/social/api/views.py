from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from ccc.social_media.social.generics import CreatePostAPIView
from ccc.social_media.social.models import TARGET_PLATFORMS_FOR_POSTS, Post
from ccc.social_media.social.paginations import PostPagination
from ccc.social_media.social.serializers import PostSerializer
from ccc.social_media.social.utils import (create_local_version_post,
                                           handle_facebook_page_post)


class ListPostsLocal(ListAPIView):
    def get_queryset(self):
        posts = Post.objects.filter(user=self.request.user).order_by('-created')
        is_pending = self.request.GET.get('pending', None)
        if is_pending is not None:
            posts = posts.filter(schedule_date__gte=timezone.now())
        return posts

    serializer_class = PostSerializer
    pagination_class = PostPagination
    permission_classes = (IsAuthenticated,)


class CreateFacebookPost(CreatePostAPIView):
    def post(self, request, *args, **kwargs):
        response = handle_facebook_page_post(self.access_token, self.target_id, self.post_object_data)
        ref = response.data.get('id', None)

        if ref is not None:
            # Means the request was successful, it not, errors could be caused by duplicate or something
            # Create our own version of the Post and target
            create_local_version_post(self.request.user, self.post_object_data, TARGET_PLATFORMS_FOR_POSTS[0][0],
                                      self.target_id, ref)
        return response
