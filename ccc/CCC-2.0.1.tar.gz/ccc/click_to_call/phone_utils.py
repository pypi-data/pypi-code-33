# -*- coding: utf-8 -*-
import phonenumbers


def is_from_usa_or_canada(country_code):
    return country_code == 1


def clean_phone_number(phone_number):
    phone = phone_number.replace('+', '')
    phone = phone.replace('-', '')

    if len(phone) == 10:
        phone = '1' + phone

    phone = "+" + phone

    try:
        phone = phonenumbers.parse(phone)
    except Exception as e:
        return phone, e

    if not is_from_usa_or_canada(phone.country_code):
        return phone, 'Invalid Country Code. Please only numbers from US & Canada. +1'

    elif len(str(phone.national_number)) > 10:
        return phone, 'Invalid National number, this should have ONLY 10 numeric digits. NO spaces, dashes, ' \
                      'or non-numeric characters'

    elif len(str(phone.national_number)) < 10:
        return phone, 'Invalid National number, this should have 10 numeric digits not less'

    return phone, False
