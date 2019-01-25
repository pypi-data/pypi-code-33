# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import simplemde.fields


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                ("cover", models.ImageField(upload_to="author_cover")),
                ("image", models.ImageField(upload_to="image")),
                ("slug", models.CharField(max_length=140)),
                ("location", models.CharField(max_length=100)),
                ("website", models.URLField(max_length=100)),
                ("facebook_profile", models.URLField(max_length=100)),
                ("twitter_profile", models.URLField(max_length=100)),
                (
                    "block_header",
                    simplemde.fields.SimpleMDEField(
                        max_length=10000, blank=True, null=True
                    ),
                ),
                (
                    "block_footer",
                    simplemde.fields.SimpleMDEField(
                        max_length=10000, blank=True, null=True
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        related_name="author_profile", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AuthorBio",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                ("bio", simplemde.fields.SimpleMDEField(max_length=255)),
                (
                    "language",
                    models.CharField(
                        max_length=15,
                        db_index=True,
                        choices=[("en", "en"), ("es", "es")],
                    ),
                ),
                ("author", models.ForeignKey(to="djcms_blog.Author")),
            ],
        ),
        migrations.CreateModel(
            name="Blog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                ("title", models.CharField(max_length=140)),
                ("slug", models.CharField(max_length=140, db_index=True)),
                ("cover", models.ImageField(upload_to="blog_cover")),
                (
                    "block_header",
                    simplemde.fields.SimpleMDEField(
                        max_length=10000, blank=True, null=True
                    ),
                ),
                (
                    "block_footer",
                    simplemde.fields.SimpleMDEField(
                        max_length=10000, blank=True, null=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BlogTitle",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        max_length=15,
                        db_index=True,
                        choices=[("en", "en"), ("es", "es")],
                    ),
                ),
                ("title", models.CharField(max_length=140)),
                ("description", simplemde.fields.SimpleMDEField(max_length=255)),
                (
                    "meta_title",
                    simplemde.fields.SimpleMDEField(
                        max_length=70, blank=True, null=True
                    ),
                ),
                (
                    "meta_description",
                    simplemde.fields.SimpleMDEField(
                        max_length=156, blank=True, null=True
                    ),
                ),
                ("blog", models.ForeignKey(to="djcms_blog.Blog")),
            ],
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("slug", models.CharField(max_length=140)),
                (
                    "cover",
                    models.ImageField(blank=True, null=True, upload_to="post_cover"),
                ),
                ("author", models.ForeignKey(to="djcms_blog.Author")),
                ("blog", models.ForeignKey(to="djcms_blog.Blog")),
            ],
        ),
        migrations.CreateModel(
            name="PostTitle",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "language",
                    models.CharField(
                        max_length=15,
                        db_index=True,
                        choices=[("en", "en"), ("es", "es")],
                    ),
                ),
                ("description", simplemde.fields.SimpleMDEField(max_length=80000)),
                ("body", simplemde.fields.SimpleMDEField(max_length=80000)),
                (
                    "meta_title",
                    simplemde.fields.SimpleMDEField(
                        max_length=70, blank=True, null=True
                    ),
                ),
                (
                    "meta_description",
                    simplemde.fields.SimpleMDEField(
                        max_length=156, blank=True, null=True
                    ),
                ),
                ("published", models.BooleanField(default=False)),
                (
                    "publisher_is_draft",
                    models.BooleanField(db_index=True, default=True, editable=False),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                ("published_date", models.DateTimeField(blank=True, null=True)),
                ("post", models.ForeignKey(to="djcms_blog.Post")),
                (
                    "publisher_public",
                    models.OneToOneField(
                        null=True,
                        editable=False,
                        related_name="publisher_draft",
                        to="djcms_blog.PostTitle",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                ("cover", models.ImageField(upload_to="tag_cover")),
                ("name", models.CharField(max_length=140)),
                ("slug", models.CharField(max_length=140)),
                (
                    "color",
                    models.CharField(
                        max_length=14,
                        choices=[
                            ("red", "red"),
                            ("orange", "orange"),
                            ("yellow", "yellow"),
                            ("olive", "olive"),
                            ("green", "green"),
                            ("teal", "teal"),
                            ("blue", "blue"),
                            ("violet", "violet"),
                            ("purple", "purple"),
                            ("pink", "pink"),
                            ("brown", "brown"),
                            ("grey", "grey"),
                            ("black", "black"),
                        ],
                    ),
                ),
                (
                    "meta_title",
                    simplemde.fields.SimpleMDEField(
                        max_length=70, blank=True, null=True
                    ),
                ),
                (
                    "meta_description",
                    simplemde.fields.SimpleMDEField(
                        max_length=156, blank=True, null=True
                    ),
                ),
                ("blog", models.ForeignKey(to="djcms_blog.Blog")),
            ],
        ),
        migrations.CreateModel(
            name="TagTitle",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        max_length=15,
                        db_index=True,
                        choices=[("en", "en"), ("es", "es")],
                    ),
                ),
                ("name", models.CharField(max_length=140)),
                ("description", simplemde.fields.SimpleMDEField(max_length=200)),
                (
                    "meta_title",
                    simplemde.fields.SimpleMDEField(
                        max_length=70, blank=True, null=True
                    ),
                ),
                (
                    "meta_description",
                    simplemde.fields.SimpleMDEField(
                        max_length=156, blank=True, null=True
                    ),
                ),
                ("tag", models.ForeignKey(to="djcms_blog.Tag")),
            ],
        ),
        migrations.AddField(
            model_name="post",
            name="tag",
            field=models.ManyToManyField(to="djcms_blog.Tag"),
        ),
        migrations.AlterUniqueTogether(
            name="tagtitle", unique_together=set([("tag", "language")])
        ),
        migrations.AlterUniqueTogether(
            name="posttitle",
            unique_together=set([("post", "language", "publisher_is_draft")]),
        ),
        migrations.AlterUniqueTogether(
            name="blogtitle", unique_together=set([("blog", "language")])
        ),
    ]
