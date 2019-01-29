import json
import re

from rest_framework import serializers

from ccc.commonregex import CommonRegex
from ccc.contacts.models import Contact
from ccc.ocr.models import ImageContacts


class OCRImageContactsSerializer(serializers.ModelSerializer):
    """
    Purpose: A serializer that deals with Details instances and
    querysets.
    """
    data = serializers.SerializerMethodField()

    def get_data(self, obj):
        removal_options = ["dates", "times", "phones", "phones_with_exts", "links",
                           "emails", "prices", "btc_addresses", "street_addresses", "zip_codes", "po_boxes"
                           ]

        filter_data = ImageContacts.objects.filter(
            unique_upload_id=obj.unique_upload_id, campaign=obj.campaign)
        emails = []
        phones = []
        img_data = []
        meaningful_text = []
        request = self.context.get('request')
        exising_upload = Contact.objects.filter(
            card_image_uuid=obj.unique_upload_id).exclude(card_image_uuid=None)
        for img_obj in filter_data:
            image_url = img_obj.image.url
            if request:
                image_url = request.build_absolute_uri(img_obj.image.url)
            tmp_data = {"image": image_url,
                        "uuid": img_obj.unique_upload_id
                        }
            img_data.append(tmp_data)

            if exising_upload.exists():
                continue
            try:
                tmp_email = json.loads(img_obj.emails)
                emails.extend(tmp_email)
            except BaseException:
                pass
            try:
                parsed_text = CommonRegex(json.loads(img_obj.converted_text))
            except BaseException:
                parsed_text = CommonRegex(img_obj.converted_text)
            text = parsed_text.text
            for option in removal_options:
                try:
                    macthed_text = parsed_text.__getattribute__(option)()
                except BaseException:
                    macthed_text = parsed_text.__getattribute__(option)
                for remove_text in macthed_text:
                    text = text.replace(remove_text, "")
            text = re.sub("\S*\d\S*", "", text).strip()
            regex = re.compile('[a-zA-Z0-9\.\-\, ]+$')
            text = text.splitlines()
            text = [str(x).strip() for x in text if x and len(x) > 2 and regex.match(x)]
            meaningful_text.extend(text)

            try:
                tmp_phone = json.loads(img_obj.phones)
                phones.extend(tmp_phone)
            except BaseException:
                pass

        data = {"phones": list(set(phones)),
                "names": list(set(meaningful_text)),
                "company_names": list(set(meaningful_text)),
                "images": img_data,
                "emails": list(set(emails)),
                "uuid": obj.unique_upload_id,
                "campaign_id": obj.campaign.id if obj.campaign else '',
                "survey_id": obj.survey.id if obj.survey else '',
                }
        if exising_upload.exists():
            exising_upload = exising_upload[0]
            data = {"phones": [exising_upload.phone],
                    "names": [" ".join([exising_upload.first_name, exising_upload.last_name]).strip()],
                    "company_names": [exising_upload.company_name],
                    "images": img_data,
                    "emails": [exising_upload.email],
                    "uuid": obj.unique_upload_id,
                    "campaign_id": obj.campaign.id if obj.campaign else '',
                    "survey_id": obj.survey.id if obj.survey else '',
                    }

        return data

    class Meta(object):
        model = ImageContacts
        fields = ["data", "is_processed"]
