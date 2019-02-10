import requests
from .amara_video import AmaraVideo
from .exceptions import AmaraApiException


class AmaraTools:

    def __init__(self, headers):
        self.headers = headers

    def get_amara_id(self, video_id):
        self.video_url = "http://www.youtube.com/watch?v=" + video_id
        url = 'https://amara.org/api/videos/'
        urldict = dict({'video_url': self.video_url})
        r = requests.get(url, params=urldict, headers=self.headers)
        json_ret = r.json()

        if 'objects' in json_ret and len(json_ret['objects']) > 0:
            amara_id = json_ret['objects'][0]['id']
            return amara_id
        else:
            return None

    def post_video(self, video_url, language_code):
        url = 'https://amara.org/api/videos/'
        urldict = dict({'video_url': video_url, 'primary_audio_language_code': language_code})

        r = requests.post(url, data=urldict, headers=self.headers)
        json_ret = r.json()
        if 'id' in json_ret:
            return json_ret['id']
        else:
            return None

    def retrieve_video(self, video_id):
        amara_id = self.get_amara_id(video_id)
        if (amara_id):
            amara_video = AmaraVideo(self.headers, amara_id)
            return amara_video
        else:
            return None

    def retrieve_or_create_video(self, video_id, languageCode):
        amara_video = self.retrieve_video(video_id)
        if (amara_video):
            return amara_video
        else:
            amara_id = self.post_video(video_id, languageCode)
            if (amara_id):
                amara_video = AmaraVideo(self.headers, amara_id)
                return amara_video
            else:
                return None

    def convert_to_lyrics(self, lines):
        ret_value = ""
        rows_t = lines.split('\n')
        rows = [x for x in rows_t if len(x.strip()) > 0]
        for count, row in enumerate(rows):
            ret_value = ret_value + str(count + 1) + '\r\n'
            ret_value = ret_value + '99:59:59,999 --> 99:59:59,999\r\n'
            ret_value = ret_value + row
            ret_value = ret_value + '\r\n\r\n'

        return ret_value

    def get_video_id(self, video_url, language_code=None):
        url = 'https://amara.org/api/videos/'
        urldict = dict({'video_url': video_url})
        r = requests.get(url, params=urldict, headers=self.headers)
        json_ret = r.json()
        if 'objects' in json_ret and len(json_ret['objects']) > 0:
            return json_ret['objects'][0]['id']
        else:
            if language_code:
                return self.post_video(video_url, language_code)
            else:
                raise AmaraApiException('No video can be found or crated for url {}, language {}'.format(video_url, language_code))