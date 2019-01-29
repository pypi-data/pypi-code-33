# import os
#
# from celery import shared_task
#
# from .models import *
#
#
# def handle_uploaded_file(video):
#     filename, extension = os.path.splitext(video.name)
#     # relative_path = "digital_assets/video/%s" % video.name
#     full_path = "media/digital_assets/video/%s" % video.name
#     with open(full_path, 'wb+') as destination:
#         for chunk in video.chunks():
#             destination.write(chunk)
#     return full_path
#
#
# @shared_task
# def save_attachment(attachment, user_id, attachment_name):
#     DigitalAttachment.objects.create(attachment=attachment, user_id=user_id, attachment_name=attachment_name)
#
#
# @shared_task
# def save_image(image, user_id, image_name):
#     DigitalImage.objects.create(image=image, user_id=user_id, image_name=image_name)
#
#
# @shared_task
# def save_audio(audio, user_id, audio_name):
#     DigitalAudio.objects.create(audio=audio, user_id=user_id, audio_name=audio_name)
#
#
# @shared_task
# def save_video(video, user_id, video_name):
#     video_path = handle_uploaded_file(video)
#     DigitalVideo.objects.create(video=video_path, user_id=user_id, video_name=video_name)
