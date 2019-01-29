import os

from django.core.management.base import BaseCommand
from election.models import Candidate
from entity.models import PersonImage, ImageTag
from tracker.utils.aws import get_bucket


LAST_NAME_EXCEPTIONS = {"Orourke": "O'Rourke", "Omalley": "O'Malley"}


class Command(BaseCommand):
    def handle(self, *args, **options):
        cmd_path = os.path.dirname(os.path.realpath(__file__))
        img_folder = os.path.join(cmd_path, "../../bin/candidate-images")
        s3_path = "election-results/2020/presidential-candidates/images/"

        for img in os.listdir(img_folder):
            bucket = get_bucket()
            img_path = os.path.join(img_folder, img)
            s3_key = os.path.join(s3_path, img.lower())

            bucket.upload_file(
                img_path,
                s3_key,
                {"CacheControl": "max-age=60", "ContentType": "image/png"},
            )

            public_url = "https://s3.amazonaws.com/staging.interactives.politico.com/{}".format(
                s3_key
            )
            print(public_url)

            first_name = img.split("-")[0]
            last_name = img.split("-")[1]

            if LAST_NAME_EXCEPTIONS.get(last_name):
                last_name = LAST_NAME_EXCEPTIONS[last_name]

            candidate = Candidate.objects.get(
                person__first_name=first_name,
                person__last_name=last_name,
                race__office__slug="president",
                race__cycle__slug="2020",
            )
            image_tag = ImageTag.objects.get_or_create(name="tracker")[0]

            image_record = PersonImage.objects.get_or_create(
                person=candidate.person, tag=image_tag
            )[0]

            image_record.image = public_url

            image_record.save()
