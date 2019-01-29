# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import (AnswerChoice, McqAnswer, Question, Survey, SurveyLink,
                     TextAnswer, UserAnswer)


class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'phone', 'user', 'created']


class QustionAdmin(admin.ModelAdmin):
    list_display = ['question', 'question_type', 'survey', 'parent', 'created']

    def parent(self, obj):
        res = ""
        for x in obj.in_response_of.all():
            res = "{} <{}>".format(res, x)
        return res


class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer', 'code', 'created']


class McqAnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_choice', 'survey', 'contact', 'created']

    def survey(self, obj):
        return obj.answer_choice.question.survey.title


class TextAnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'contact', 'answer', 'created']


class SurveyLinkAdmin(admin.ModelAdmin):
    list_display = ['long_url', 'short_url', 'question',
                    'contact', 'created']

    def user(self, obj):
        try:
            return obj.contact.user.email
        except BaseException:
            pass


admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QustionAdmin)
admin.site.register(AnswerChoice, AnswerChoiceAdmin)
admin.site.register(McqAnswer, McqAnswerAdmin)
admin.site.register(TextAnswer, TextAnswerAdmin)
admin.site.register(SurveyLink, SurveyLinkAdmin)
admin.site.register(UserAnswer)
