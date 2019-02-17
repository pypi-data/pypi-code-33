from pymongo import MongoClient
from .blog_client import BlogPost
from amaraapi import AmaraTools, AmaraVideo
import traceback


class BlogRepository:

    def __init__(self, mongo_connection, blogId):
        self.mongo_connect = mongo_connection
        self.client = MongoClient(mongo_connection)
        self.musicblogs_database = self.client.musicblogs
        self.blogId = blogId
        self.posts_collection = self.musicblogs_database['posts.' + blogId]
        self.posts_in_blog = self.posts_collection.find()
        self.posts_map = \
            {p['postId']: BlogPost(
                postId=p['postId'], title=p['title'], videoId=p['videoId'], content=p['content'],
                labels=p.get('labels', 0),
                url=p.get('url', ''),
                amara_embed=p.get('amara_embed', '')
            ) for p in self.posts_in_blog
            }

        self.postids = set(self.posts_map.keys())
        self.subtitles_collection = self.musicblogs_database['subtitles.' + blogId]



    def update_blog_post(self, blog_post):
        if not blog_post:
            return

        if not hasattr(blog_post, "postId"):
            return
        if blog_post.postId in self.postids:
            self.postids.remove(blog_post.postId)

        if blog_post.postId in self.posts_map:

            update_key, update_value = {'postId': blog_post.postId}, {k: v for k, v in blog_post._asdict().items() if k not in "postId"}

            if blog_post != self.posts_map[blog_post.postId]:
                print("updating {}".format(update_key ))

                self.posts_collection.update_one(update_key,   { '$set' : update_value } )
                print("updated {} ".format(update_key))
            else:
                print("post {} unchanged".format(blog_post.postId))
        else:
            print("inserting {} ".format(blog_post.postId))
            self.posts_collection.insert_one(blog_post._asdict())
            print("inserted {} ".format(blog_post.postId))

    def update_sub_titles(self, blog_post, languages, amara_headers):

        amara_tools = AmaraTools(amara_headers)
        if hasattr(blog_post, "labels"):
            labels = blog_post.labels
            video_url = blog_post.videoId

            if labels and ('subtitled' in labels or 'SUBTITLED' in labels):
                print("Trying to get video for {}".format(video_url))
                try:
                    amara_id = amara_tools.get_video_id(video_url='https://youtu.be/' + video_url)
                    amara_video = AmaraVideo(amara_headers, amara_id)
                    if amara_video:
                        languages_video = amara_video.get_languages()
                        common_languages = [l for l in languages_video if l in languages]
                        if common_languages:
                            sel_language = common_languages[0]
                            subtitles = amara_video.get_subtitles(sel_language)
                            if subtitles and len(subtitles) > 0:
                                print("Saving subtitles for {}".format(video_url))
                                self.subtitles_collection.replace_one(
                                    filter={"video_url": video_url},
                                    replacement={"video_url": video_url, "video_id": amara_id, "lang": sel_language,
                                                 "subtitles": subtitles},
                                    upsert=True
                                )

                except:
                    print("Could not process {} from {}".format(video_url, blog_post.url))
                    traceback.print_exc()

    def delete_old_posts(self):
        for postid in self.postids:
            self.posts_collection.delete_one({'postId': postid})
            print("post {} deleted".format(postid))
