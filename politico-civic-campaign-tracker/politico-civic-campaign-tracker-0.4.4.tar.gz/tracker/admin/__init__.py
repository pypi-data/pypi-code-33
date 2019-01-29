from django.contrib import admin
from entity.models import Person
from tracker.models import (
    CampaignContent,
    CandidateRankingSet,
    CandidateRanking,
    CandidateRatingCategory,
    CandidateWinRating,
    Quote,
    Story,
    Tweet,
    Video,
)
from .person import PersonAdmin

admin.site.unregister(Person)
admin.site.register(Person, PersonAdmin)
admin.site.register(CampaignContent)
admin.site.register(CandidateRankingSet)
admin.site.register(CandidateRanking)
admin.site.register(CandidateRatingCategory)
admin.site.register(CandidateWinRating)
admin.site.register(Quote)
admin.site.register(Story)
admin.site.register(Tweet)
admin.site.register(Video)
