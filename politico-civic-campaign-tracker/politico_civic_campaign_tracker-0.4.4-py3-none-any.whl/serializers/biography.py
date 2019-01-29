from biography.models import (
    Biography,
    Birthplace,
    Financials,
    Ideology,
    Education,
    Occupation,
    PastCampaign,
    Publication,
    Legislation,
    Residence,
)
from rest_framework import serializers


class BirthplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Birthplace
        fields = ("city", "state", "country")


class ResidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Residence
        fields = ("city", "state", "country")


class FinancialsSerializer(serializers.ModelSerializer):
    net_worth = serializers.IntegerField()

    class Meta:
        model = Financials
        fields = ("net_worth", "notes")


class IdeologySerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        return obj.category.name

    class Meta:
        model = Ideology
        fields = ("dw_nominate", "category")


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = (
            "id",
            "school",
            "degree",
            "degree_program",
            "graduation_date",
            "honorary",
            "state",
            "country",
        )


class OccupationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = (
            "id",
            "sector",
            "title",
            "from_date",
            "to_date",
            "employer",
            "present",
        )


class PastCampaignSerializer(serializers.ModelSerializer):
    office = serializers.SerializerMethodField()

    def get_office(self, obj):
        return obj.office.label

    class Meta:
        model = PastCampaign
        fields = ("id", "office", "year")


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = (
            "id",
            "title",
            "publication_type",
            "publisher",
            "link",
            "publication_date",
        )


class LegislationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Legislation
        fields = "__all__"


class BiographySerializer(serializers.ModelSerializer):
    birthplace = serializers.SerializerMethodField()
    residence = serializers.SerializerMethodField()
    financials = serializers.SerializerMethodField()
    ideology = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    occupations = serializers.SerializerMethodField()
    past_campaigns = serializers.SerializerMethodField()
    publications = serializers.SerializerMethodField()
    legislation = serializers.SerializerMethodField()

    def get_birthplace(self, obj):
        try:
            return BirthplaceSerializer(obj.birthplace).data
        except:
            return None

    def get_residence(self, obj):
        try:
            return ResidenceSerializer(obj.residence).data
        except:
            return None

    def get_financials(self, obj):
        try:
            return FinancialsSerializer(obj.financials).data
        except:
            return None

    def get_ideology(self, obj):
        try:
            return IdeologySerializer(obj.ideology).data
        except:
            return None

    def get_education(self, obj):
        return EducationSerializer(obj.education, many=True).data

    def get_occupations(self, obj):
        return OccupationSerializer(obj.occupations, many=True).data

    def get_past_campaigns(self, obj):
        return PastCampaignSerializer(obj.campaigns, many=True).data

    def get_publications(self, obj):
        return PublicationSerializer(obj.publications, many=True).data

    def get_legislation(self, obj):
        return LegislationSerializer(obj.legislation, many=True).data

    class Meta:
        model = Biography
        fields = (
            "birthplace",
            "residence",
            "financials",
            "ideology",
            "education",
            "occupations",
            "past_campaigns",
            "publications",
            "legislation",
        )
