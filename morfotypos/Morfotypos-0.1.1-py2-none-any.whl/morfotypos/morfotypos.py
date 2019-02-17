# -*- coding: utf-8 -*-
# Copyright 2019 bitwise.solutions <https://bitwise.solutions>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
""" Αυτη η μοναδα ειναι μια υλοποιηση του παρασρτηματος Π1 του εγγραφου που
βρισκεται στην παρακατω διευθυνση:
ttp://www.opengov.gr/minfin/wp-content/uploads/downloads/2013/06/MFS.pdf
και φερει τον τιτλο:

    ΔΟΜΗ (ΜΟΡΦΟΤΥΠΟΣ) ΤΩΝ ΗΛΕΚΤΡΟΝIΚΩΝ ΔΕΔΟΜΕΝΩΝ ΤΩΝ
    ΦΟΡΟΛΟΓΙΚΩΝ ΣΤΟΙΧΕΙΩΝ ΠΟΥ ΕΚΔΙΔΟΝΤΑΙ ΜΕ ΗΛΕΚΤΡΟΝΙΚΟΥΣ
    ΥΠΟΛΟΓΙΣΤΕΣ ΚΑΙ ΔΙΑΣΦΑΛΙΣΗ ΑΥΤΩΝ ΓΙΑ ΤΗΝ ΗΛΕΚΤΡΟΝΙΚΗ ΤΟΥΣ
    ΕΚΔΟΣΗ, ΤΗΝ ΗΛΕΚΤΡΟΝΙΚΗ ΤΟΥΣ ΑΠΟΘΗΚΕΥΣΗ ΚΑΙ ΤΗΝ
    ΗΛΕΚΤΡΟΝΙΚΗ ΤΟΥΣ ΔΙΑΒΙΒΑΣΗ

Η λειτουργια της συνοψιζεται ως εξης:
    1) Εισαγουμε τα στοιχεια προς σημανση στις μεταβλητες header, details και
    extra.
    2) Η μοναδα αναλαμβανει να δημιουργισει μια αλληλουχια χαρακτηρων και
    την επιστρεφει στον χρηστη.
    3) Αυτη η αλληλουχια χαρακτηρων που ονομαζεται Φορολογικά Δεδομένα
    Στοιχείου ειναι ετοιμη προς αποστολη στον Φορολογικο Μηχανισμο (ΕΑΦΔΣΣ)
    η/και στον Πάροχο Άυλης Φορολογικής Σήμανσης (ΠΑΦΣ)
"""
import json
from argparse import ArgumentParser
from collections import OrderedDict
from ast import literal_eval
from sys import stdout

SEPARATOR_HEADER = 'h$'
SEPARATOR_DETAILS = 'd$'
SEPARATOR_EXTRA = 'a$'
SEPARATOR_FIELD = '#'


def __validate_input_type(fields):
    _fields = None
    try:
        if type(fields) is str:
            _fields = literal_eval(fields)
        elif type(fields) is dict:
            _fields = fields
        else:
            raise ValueError
    except ValueError:
        raise Exception(
            'Header and details expects a string if called from the command '
            'line else a native Python dictionary.')
    return _fields


def _validate_numbers(fields):
    if not fields:
        raise Exception(
            'All the fields need to be filled in header and details.')
    fields = OrderedDict(fields)
    for key in fields.keys():
        key = int(key)
        if '#' in fields[key]:
            raise Exception('Illegal character')
        if key > 1:
            previous_val = fields.get(key - 1)
            if type(previous_val) is None:
                raise Exception(
                    'The field keys must be integers starting from 1 '
                    'ordered and with no empty vals between them. '
                    'All the fields must be given even if empty.')


def _validate_header(header_fields):
    fields = __validate_input_type(header_fields)
    _validate_numbers(fields)
    return fields


def _validate_details(details_fields):
    fields = __validate_input_type(details_fields)
    _validate_numbers(details_fields)
    return fields


def _validate_extra(extra_fields):
    fields = __validate_input_type(extra_fields)
    _validate_numbers(extra_fields)
    return fields


def get_fds(header, details, extra):
    header = _validate_header(header)
    details = _validate_details(details)
    extra = _validate_extra(extra)
    full = header
    full.update(details)
    full.update(extra)
    string = ''
    for key in full.keys():
        if key == 1:
            string += SEPARATOR_HEADER  # header starts
        elif key == 289:
            string += SEPARATOR_DETAILS  # details start
        elif key == 351:  # more fields exist after details
            string += SEPARATOR_EXTRA
        else:
            string += SEPARATOR_FIELD
        string += full[key]
    return string.decode('iso8859_7')


if __name__ == '__main__':
    raise Exception('Use get_fds instead.')  # TODO to be implemented.
    parser = ArgumentParser(
        description='Εκδοση Φορολογικων Δεδομένων Στοιχείου (ΦΔΣ)',
    )
    parser.add_argument(
        'header',
        help='Φορολογικά Δεδομένα Στοιχείου (ΦΔΣ) ΠΕΔΙΑ ΠΙΝΑΚΑ Α`'
             'Εδω εισαγετε τα πεδια header (συνολο 288 πεδια) με την μορφη '
             '{αριθμος_πεδιου: τιμη_πεδιου} '
             'οπου ο αριθμος πεδιου βρισκεται στον Πινακα Α` '
             'Τα πεδια με αριθμους 1 και 2 αποστελλονται αλλα δεν '
             'συμμετεχουν στην σημανση.',
        type=json.loads,
    )
    parser.add_argument(
        'details',
        help='Φορολογικα Δεδομενα Στοιχειου (ΦΔΣ) ΠΕΔΙΑ ΠΙΝΑΚΑ Β`'
             'Εδω εισαγετε τα πεδια details (συνολο 62 πεδια) με την μορφη '
             '{αριθμος_πεδιου: τιμη_πεδιου} '
             'οπου ο αριθμος πεδιου βρισκεται στον πινακα Β`',
        type=json.loads,
    )
    parser.add_argument(
        'extra',
        help='Επιπλεον πεδια που δεν συμπεριλαμβανονται στους δυο πινακες. '
             'Τα πεδια αυτα αποστελλονται μεν αλλα δεν συμμετεχουν στην '
             'σημανση.',
        type=json.loads,
    )
    args = parser.parse_args()
    stdout.write(get_fds(args.header, args.details, args.extra))
