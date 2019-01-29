import copy

import xlrd
from django import forms
from django.core.validators import validate_email as email_validator
from django.db import transaction

from ccc.contacts.models import Contact, ContactProperty
from ccc.contacts.utils import clean_phone

WINDOW_LENGTH = 1


def validate_email(email):
    email = email.strip()  # Remove spaces
    return email_validator(email)


class XLSJobImporter(object):
    def __init__(self, excel_file):
        self.file = excel_file

    def preview(self, num_of_rows=10):
        book = xlrd.open_workbook(file_contents=self.file.read())
        sheet = book.sheet_by_index(0)

        rows = []
        for i in range(min(sheet.nrows, num_of_rows)):
            rows.append(sheet.row_values(i))

        return rows

    @transaction.atomic
    def import_jobs(self):
        # Open first sheet in workbook we find
        book = xlrd.open_workbook(file_contents=self.file.read())
        sheet = book.sheet_by_index(0)

        # Load in each row as a Job entry
        curr_row = 1
        while curr_row < sheet.nrows:
            self.read_row(sheet, curr_row)
            curr_row += 1

    def validate_all(self, col_types, col_custom_names, drop_first_row):
        return self.import_all(user=None,
                               col_types=col_types,
                               col_custom_names=col_custom_names,
                               drop_first_row=drop_first_row,
                               validate_only=True)

    def import_all(
        self,
        user,
        col_types,
        col_custom_names,
        drop_first_row,
        validate_only=False,
        campaigns=[],
        groups=[]):
        book = xlrd.open_workbook(file_contents=self.file.read())
        sheet = book.sheet_by_index(0)

        invalid_rows = []

        start = drop_first_row and 1 or 0

        for row_index in range(start, sheet.nrows):
            invalid_cells = []
            raw_row = sheet.row_values(row_index)
            row = copy.deepcopy(raw_row)

            existing_contact = None

            try:
                phone_number, country = clean_phone(str(row[col_types.index('phone')]))
            except ValueError:
                pass  # no 'phone' column
            else:
                if phone_number:
                    existing_contact = Contact.objects.filter(phone=phone_number, user=user).first()

            try:
                email = row[col_types.index('email')]
                validate_email(email)
            except (ValueError, forms.ValidationError):
                pass  # no 'email' column or invalid
            else:
                if email:
                    existing_contact = Contact.objects.filter(email=email, user=user).first()

            if existing_contact:
                contact = existing_contact
            else:
                contact = Contact()
                contact.user = user
                contact.lead_type = 4

            contact_properties = []

            for col_index, col_type in enumerate(col_types):

                if col_type != 'None':
                    if col_type == 'phone':
                        row[col_index] = str(row[col_index])
                        phone_number, country = clean_phone(row[col_index])
                        contact.phone = phone_number
                        contact.country = country
                        if not phone_number:
                            invalid_cells.append(col_index)

                    elif col_type == 'email':
                        try:
                            validate_email(row[col_index])
                        except forms.ValidationError:
                            invalid_cells.append(col_index)
                        else:
                            contact.email = row[col_index]

                    elif col_type == 'custom':
                        cp = ContactProperty()
                        cp.name = col_custom_names[col_index]
                        cp.value = row[col_index]
                        contact_properties.append(cp)

                    else:
                        setattr(contact, col_type, row[col_index])

            if invalid_cells:
                row_result = [(row[i], None) for i in range(len(row))]
                for invalid_cell_index in invalid_cells:
                    row_result[invalid_cell_index] = (row_result[invalid_cell_index][0], True)

                invalid_rows.append([(row_index + 1, None)] + row_result)

            if not validate_only and not invalid_cells:
                # save contact and properties
                contact.save()
                for contact_property in contact_properties:
                    cp, created = ContactProperty.objects.get_or_create(contact=contact, name=contact_property.name)
                    cp.value = contact_property.value
                    cp.save()

                # add to campaigns
                for campaign in campaigns:
                    contact.campaigns.add(campaign)

                # add to groups
                for group in groups:
                    group.contacts.add(contact)

        if validate_only or invalid_cells:
            return invalid_rows
        else:
            return drop_first_row and sheet.nrows - 1 or sheet.nrows
