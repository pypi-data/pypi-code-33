import datetime

import pytz
from django.conf import settings

from ccc.social_media.facebook.api.utils import GraphAPI
from ccc.social_media.facebook.utils import add_query_param_to_url
from ccc.social_media.social.models import Post, PostedTo


def create_local_version_post(user, post, target, target_id, ref):
    content = post['message']
    location = post['location']

    schedule_date = None
    media = None

    if post['schedule_date'] is not None:
        schedule_date = datetime.datetime.fromtimestamp(int(post['schedule_date']),
                                                        tz=pytz.timezone(user.time_zone or settings.TIME_ZONE))
    if len(post['media']) > 0:
        media = post['media'][0]

    post_object, created = Post.objects.get_or_create(user=user, content=content, location=location,
                                                      schedule_date=schedule_date,
                                                      media=media)

    PostedTo.objects.create(post_id=post_object.id, target=target,
                            target_id=target_id, target_link='http://facebook.com/' + ref)


def check_schedule_date_pass_test(schedule_date):
    if schedule_date is not None:
        try:
            int(schedule_date)
            return True
        except ValueError:
            return False
    return True


def handle_facebook_page_post(access_token, page_id, post_object):
    """Post will contain 'media', 'message', 'schedule_date', 'link'"""
    data = dict()

    link = post_object['link']
    title = post_object['title']
    message = post_object['message']
    schedule_date = post_object['schedule_date']
    location = post_object['location']
    # if there is no message body, maybe the use is intending to post images or videos,then publish it,
    # if message body, dont publish
    photos, photo_ids = list(), list()
    videos, video_ids = list(), list()
    for media in post_object['media']:
        file_type = media.content_type
        if 'image' in file_type:
            photos.append(media)
        elif 'video' in file_type:
            videos.append(media)
        else:
            raise Exception('File type invalid')

    def post_videos(videos_):
        # re initialize, because we are publishing videos directly
        graph_ = GraphAPI(access_token)
        extra_payload = dict()
        if title:
            extra_payload.update({'title': title})
        if message:
            extra_payload.update({'description': message})
        if location:
            extra_payload.update({'place': {'id': location}})
        if schedule_date:
            extra_payload.update({'published': 'false', 'scheduled_publish_time': schedule_date})
        global resp
        for video_ in videos_:
            resp = graph_.get_ep(page_id + '/videos', method='POST', json=extra_payload, files={'source': video_})
            if resp.data.get('id', None) is not None:
                video_ids.append(resp.data['id'])
        if videos_:
            return resp
        return None

    def post_photos(photos_):
        # re initialize, because we are publishing videos directly
        graph_ = GraphAPI(access_token)
        extra_payload = dict()
        if message:
            extra_payload.update({'published': 'false'})
            if schedule_date:
                extra_payload.update({'scheduled_publish_time': 'schedule_date'})
        if location:
            extra_payload.update({'place': {'id': location}})
        if message and schedule_date:
            # Facebook asks that this be added if photo is going to be used in a post
            extra_payload.update({'temporary': 'true'})
        global resp
        for photo_ in photos_:
            resp = graph_.get_ep(page_id + '/photos', method='POST', data=extra_payload, files={'file': photo_})
            if resp.data.get('id', None) is not None:
                photo_ids.append(resp.data['id'])
        if not message and photos_:
            return resp
        return None

    resp_p = post_photos(photos)
    resp_v = post_videos(videos)

    # Return if it's a post that is independent(video)
    if resp_p or resp_v:
        return resp_p or resp_v

    # Graph API is being re-initialized here so we can reset the URL for the post
    graph = GraphAPI(access_token)
    if link:
        graph.url = add_query_param_to_url(graph.url, {'link': link}, encode_params=True)
    if message:
        graph.url = add_query_param_to_url(graph.url, {'message': message}, encode_params=True)
    if schedule_date:
        graph.url = add_query_param_to_url(graph.url, {'scheduled_publish_time': post_object['schedule_date'],
                                                       'published': 'false'})
    # If place is attached, add it to the post
    if location:
        data.update({'place': {'id': location}})
    if len(photo_ids) > 0:
        if schedule_date:
            data.update({'unpublished_content_type': 'SCHEDULED'})
        # If images were uploaded, then attach the IDs to the post
        for index, img_id in enumerate(photo_ids):
            data.update({'attached_media[' + str(index) + ']': '{"media_fbid": "' + img_id + '"}'})
    response = graph.get_ep(page_id + '/feed', method='POST', data=data)
    return response
