
from googleapiclient import sample_tools
from bs4 import BeautifulSoup  # Or from BeautifulSoup import BeautifulSoup
import datetime
from collections import namedtuple
import re
BlogPost = namedtuple('BlogPost', 'postId url title videoId content labels amara_embed')

class BlogClient:

    def __init__(self, client_json_file):
        self.client_json_file = client_json_file
        self.service, self.flags = self.login()
        self.posts = self.service.posts()

    def stripHtmlTags(self, htmlTxt):
        if htmlTxt is None:
            return None
        else:
            all_lines = BeautifulSoup(htmlTxt).findAll(text=True)
            not_empty_lines = [line for line in all_lines if len(line) > 0]
            return '\n'.join(not_empty_lines)

    def login(self):
        service, flags = sample_tools.init(
            ['--noauth_local_webserver'], 'blogger', 'v3', __doc__, self.client_json_file ,
            scope='https://www.googleapis.com/auth/blogger')
        return service, flags

    def replace_object_in_blog_post(self, blogId, postId):

        content, videoId, posts_doc = self.extract_content_and_video(blogId, postId)
        obind1 = content.find('<object')
        obind2 = content.find('object>')

        if videoId and obind1 >= 0 and obind2 >=0 :
            newcontent = content[0:obind1]+'<iframe src="https://www.youtube.com/embed/'+videoId+'" width="640" height="390" frameborder="0" allowfullscreen></iframe>'+content[obind2+7:len(content)]
            posts_doc['content'] = newcontent
            request = self.posts.update(blogId=blogId, postId=postId,body=posts_doc)
            print('Replacing object' + postId)
            request.execute()

    def extract_video(self, blogId, postId):
        return self.extract_content_and_video(blogId, postId)['videoId']

    def extract_content_and_video(self, blogId, postId):
        request = self.posts.get(blogId=blogId, postId=postId)
        posts_doc = request.execute()
        content = posts_doc['content']
        #print('Processing post ' + postId + ':' + posts_doc['title'])
        #search_youtube = re.search('youtube\.com\/v\/([\w\-]{11})', content)
        search_youtube = re.search('\\\".*?youtube\.com\/embed\/([\w\-]{11})[\"\?]', content)
        videoId = None
        if search_youtube :
            videoId = search_youtube.group(1)
        result_dict = {'content':content, 'videoId': videoId, 'posts_doc': posts_doc}
        return result_dict

    def insert_amara_tags(self, blogId, postId, language_code):
        result_dict = self.extract_content_and_video(blogId, postId)
        content, videoId, posts_doc = result_dict['content'],result_dict['videoId'],result_dict['posts_doc']
        if content.find('amara') > -1:
            return
        pos_iframe= content.find('<iframe')
        snippet_amara = '<div class="amara-embed" data-height="390px" data-resizable="true" data-show-subtitles-default="true" data-url="http://www.youtube.com/watch?v='+videoId+'" data-width="640px" data-initial-language="'+language_code+'"></div></br>'
        newContent = content[0:pos_iframe]+snippet_amara +content[pos_iframe:len(content)]
        posts_doc['content'] = newContent
        posts_doc['labels'].append('subtitled')
        posts_doc['updated'] = posts_doc['published'] = str(datetime.datetime.now().isoformat(timespec='microseconds'))
        request = self.posts.update(blogId=blogId,postId=postId,body=posts_doc)
        request.execute()


    def update_video_in_blog_post(self, blogId, postId, old_youtube_ref,new_youtube_ref, posts):
        request = posts.get(blogId=blogId,postId=postId)
        posts_doc = request.execute()
        posts_doc['content'] = posts_doc['content'].replace(old_youtube_ref,new_youtube_ref)
        request = posts.update(blogId=blogId, postId=postId,body=posts_doc)
        request.execute()

    def retrieve_lyrics(self, blogId, postId ):
        request = self.posts.get(blogId=blogId, postId=postId)
        posts_doc = request.execute()
        content = posts_doc['content']
        return self.stripHtmlTags(content )


    def iterate_blog_items(self, blogId):

        request = self.posts.list(blogId=blogId)
        while request != None:
            posts_doc = request.execute()
            if 'items' in posts_doc and not (posts_doc['items'] is None):
                for post in posts_doc['items']:
                    yield post
            request = self.posts.list_next(request, posts_doc)

    def iterate_blog_posts(self, blogId):
        for item in self.iterate_blog_items(blogId):
            content = item['content']
            m_you_tube = re.search('src=\\\".*?youtube\.com\/embed\/([\w\-]{11})[\"\?]', content)
            m_amara_embed = re.search('amara-embed', content)
            video_id = m_you_tube.group(1) if m_you_tube else None
            yield BlogPost(postId=item['id'],
                           url=item['url'],
                           title=item['title'].strip(),
                           videoId=video_id,
                           content=self.stripHtmlTags(item['content']),
                           labels=item.get('labels', None),
                           amara_embed=1 if m_amara_embed else 0)
