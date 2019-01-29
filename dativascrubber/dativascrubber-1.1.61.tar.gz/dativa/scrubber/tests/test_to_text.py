# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
# Usage subject to license agreement
# hello@dativa.com for more information

from dativa.scrubber.tests import _BaseTest
from dativa.scrubber import ScrubberValidationError


class StringTests(_BaseTest):

    def test_to_text(self):
        bucket = "test-bucket"

        business_rules = [
            {'rule_type': 'Date',
             'field': 'timestamp',
             'params': {'fallback_mode': 'remove_record',
                        'skip_blank': False,
                        'date_format': '%Y-%m-%d %H:%M:%S'}},
            {'rule_type': 'String',
             'field': 'discount',
             'params': {'fallback_mode': 'remove_record',
                        'minimum_length': 0,
                        'maximum_length': 1}},
            {'rule_type': 'String',
             'field': 'custState',
             'params': {'fallback_mode': 'remove_record',
                        'minimum_length': 0,
                        'maximum_length': 2,
                        'skip_blank': True,
                        'regex': '(?!NY|CA)'}},
            {'rule_type': 'String',
             'field': 'expressConsent',
             'params': {'fallback_mode': 'remove_record',
                        'minimum_length': 4,
                        'skip_blank': True,
                        'maximum_length': 4,
                        'regex': '(T|t)rue'}},
            {'rule_type': 'Number',
             'field': 'latitude',
             'params': {'fallback_mode': 'remove_record',
                        'fix_decimal_places': True,
                        'decimal_places': 7,
                        'minimum_value': -90,
                        'maximum_value': 90}},
            {'rule_type': 'Number',
             'field': 'longitude',
             'params': {'fallback_mode': 'remove_record',
                        'fix_decimal_places': True,
                        'decimal_places': 7,
                        'minimum_value': -180,
                        'maximum_value': 180}},
            {'rule_type': 'String',
             'field': 'custCountry',
             'params': {'maximum_length': 3,
                        'minimum_length': 2,
                        'regex': 'US.?',
                        'fallback_mode': 'remove_record',
                        'skip_blank': True}},

            {'rule_type': 'String',
             'field': 'vin',
             'params': {'maximum_length': 17,
                        'minimum_length': 17,
                        'regex': '.{12}\d{5}',
                        'fallback_mode': 'remove_record',
                        }},
        ]
        source_params = {'minimum_length': 2,
                         'maximum_length': 5,
                         'regex': 'IDS2|GM|TOY|TOYO',
                         'fallback_mode': 'remove_record'}

        source_params_blanks = {'minimum_length': 2,
                                'maximum_length': 5,
                                'skip_blank': True,
                                'regex': 'IDS2|GM|TOY|ZCW',
                                'fallback_mode': 'remove_record'}

        date_param_blank = {'fallback_mode': 'remove_record',
                            'skip_blank': True,
                            'date_format': '%Y-%m-%d %H:%M:%S'}

        cleaning_rules = [
            {'rule_type': 'String',
             'field': 'engineOff',
             'params': {'minimum_length': 0,
                        'maximum_length': 10,
                        'regex': 'True|False',
                        'skip_blank': True,
                        'fallback_mode': 'remove_record'}},
            {'rule_type': 'Number',
             'field': 'fuelCapacity',
             'params': {'minimum_value': 0,
                        'maximum_value': 200,
                        'fallback_mode': 'remove_record',
                        'decimal_places': 1,
                        'fix_decimal_places': True}},
            {'rule_type': 'String',
             'field': 'fuelUom',
             'params': {'minimum_length': 0,
                        'maximum_length': 1024,
                        'regex': 'gal',
                        'fallback_mode': 'remove_record'}},
            {'rule_type': 'String',
             'field': 'gpsCountry',
             'params': {'minimum_length': 0,
                        'maximum_length': 25,
                        'fallback_mode': 'remove_record',
                        'skip_blank': True}},
            {'rule_type': 'Date',
             'field': 'lastCommDate',
             'params': date_param_blank},
            {'rule_type': 'Date',
             'field': 'lastUpdate',
             'params': date_param_blank},
            {'rule_type': 'String',
             'field': 'licenseCountry',
             'params': {'fallback_mode': 'remove_record',
                        'minimum_length': 2,
                        'maximum_length': 2}},
            {'rule_type': 'String',
             'field': 'make',
             'params': {'fallback_mode': 'remove_record',
                        'maximum_length': 4,
                        'minimum_length': 2}},
            {'rule_type': 'String',
             'field': 'model',
             'params': {'fallback_mode': 'remove_record',
                        'maximum_length': 4,
                        'minimum_length': 4}},
            {'rule_type': 'String',
             'field': 'mva',
             'params': {'fallback_mode': 'remove_record',
                        'maximum_length': 10,
                        'minimum_length': 8}},
            {'rule_type': 'String',
             'field': 'odometerUom',
             'params': {'maximum_length': 2,
                        'minimum_length': 2,
                        'fallback_mode': 'remove_record'}},
            {'rule_type': 'Date',
             'field': 'parkedTime',
             'params': date_param_blank},
            {'rule_type': 'String',
             'field': 'source',
             'params': source_params},
            {'rule_type': 'String',
             'field': 'tcu',
             'params': source_params},
            {'rule_type': 'Number',
             'field': 'year',
             'params': {'maximum_value': 2030,
                        'minimum_value': 2000,
                        'fallback_mode': 'remove_record',
                        'decimal_places': 0,
                        'fix_decimal_places': False}},
            {'rule_type': 'String',
             'field': 'source_fuelMetrics',
             'params': source_params_blanks},
            {'rule_type': 'String',
             'field': 'source_geoPoint',
             'params': source_params_blanks},
            {'rule_type': 'String',
             'field': 'source_odometerMetrics',
             'params': source_params_blanks},
            {'rule_type': 'String',
             'field': 'tcu_tireMetrics',
             'params': source_params_blanks},
            {'rule_type': 'String',
             'field': 'tcu_fuelMetrics',
             'params': source_params_blanks},
            {'rule_type': 'String',
             'field': 'tcu_tcuData',
             'params': source_params_blanks},
            {'rule_type': 'String',
             'field': 'tcu_geoPoint',
             'params': source_params_blanks},
            {'rule_type': 'String',
             'field': 'tcu_odometerMetrics',
             'params': source_params_blanks},
            {'rule_type': 'String',
             'field': 'tcu_rentalData',
             'params': source_params_blanks},
            {'rule_type': 'Date',
             'field': 'timestamp_tireMetrics',
             'params': date_param_blank},
            {'rule_type': 'Date',
             'field': 'timestamp_fuelMetrics',
             'params': date_param_blank},
            {'rule_type': 'Date',
             'field': 'timestamp_geoPoint',
             'params': date_param_blank},
            {'rule_type': 'Date',
             'field': 'timestamp_odometerMetrics',
             'params': date_param_blank},
            {'rule_type': 'Date',
             'field': 'timestamp_rentalData',
             'params': date_param_blank},
            {'rule_type': 'Date',
             'field': 'checkInDue',
             'params': date_param_blank},
            {'rule_type': 'Number',
             'field': 'fuel',
             'params': {'maximum_value': 200,
                        'minimum_value': 0,
                        'decimal_places': 2,
                        'fix_decimal_places': True,
                        'skip_blank': True,
                        'fallback_mode': 'remove_record'}},
            {'rule_type': 'Number',
             'field': 'fuelInEights',
             'params': {'maximum_value': 8,
                        'minimum_value': 0,
                        'skip_blank': True,
                        'decimal_places': 0,
                        'fix_decimal_places': True,
                        'fallback_mode': 'remove_record'}},
            {'rule_type': 'Number',
             'field': 'fuelInTenths',
             'params': {'maximum_value': 200,
                        'minimum_value': 0,
                        'decimal_places': 1,
                        'skip_blank': True,
                        'fix_decimal_places': True,
                        'fallback_mode': 'remove_record'}},
            {'rule_type': 'String',
             'field': 'uom_fuelMetrics',
             'params': {'maximum_length': 3,
                        'minimum_length': 1,
                        'skip_blank': True,
                        'fallback_mode': 'remove_record',
                        'regex': 'gal|l'}},
            {'rule_type': 'Number',
             'field': 'odometer',
             'params': {'maximum_value': 200000,
                        'minimum_value': 0,
                        'decimal_places': 1,
                        'fix_decimal_places': True,
                        'skip_blank': True,
                        'fallback_mode': 'remove_record'}},
            {'rule_type': 'String',
             'field': 'uom_odometerMetrics',
             'params': {'maximum_length': 2,
                        'minimum_length': 0,
                        'fallback_mode': 'remove_record',
                        'skip_blank': True,
                        'regex': 'mi|km'}},
            {'rule_type': 'String',
             'field': 'brand',
             'params': {'maximum_length': 1,
                        'minimum_length': 0,
                        'regex': 'A|B|C|P',
                        'skip_blank': True,
                        'fallback_mode': 'remove_record'}},
            {'rule_type': 'String',
             'field': 'ciLocIdentifier',
             'params': {'maximum_length': 1,
                        'minimum_length': 0,
                        'regex': 'C|A|L',
                        'skip_blank': True,
                        'fallback_mode': 'remove_record'}},
            {'rule_type': 'String',
             'field': 'coLocIdentifier',
             'params': {'maximum_length': 1,
                        'minimum_length': 0,
                        'regex': 'C|A|L',
                        'skip_blank': True,
                        'fallback_mode': 'remove_record'}},
            {'rule_type': 'String',
             'field': 'rentalStatus',
             'params': {'maximum_length': 6,
                        'minimum_length': 6,
                        'fallback_mode': 'remove_record',
                        'skip_blank': True}}
        ]

        config = dict()

        config['rules'] = business_rules + cleaning_rules

        scrubber = self.ScrubberClass()

        self.assertEquals(scrubber.to_text(config),
                          """field,type,date_format,decimal_places,fallback_mode,fix_decimal_places,maximum_length,maximum_value,minimum_length,minimum_value,regex,skip_blank
timestamp,Date,%Y-%m-%d %H:%M:%S,,remove_record,,,,,,,
discount,String,,,remove_record,,1.0,,0.0,,,
custState,String,,,remove_record,,2.0,,0.0,,(?!NY|CA),True
expressConsent,String,,,remove_record,,4.0,,4.0,,(T|t)rue,True
latitude,Number,,7.0,remove_record,True,,90.0,,-90.0,,
longitude,Number,,7.0,remove_record,True,,180.0,,-180.0,,
custCountry,String,,,remove_record,,3.0,,2.0,,US.?,True
vin,String,,,remove_record,,17.0,,17.0,,.{12}\d{5},
engineOff,String,,,remove_record,,10.0,,0.0,,True|False,True
fuelCapacity,Number,,1.0,remove_record,True,,200.0,,0.0,,
fuelUom,String,,,remove_record,,1024.0,,0.0,,gal,
gpsCountry,String,,,remove_record,,25.0,,0.0,,,True
lastCommDate,Date,%Y-%m-%d %H:%M:%S,,remove_record,,,,,,,True
lastUpdate,Date,%Y-%m-%d %H:%M:%S,,remove_record,,,,,,,True
licenseCountry,String,,,remove_record,,2.0,,2.0,,,
make,String,,,remove_record,,4.0,,2.0,,,
model,String,,,remove_record,,4.0,,4.0,,,
mva,String,,,remove_record,,10.0,,8.0,,,
odometerUom,String,,,remove_record,,2.0,,2.0,,,
parkedTime,Date,%Y-%m-%d %H:%M:%S,,remove_record,,,,,,,True
source,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|TOYO,
tcu,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|TOYO,
year,Number,,0.0,remove_record,False,,2030.0,,2000.0,,
source_fuelMetrics,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|ZCW,True
source_geoPoint,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|ZCW,True
source_odometerMetrics,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|ZCW,True
tcu_tireMetrics,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|ZCW,True
tcu_fuelMetrics,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|ZCW,True
tcu_tcuData,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|ZCW,True
tcu_geoPoint,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|ZCW,True
tcu_odometerMetrics,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|ZCW,True
tcu_rentalData,String,,,remove_record,,5.0,,2.0,,IDS2|GM|TOY|ZCW,True
timestamp_tireMetrics,Date,%Y-%m-%d %H:%M:%S,,remove_record,,,,,,,True
timestamp_fuelMetrics,Date,%Y-%m-%d %H:%M:%S,,remove_record,,,,,,,True
timestamp_geoPoint,Date,%Y-%m-%d %H:%M:%S,,remove_record,,,,,,,True
timestamp_odometerMetrics,Date,%Y-%m-%d %H:%M:%S,,remove_record,,,,,,,True
timestamp_rentalData,Date,%Y-%m-%d %H:%M:%S,,remove_record,,,,,,,True
checkInDue,Date,%Y-%m-%d %H:%M:%S,,remove_record,,,,,,,True
fuel,Number,,2.0,remove_record,True,,200.0,,0.0,,True
fuelInEights,Number,,0.0,remove_record,True,,8.0,,0.0,,True
fuelInTenths,Number,,1.0,remove_record,True,,200.0,,0.0,,True
uom_fuelMetrics,String,,,remove_record,,3.0,,1.0,,gal|l,True
odometer,Number,,1.0,remove_record,True,,200000.0,,0.0,,True
uom_odometerMetrics,String,,,remove_record,,2.0,,0.0,,mi|km,True
brand,String,,,remove_record,,1.0,,0.0,,A|B|C|P,True
ciLocIdentifier,String,,,remove_record,,1.0,,0.0,,C|A|L,True
coLocIdentifier,String,,,remove_record,,1.0,,0.0,,C|A|L,True
rentalStatus,String,,,remove_record,,6.0,,6.0,,,True
""")
