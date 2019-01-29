import logging

from ccc.marketing.surveys.api.serializers import SurveySerializer
from ccc.marketing.surveys.elasticsearch import SurveyElasticSearch
from ccc.survey.cloud_tasks import survey_convert_audio_format

logger = logging.getLogger(__name__)


def post_save_survey(sender, instance, **kwargs):
    survey_convert_audio_format(survey_id=instance.id).execute()
    try:
        ce = SurveyElasticSearch()
        ce.store_record(id=instance.id, data=SurveySerializer(instance).data)
    except Exception as ex:
        logger.info('Survey data is not saved in elastic search index for survey id {},'
                    '{}'.format(instance.id, ex))


def post_delete_survey(sender, instance, **kwargs):
    try:
        ce = SurveyElasticSearch()
        ce.delete_record(id=instance.id)
    except Exception as ex:
        logger.info('Survey data is not deleted in elastic search index for contact id {},'
                    '{}'.format(instance.id, ex))
