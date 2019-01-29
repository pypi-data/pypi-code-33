import os

from django import forms

from ccc.survey import choices
from ccc.survey.models import Question, Survey, SurveyMappedKeywords


class SurveyForm(forms.ModelForm):
    VOICE_GREETING_TYPE_CHOICES = (
        ('voice_greeting_upload', 'Audio file'),
        ('voice_greeting_record', 'Record own message'),
    )

    voice_greeting_type = forms.ChoiceField(choices=VOICE_GREETING_TYPE_CHOICES, required=False)
    voice_greeting_original_recording = forms.CharField(required=False)

    class Meta:
        model = Survey
        fields = ['title', 'phone', 'voice_greeting_original', 'greeting_text',
                  'last_message', 'campaign', ]
        widgets = {
            'phone': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_voice_greeting_original(self):
        file = self.cleaned_data.get("voice_greeting_original")
        if file:
            ext = os.path.splitext(file.name)[1]
            if not ext.lower() in [".mp3", ".wav", ".m4a"]:
                raise forms.ValidationError(
                    'Invalid audio file. Please upload a valid audio file'
                )
        return file


class QuestionForm(forms.ModelForm):
  
    schedular_step = forms.ChoiceField(choices=choices.QUESTION_SCHEDULAR_STEP)

    class Meta:
        model = Question
        fields = ['question', 'question_type', 'contact_mapping', 'delay',
                  'schedular_step']
        widgets = {
            'question': forms.Textarea(attrs={'rows': '3', 'cols': '40'}),
        }

    def clean(self):
        cleaned_data = super(QuestionForm, self).clean()

        from ccc.survey.models import Question
        delay, schedular_step = cleaned_data['delay'], cleaned_data['schedular_step']
        cleaned_data['delay'] = Question.clean_delay_value(delay, schedular_step)

        return cleaned_data


class AssignKwywordsToSurveyForm(forms.Form):

    surveys = forms.ModelChoiceField(
        Survey.objects.none(), empty_label=None,
        widget=forms.Select(attrs={
            'class': 'form-control chosen-select select2'}))

    keywords = forms.CharField(
        max_length=1000, required=True,
        help_text="Survey keywords separated by comma(,)",
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        survey_id = kwargs.pop('survey_id')
        super(AssignKwywordsToSurveyForm, self).__init__(*args, **kwargs)
        self.fields['surveys'].queryset = Survey.objects.filter(
            active=True, user=user, id=survey_id)

    def clean_keywords(self):
        keywords = self.cleaned_data.get("keywords", '').split(",")
        keywords_list = [str(x).lower().strip() for x in keywords]

        survey = self.cleaned_data.get("surveys")
        surveys = Survey.objects.filter(phone=survey.phone, active=True)
        maaped_keywords = SurveyMappedKeywords.objects.filter(
            survey__in=surveys,
            is_active=True).exclude(survey=survey)

        for obj in maaped_keywords:
            if str(obj.keyword).lower() in keywords_list:
                raise forms.ValidationError(
                    "{} is already mapped with {} survey".format(obj.keyword, obj.survey))

        return self.cleaned_data.get("keywords", '')

    def save(self):
        survey = self.cleaned_data.get("surveys")
        keywords = self.cleaned_data.get("keywords")
        if keywords:
            mapped_keywords = keywords.split(",")
            SurveyMappedKeywords.objects.filter(
                survey=survey).update(is_active=False)
            for keyword in mapped_keywords:
                keyword = keyword.strip()
                key_obj, created = SurveyMappedKeywords.objects.get_or_create(
                    survey=survey,
                    keyword=keyword)
                key_obj.is_active = True
                key_obj.save()
