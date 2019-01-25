#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from djcms_blog.models import Blog, BlogTitle, Author, AuthorBio, Post, PostTitle, Tag, TagTitle


class BlogModelsTestCase(TestCase):

    def setUp(self):
        self.default_user = User.objects.create_user('luke', 'luke_skywalker@gmail.com', '123123')
        self.default_user.first_name = 'Luke'
        self.default_user.last_name = 'Skywalker'
        self.default_user.save()

        self.blog = Blog.objects.create(
            title="My Blog",
            slug="my-blog",
            cover="my-blog-cover-image.png",
            block_header="My Blog header tag",
            block_footer="My Blog footer tag",
        )
        self.blog_title_en = BlogTitle.objects.create(
            blog=self.blog,
            language='en',
            title="My Blog",
            description="This is My Blog description",
            meta_title="This is My Blog title meta tag",
            meta_description="This is My Blog description meta tag"
        )
        self.blog_title_es = BlogTitle.objects.create(
            blog=self.blog,
            language='es',
            title="Mi Blog",
            description="Esta es la descripción de Mi Blog",
            meta_title="Esta es la meta tag title de Mi Blog",
            meta_description="Esta es la meta tag desccription de Mi Blog"
        )

        self.author = Author.objects.create(
            user=self.default_user,
            cover="/this/is/cover.png",
            profile_image="/this/is/profile.png",
            slug='luke-skywalker',
            location='Tatooine',
            website='http://jedirules.com',
            facebook_profile='https://facebook.com/luke_skywalker',
            twitter_profile='https://twitter.com/luke_skywalker',
            block_header='This is the block header Luke',
            block_footer='This is the block footer Luke',
        )

        self.author_bio_en = AuthorBio.objects.create(
            author=self.author,
            bio="#Hi! \n I'm developer from Tatooine",
            language='en'
        )
        self.author_bio_es = AuthorBio.objects.create(
            author=self.author,
            bio="#Hola! \n Soy desarrollador y soy de Tatooine",
            language='es'
        )

        self.django_tag = Tag.objects.create(
            blog=self.blog,
            cover="tag/cover.jpg",
            name="django",
            slug="django",
            color="red",
            meta_title="meta title",
            meta_description="meta description"
        )
        self.django_tag_en = TagTitle.objects.create(
            tag=self.django_tag,
            language="en",
            name="django",
            description="",
            meta_title="meta title",
            meta_description="meta description"
        )
        self.django_tag_es = TagTitle.objects.create(
            tag=self.django_tag,
            language="es",
            name="django",
            description="",
            meta_title="meta titulo",
            meta_description="meta descripcion"
        )

        self.luke_first_post = Post.objects.create(
            blog=self.blog,
            title="Luke first post",
            slug="luke-first-post",
            author=self.author
        )
        self.luke_first_post.tags.add(self.django_tag)

        self.luke_first_post_en = PostTitle.objects.create(
            post=self.luke_first_post,
            title="Luke first post",
            language='en',
            description="# Luke first post",
            body="This is the post body",
            meta_title="post meta title",
            meta_description="post meta description",
            published=False,
            is_draft=True,
            created=timezone.now(),
            modified=timezone.now(),
            published_date=timezone.now(),
        )
        self.luke_first_post_en.publish()
        self.luke_first_post_es = PostTitle.objects.create(
            post=self.luke_first_post,
            title="Primer post de Luke",
            language='es',
            description="# Primer post de Luke",
            body="Body del primer post",
            meta_title="post meta title",
            meta_description="post meta description",
            published=False,
            is_draft=True,
            created=timezone.now(),
            modified=timezone.now(),
            published_date=timezone.now(),
        )
        self.luke_first_post_es.publish()

    def test_blog_model(self):
        self.assertEqual(str(self.blog), "My Blog")

        self.assertEqual(self.blog.get_language_object('en'), self.blog_title_en)
        self.assertEqual(self.blog.get_language_object('es'), self.blog_title_es)
        self.assertEqual(self.blog.get_language_object('fr'), self.blog_title_en)

        self.assertEqual(str(self.blog_title_en), "My Blog")
        self.assertEqual(str(self.blog_title_es), "Mi Blog")

        self.assertTrue(self.blog.has_language('en'))
        self.assertFalse(self.blog.has_language('fr'))

        self.assertEqual(list(self.blog.get_posts()), [self.luke_first_post])

    def test_author_model(self):
        self.assertEqual(str(self.author), 'luke_skywalker@gmail.com')
        self.assertEqual(self.author.get_name(), 'Luke Skywalker')

        self.assertEqual(self.author.get_language_object('en'), self.author_bio_en)
        self.assertEqual(self.author.get_language_object('es'), self.author_bio_es)
        self.assertEqual(self.author.get_language_object('fr'), self.author_bio_en)

        self.assertEqual(str(self.author_bio_en), 'luke_skywalker@gmail.com en')
        self.assertEqual(str(self.author_bio_es), 'luke_skywalker@gmail.com es')

        self.assertTrue(self.author.has_language('en'))
        self.assertFalse(self.author.has_language('fr'))

        self.assertEqual(list(self.author.get_posts()), [self.luke_first_post])
        self.assertEqual(self.author.get_post_count(), 1)

    def test_tag_model(self):
        self.assertEqual(str(self.django_tag), "django")

        self.assertEqual(self.django_tag.get_language_object('en'), self.django_tag_en)
        self.assertEqual(self.django_tag.get_language_object('es'), self.django_tag_es)
        self.assertEqual(self.django_tag.get_language_object('fr'), self.django_tag_en)

        self.assertTrue(self.django_tag.has_language('en'))
        self.assertTrue(self.django_tag.has_language('es'))
        self.assertFalse(self.django_tag.has_language('fr'))

        self.assertEqual(str(self.django_tag_en), "django")
        self.assertEqual(str(self.django_tag_es), "django")

        self.assertEqual(list(self.django_tag.get_posts()), [self.luke_first_post])
        self.assertEqual(self.django_tag.get_post_count(), 1)

    def test_post_model(self):
        self.assertEqual(str(self.luke_first_post), "Luke first post")

        self.assertTrue(self.luke_first_post.has_language('en'))
        self.assertFalse(self.luke_first_post.has_language('fr'))

        self.assertEqual(self.luke_first_post.get_language_object('en'), self.luke_first_post_en)
        self.assertEqual(self.luke_first_post.get_language_object('es'), self.luke_first_post_es)
        self.assertEqual(self.luke_first_post.get_language_object('fr'), self.luke_first_post_en)

        # Plubished object
        self.assertEqual(self.luke_first_post.language_object('en'), self.luke_first_post_en.public_post_title)
        self.assertEqual(self.luke_first_post.language_object('es'), self.luke_first_post_es.public_post_title)
        self.assertEqual(self.luke_first_post.language_object('fr'), self.luke_first_post_en.public_post_title)

        self.assertTrue(self.luke_first_post.is_published())

        self.assertEqual(list(self.luke_first_post.get_tags()), [self.django_tag])

    def test_post_not_published(self):
        other_post = Post.objects.create(
            blog=self.blog,
            title="other post",
            slug="other-post",
            author=self.author
        )

        self.assertFalse(other_post.is_published())

        other_post_en = PostTitle.objects.create(
            post=other_post,
            title="Other post",
            language='en',
            description="# Other post",
            body="Body post",
            meta_title="post meta title",
            meta_description="post meta description",
            published=False,
            is_draft=True,
            created=timezone.now(),
            modified=timezone.now(),
            published_date=timezone.now(),
        )
        self.assertFalse(other_post_en.edited())

    def test_post_title_model(self):
        self.assertEqual(self.luke_first_post_en.get_absolute_url(), "/en/my-blog/luke-first-post/")

        self.assertFalse(self.luke_first_post_en.edited())

        self.luke_first_post_en.title = self.luke_first_post_en.title + " edited"
        self.luke_first_post_en.save()

        self.assertTrue(self.luke_first_post_en.edited())

        self.assertIsNotNone(self.luke_first_post_en.public_post_title)
        self.assertTrue(self.luke_first_post_en.publish())
        self.assertEqual(self.luke_first_post_en.public_post_title.title, "Luke first post edited")

        self.assertFalse(self.luke_first_post_en.publish())  # Nothing to publish

        self.luke_first_post_en.unpublish()
        self.assertIsNone(self.luke_first_post_en.public_post_title)
        self.assertIsNone(self.luke_first_post_en.published_date)
        self.assertFalse(self.luke_first_post_en.published)
