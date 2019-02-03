import requests


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


class AmaraVideo:

    def __init__(self, headers, amara_id):
        self.headers = headers
        self.amara_id = amara_id

    def get_subtitles(self, language):

        url='https://amara.org/api/videos/'+self.amara_id+'/languages/'+language+'/subtitles/?sub_format=srt'

        r =requests.get(url, headers=self.headers)
        subtitles_obj = r.json()
        if 'version_number' in subtitles_obj and 'subtitles' in subtitles_obj and subtitles_obj['version_number'] > 1:
            return subtitles_obj
        else:
            return None

    def get_video_info(self):
        if not hasattr(self, 'video_info'):
            url='https://amara.org/api/videos/'+self.amara_id+'/'

            r =requests.get(url, headers=self.headers)
            self.video_info = r.json()

        return self.video_info

    def get_title(self):
        return self.get_video_info()['title']

    def get_urls(self):
        return self.get_video_info()['all_urls']

    def get_languages(self):
        return self.get_video_info()['languages']

    def get_best_subtitles(self):
        languages = self.get_languages()
        best_subtitle = None
        for language in languages:
            curr_subtitle = self.get_subtitles(language['code'])
            if not best_subtitle or (curr_subtitle and curr_subtitle['version_number'] > best_subtitle['version_number']):
                best_subtitle = curr_subtitle

        if best_subtitle:
            return best_subtitle['subtitles']
        else:
            return None


    def get_actions(self,language_code):
        url = 'https://amara.org/api/videos/'+self.amara_id+'/languages/'+language_code+'/subtitles/actions/'
        r = requests.get(url, headers=self.headers)
        self.actions = r.json()
        return self.actions

    def post_subtitles(self, language_code, subtitles):
        url = 'https://amara.org/api/videos/'+self.amara_id+'/languages/'+language_code+'/subtitles/'
        urldict = dict({'subtitles': subtitles, 'sub_format': 'srt'})
        r = requests.post(url, data=urldict, headers=self.headers)



class Amara:

    def __init__(self,headers):
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


