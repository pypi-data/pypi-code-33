#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import activate, deactivate_all

from djcms_blog.models import Blog, BlogTitle, Author, AuthorBio, Post, PostTitle, Tag, TagTitle


class BlogAdminTestCase(TestCase):

    def setUp(self):
        activate('en')
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

    def test_not_valid_url(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)

    def test_not_valid_i18n_langcode_views(self):
        activate('jp')
        response = self.client.get(reverse('blog-main', kwargs={'blog_slug': self.blog.slug}))
        self.assertEqual(response.status_code, 404)

    def test_blog_disabled_i18n_views(self):
        deactivate_all()
        response = self.client.get(reverse('blog-main', kwargs={'blog_slug': self.blog.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("<title>Test Blog\\nMy Blog\\n</title>", str(response._container))

    def test_blog_views(self):
        response = self.client.get(reverse('blog-main', kwargs={'blog_slug': self.blog.slug}))
        self.assertEqual(response.status_code, 200)

    def test_tag_view(self):
        response = self.client.get(
            reverse('tag-main', kwargs={'blog_slug': self.blog.slug, 'tag_slug': self.django_tag.slug}))
        self.assertEqual(response.status_code, 200)

    def test_author_views(self):
        response = self.client.get(
            reverse('author-main', kwargs={'author_slug': self.author.slug}))
        self.assertEqual(response.status_code, 200)

    def test_post_views(self):
        response = self.client.get(
            reverse('post-detail', kwargs={'blog_slug': self.blog.slug, 'post_slug': self.luke_first_post.slug}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('post-detail', kwargs={'blog_slug': self.blog.slug, 'post_slug': 'not-valid'}))
        self.assertEqual(response.status_code, 404)

        other_post = Post.objects.create(
            blog=self.blog,
            title="Other post",
            slug="other-post",
            author=self.author
        )
        response = self.client.get(
            reverse('post-detail', kwargs={'blog_slug': self.blog.slug, 'post_slug': other_post.slug}))
        self.assertEqual(response.status_code, 404)

    def test_post_draft_views(self):
        response = self.client.get(
            reverse('draft-post-detail', kwargs={'blog_slug': self.blog.slug, 'post_slug': self.luke_first_post.slug}))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('draft-post-detail', kwargs={'blog_slug': self.blog.slug, 'post_slug': None}))
        self.assertEqual(response.status_code, 404)
