from __future__ import absolute_import
import responses

VALUES = [
    ('43.69448', '6.85575', 'FR', '720'),
    ('52.06453', '9.32880', 'DE', '79'),
    ('52.06255', '9.34737', 'DE', '73'),
    ('52.06313', '9.32412', 'DE', '79'),
    ('52.07567', '9.35367', 'DE', '126'),
    ('52.08638', '9.50065', 'DE', '130'),
    ('52.07258', '9.35628', 'DE', '154'),
    ('43.69363', '6.86093', 'FR', '759'),
    ('43.67920', '6.85293', 'FR', '699'),
    ('43.70423', '6.86983', 'FR', '1105'),
    ('43.70177', '6.84085', 'FR', '705'),
    ('0.00000', '0.00000', '', 'None'),
    ('43.78000', '7.06000', 'FR', '996'),
    ('43.79000', '7.06000', 'FR', '997'),
    ('0.00000', '1.00000', '', 'None'),
    ('1.00000', '0.00000', '', 'None'),
]


class ResponsesMixin(object):
    def setUp(self):
        assert responses, 'responses package required to use ResponsesMixin'
        responses.start()
        for lat, lon, country, elevation in VALUES:
            responses.add(responses.GET, 'https://geo.kumy.org/api/getCountry?lat={}&lon={}'.format(lat, lon),
                          status=200, body=country, match_querystring=True)
            responses.add(responses.GET, 'https://geo.kumy.org/api/getElevation?lat={}&lon={}'.format(lat, lon),
                          status=200, body=elevation, match_querystring=True)

        responses.add(responses.GET, 'https://geo.kumy.org/api/getCountry?lat=42.00000&lon=42.00000',
                      status=400, match_querystring=True)
        responses.add(responses.GET, 'https://geo.kumy.org/api/getElevation?lat=42.00000&lon=42.00000',
                      status=500, match_querystring=True)

        responses.add(responses.GET, 'https://geo.kumy.org/api/getCountry?lat=None&lon=None',
                      status=500, match_querystring=True)
        responses.add(responses.GET, 'https://geo.kumy.org/api/getElevation?lat=None&lon=None',
                      status=500, match_querystring=True)

        responses.add(responses.GET, 'https://geo.kumy.org/api/getCountry?lat=0.00000&lon=None',
                      status=500, match_querystring=True)
        responses.add(responses.GET, 'https://geo.kumy.org/api/getElevation?lat=0.00000&lon=None',
                      status=500, match_querystring=True)
        responses.add(responses.GET, 'https://geo.kumy.org/api/getCountry?lat=None&lon=0.00000',
                      status=500, match_querystring=True)
        responses.add(responses.GET, 'https://geo.kumy.org/api/getElevation?lat=None&lon=0.00000',
                      status=500, match_querystring=True)

        super(ResponsesMixin, self).setUp()

    def tearDown(self):
        super(ResponsesMixin, self).tearDown()
        responses.stop()
        responses.reset()
