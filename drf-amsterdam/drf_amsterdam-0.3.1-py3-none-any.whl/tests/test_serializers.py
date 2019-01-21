import json

from django.test import TestCase
from datetime import date

from tests.serializers import TemperatureRecordSerializer
from tests.models import WeatherStation, TemperatureRecord

from rest_framework.test import APIClient
from rest_framework.serializers import ModelSerializer
from datapunt_api.rest import DisplayField

from django.contrib.gis.geos import Point
# # fake requests
# See: https://stackoverflow.com/questions/34438290/
# from rest_framework.request import Request
# from rest_framework.test import APIRequestFactory
#
# factory = APIRequestFactory()
# request = factory.get('/')

FORMATS = [
    ('api', 'text/html; charset=utf-8'),
    ('json', 'application/json'),
    ('xml', 'application/xml; charset=utf-8'),
    ('csv', 'text/csv; charset=utf-8'),
]


class TestDisplayFieldSerializer(ModelSerializer):
    """Test display field."""

    _display = DisplayField()

    class Meta:  # noqa
        model = WeatherStation
        fields = '__all__'


BBOX = [52.03560, 4.58565,
        52.48769, 5.31360]

RD = [121357.68, 487342.57]


def get_wgs_puntje():  # noqa
    lat = BBOX[0]
    lon = BBOX[1]
    return Point(float(lat), float(lon))

def get_rd_puntje(): # noqa
    x = RD[0]
    y = RD[1]
    return Point(x, y, srid=28992)


class SerializerTest(TestCase):
    """test datapunt_api."""

    def setUp(self):
        """Create some fake data."""
        ws = WeatherStation.objects.create(
            number=260,
            centroid=get_wgs_puntje(),
            centroid_rd=get_rd_puntje()
        )

        records = [
            {'station': ws, 'date': date(1901, 1, 1), 'temperature': '10.0'},
            {'station': ws, 'date': date(1901, 2, 1), 'temperature': '11.0'},
            {'station': ws, 'date': date(1901, 3, 1), 'temperature': '20.0'},
        ]
        for rs in records:
            TemperatureRecord.objects.create(**rs)

    def valid_response(
            self, url, response,
            content_type='text/html; charset=utf-8'):
        """Help method to check common status/json."""
        self.assertEqual(
            200, response.status_code, "Wrong response code for {}".format(url)
        )

        self.assertEqual(
            f"{content_type}",
            response["Content-Type"],
            "Wrong Content-Type for {}".format(url),
        )

    def test_rd_filter(self):
        location = "%s,%s,%s" % (
            RD[0], RD[1], 6
        )
        params = {
            location: location
        }
        c = APIClient()
        url = '/tests/weatherstation/'
        response = c.get(url, params=params)
        self.valid_response(url, response, content_type='application/json')
        self.assertEqual(len(response.json()['results']), 1)

        location = "%s,%s,%s" % (
            RD[1]+100, RD[0], 6
        )

        invalid_params = {location: location}

        response = c.get(url, params=invalid_params)

        self.assertEqual(
            200, response.status_code, "Wrong response code for {}".format(url)
        )

    def test_active(self):  # noqa
        self.assertTrue(True)

    def test_cannot_serialize_without_request_context(self):
        qs = TemperatureRecord.objects.all()
        self.assertTrue(qs.count() == 3)

        # We need request in context to build hyperlinks for relations.
        with self.assertRaises(AssertionError):
            TemperatureRecordSerializer(qs, many=True).data

    def test_json_html(self):
        c = APIClient()
        response = c.get('/tests/')
        self.assertEqual(response.status_code, 200)

    def test_options_html(self):
        c = APIClient()
        response = c.options('/tests/')
        self.assertEqual(response.status_code, 200)
        response = c.options('/tests/weatherstation/')
        self.assertEqual(response.status_code, 200)

    def test_formats(self):

        c = APIClient()

        for fmt, encoding in FORMATS:
            url = '/tests/weatherstation/'
            response = c.get(url, {'format': fmt})
            self.valid_response(url, response, content_type=encoding)

    def test_detailed(self):
        c = APIClient()
        url = '/tests/weatherstation/'
        response = c.get(url, {'format': 'json', 'detailed': True})
        self.valid_response(url, response, 'application/json')
        data = response.json()
        self.assertEqual(data['results'][0]['detailed'], 'I am detailed')

    def test_weatherstation_endpoint(self):
        c = APIClient()
        response = c.get('/tests/weatherstation/', {'format': 'json'})
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)

        # check that the basics look good for list endpoint
        self.assertEqual(payload['count'], 1)
        self.assertEqual(len(payload['results']), 1)
        self.assertEqual(
            payload['_links']['self']['href'],
            'http://testserver/tests/weatherstation/?format=json'
        )

        # check that we can follow the link to the detail endpoint
        detail_page = payload['results'][0]['_links']['self']['href']

        response = c.get(detail_page, format='json')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(
            payload['_links']['self']['href'],
            detail_page
        )
        self.assertEqual(payload['number'], 260)

    def test_hal_style_pagination(self):
        c = APIClient()
        response = c.get('/tests/weatherstation/', format='json')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)

        self.assertIn('_links', payload)
        self.assertEqual(
            payload['_links']['self']['href'],
            'http://testserver/tests/weatherstation/'
        )
        self.assertEqual(payload['_links']['next']['href'], None)
        self.assertEqual(payload['_links']['previous']['href'], None)

    def test_display_field(self):
        ws = WeatherStation.objects.get(number__exact=260)
        serializer = TestDisplayFieldSerializer(ws)
        self.assertEquals(
            serializer.data['_display'],
            'DISPLAY FIELD CONTENT'
        )
