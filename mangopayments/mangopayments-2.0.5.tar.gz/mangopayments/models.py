import base64
from datetime import datetime
from datetime import time
from decimal import Decimal, ROUND_FLOOR

import pytz
from model_utils.managers import InheritanceManager
from django_countries.fields import CountryField
from localflavor.generic.models import IBANField, BICField

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.postgres.fields import JSONField

from mangopay.resources import User, NaturalUser, LegalUser, DirectPayIn, BankWirePayIn, BankAccount, Wallet, Page, \
    Document, PayIn, PayInRefund, Transfer, CardRegistration, Money, Card, BankWirePayOut
from mangopay.utils import Address
from .constants import (INCOME_RANGE_CHOICES,
                        STATUS_CHOICES, DOCUMENT_TYPE_CHOICES,
                        CREATED, STATUS_CHOICES_DICT, NATURAL_USER,
                        DOCUMENT_TYPE_CHOICES_DICT, USER_TYPE_CHOICES,
                        VALIDATED, IDENTITY_PROOF, VALIDATION_ASKED,
                        REGISTRATION_PROOF, ARTICLES_OF_ASSOCIATION,
                        TRANSACTION_STATUS_CHOICES,
                        REFUSED, BUSINESS, ORGANIZATION, SOLETRADER,
                        USER_TYPE_CHOICES_DICT,
                        MANGOPAY_BANKACCOUNT_TYPE, BANK_WIRE, CARD,
                        IBAN, BA_US_DEPOSIT_ACCOUNT_TYPES,
                        BA_NOT_IMPLEMENTED, MANGOPAY_PAYIN_CHOICES, MANGOPAY_BANKACCOUNT_TYPE_DICT)

from .client import get_handler

handler = get_handler()
auth_user_model = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


def amount_and_currency_to_mangopay_money(amount, currency):
    amount = amount.quantize(Decimal('.01'), rounding=ROUND_FLOOR) * 100
    return Money(amount=int(amount), currency=currency)


def address_to_mangopay_address(address, city, region, postal_code, country):
    if address in [None, ""] or city in [None, ""] or postal_code in [0, None] or country in [None, ""]:
        return None

    mangopay_address = Address(address_line_1=address,
                               city=city,
                               region=region,
                               postal_code=postal_code,
                               country=country)

    return mangopay_address


def date_to_datetime(date):
    if date is None:
        return None
    return datetime.combine(date, time(tzinfo=pytz.UTC))


class MangoPayUser(models.Model):
    objects = InheritanceManager()

    create_timestamp = models.DateTimeField(auto_now_add=True, null=True)
    last_edit_timestamp = models.DateTimeField(auto_now=True, null=True)

    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(auth_user_model, related_name="mangopay_users", on_delete=models.PROTECT)
    type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES,
                            null=True)
    first_name = models.CharField(null=True, blank=True, max_length=99)
    last_name = models.CharField(null=True, blank=True, max_length=99)
    email = models.EmailField(max_length=254, blank=True, null=True)

    # Light Authentication Field:
    birthday = models.DateField(blank=True, null=True)
    country_of_residence = CountryField()
    nationality = CountryField()

    # Regular Authentication Fields:
    address = models.CharField(blank=True, null=True, max_length=254)
    city = models.CharField(blank=True, null=True, max_length=255)
    region = models.CharField(blank=True, null=True, max_length=255)
    postal_code = models.IntegerField(default=0, blank=True, null=True)
    country_code = models.CharField(blank=True, null=True, max_length=255)

    def create(self):
        mangopay_user = self._build()
        mangopay_user.save()
        self.mangopay_id = mangopay_user.get_pk()
        self.save()

    def update(self):
        mangopay_user = self._build()
        mangopay_user.save()

    def get_mp_object(self):
        return User.get(self.mangopay_id)

    def is_legal(self):
        return self.type in [BUSINESS, ORGANIZATION, SOLETRADER]

    def is_natural(self):
        return self.type == NATURAL_USER

    def has_regular_authentication(self):
        return (self.has_light_authentication()
                and self._are_required_documents_validated())

    def required_documents_types_that_need_to_be_reuploaded(self):
        return [t for t in self._required_documents_types() if
                self._document_needs_to_be_reuploaded(t)]

    def _document_needs_to_be_reuploaded(self, t):
        return (self.mangopay_documents.filter(
                type=t, status=REFUSED).exists()
                and not self.mangopay_documents.filter(
                    type=t,
                    status__in=[VALIDATED, VALIDATION_ASKED]).exists()
                and not self.mangopay_documents.filter(
                    type=t, status__isnull=True).exists())

    def _build(self):
        raise NotImplemented

    def _birthday_fmt(self):
        return int(self.birthday.strftime("%s"))

    def _are_required_documents_validated(self):
        are_validated = True
        for document_type in self._required_documents_types():
            are_validated = self.mangopay_documents.filter(
                type=document_type, status=VALIDATED).exists() and are_validated
        return are_validated

    def has_light_authentication(self):
        raise NotImplemented

    def _required_documents_types(self):
        raise NotImplemented

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def _first_name(self):
        if self.first_name:
            return self.first_name
        try:
            return self.user.first_name
        except AttributeError:
            pass
        return ''

    @property
    def _last_name(self):
        if self.last_name:
            return self.last_name
        try:
            return self.user.last_name
        except AttributeError:
            pass
        return ''

    @property
    def _email(self):
        if self.email:
            return self.email
        try:
            return self.user.email
        except AttributeError:
            pass
        return ''


class MangoPayNaturalUser(MangoPayUser):
    # Regular Authenication Fields:
    occupation = models.CharField(blank=True, null=True, max_length=254)
    income_range = models.SmallIntegerField(blank=True, null=True, choices=INCOME_RANGE_CHOICES)

    def _build(self):
        mangopay_user = NaturalUser(first_name=self._first_name,
                                    last_name=self._last_name,
                                    email=self._email,
                                    birthday=self._birthday_fmt(),
                                    country_of_residence=self.country_of_residence.code,
                                    nationality=self.nationality.code,
                                    occupation=self.occupation,
                                    income_range=self.income_range,
                                    address=address_to_mangopay_address(self.address, self.city, self.region,
                                                                        self.postal_code, self.country_code),
                                    id=self.mangopay_id)
        return mangopay_user

    def get_mp_object(self):
        return NaturalUser.get(self.mangopay_id)

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    def save(self, *args, **kwargs):
        self.type = NATURAL_USER
        return super(MangoPayNaturalUser, self).save(*args, **kwargs)

    def has_light_authentication(self):
        return (self.user
                and self.country_of_residence
                and self.nationality
                and self.birthday)

    def has_regular_authentication(self):
        return (self.address
                and self.occupation
                and self.income_range
                and super(MangoPayNaturalUser, self).has_regular_authentication())

    def _required_documents_types(self):
        return [IDENTITY_PROOF]


class MangoPayLegalUser(MangoPayUser):
    business_name = models.CharField(max_length=254)
    generic_business_email = models.EmailField(max_length=254)

    # Regular Authenication Fields:
    headquarters_address = models.CharField(blank=True, max_length=254, null=True)
    headquarters_city = models.CharField(blank=True, null=True, max_length=255)
    headquarters_region = models.CharField(blank=True, null=True, max_length=255)
    headquarters_postal_code = models.IntegerField(default=0, blank=True, null=True)
    headquarters_country_code = models.CharField(blank=True, null=True, max_length=255)

    def _build(self):
        mangopay_user = LegalUser(name=self.business_name,
                                  email=self.generic_business_email,
                                  legal_person_type=USER_TYPE_CHOICES_DICT[self.type],
                                  headquarters_address=address_to_mangopay_address(self.headquarters_address,
                                                                                   self.headquarters_city,
                                                                                   self.headquarters_region,
                                                                                   self.headquarters_postal_code,
                                                                                   self.headquarters_country_code),
                                  legal_representative_first_name=self.first_name,
                                  legal_representative_last_name=self.last_name,
                                  legal_representative_address=address_to_mangopay_address(self.address,
                                                                                           self.city,
                                                                                           self.region,
                                                                                           self.postal_code,
                                                                                           self.country_code),
                                  legal_representative_email=self.email,
                                  legal_representative_birthday=self._birthday_fmt(),
                                  legal_representative_nationality=self.nationality.code,
                                  legal_representative_country_of_residence=self.country_of_residence.code,
                                  id=self.mangopay_id)
        return mangopay_user

    def get_mp_object(self):
        return LegalUser.get(self.mangopay_id)

    def has_light_authentication(self):
        return (self.type
                and self.business_name
                and self.generic_business_email
                and self.first_name
                and self.last_name
                and self.country_of_residence
                and self.nationality
                and self.birthday)

    def has_regular_authentication(self):
        return (self.address
                and self.headquarters_address
                and self.email
                and super(MangoPayLegalUser, self).has_regular_authentication())

    def _required_documents_types(self):
        types = [IDENTITY_PROOF, REGISTRATION_PROOF]
        if self.type in [BUSINESS, ORGANIZATION]:
            types.append(ARTICLES_OF_ASSOCIATION)
        return types

    def __str__(self):
        return "%s" % self.business_name


class MangoPayDocument(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(MangoPayUser, related_name="mangopay_documents", on_delete=models.PROTECT)
    type = models.CharField(max_length=25,
                            choices=DOCUMENT_TYPE_CHOICES)
    status = models.CharField(blank=True, null=True, max_length=25,
                              choices=STATUS_CHOICES)
    refused_reason_message = models.CharField(null=True, blank=True,
                                              max_length=255)

    def create(self, tag=''):
        user = User(id=self.mangopay_user.mangopay_id)
        document = Document(tag=tag,
                            type=DOCUMENT_TYPE_CHOICES_DICT[self.type],
                            user=user)
        document.save()
        self.mangopay_id = document.get_pk()
        self.status = STATUS_CHOICES_DICT[document.status]
        self.save()

    def update_from_mp(self):
        document = Document.get(self.mangopay_id)
        self.refused_reason_message = document.refused_reason_type
        self.status = STATUS_CHOICES_DICT[document.status]
        self.save()
        return self

    def ask_for_validation(self):
        if self.status == CREATED:
            document = Document(id=self.mangopay_id)
            document.status = "VALIDATION_ASKED"
            document.save()
            self.status = STATUS_CHOICES_DICT[document.status]
            self.save()
        else:
            raise BaseException('Cannot ask for validation of a document'
                                'not in the created state')

    def __str__(self):
        return str(self.mangopay_id) + " " + str(self.status)


class MangoPayPage(models.Model):
    document = models.ForeignKey(MangoPayDocument, related_name="mangopay_pages", on_delete=models.PROTECT)

    def create(self, page_file, tag=''):
        document = Document(id=self.document.mangopay_id)
        user = User(id=self.document.mangopay_user.mangopay_id)
        page = Page(tag=tag,
                    user=user,
                    document=document,
                    file=_file_encode(page_file))
        page.save()


def _file_encode(file_document):
    return base64.b64encode(file_document.read())


class MangoPayBankAccount(models.Model):
    mangopay_user = models.ForeignKey(MangoPayUser, related_name="mangopay_bank_accounts", on_delete=models.PROTECT)
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    owner_name = models.CharField(max_length=255, default="")

    address = models.CharField(max_length=254, default="")
    city = models.CharField(max_length=255, default="")
    postal_code = models.IntegerField(default=0)
    region = models.CharField(max_length=255, null=True, blank=True)
    country_code = models.CharField(max_length=255, default="")
    account_type = models.CharField(max_length=5,
                                    choices=MANGOPAY_BANKACCOUNT_TYPE,
                                    default=IBAN)  # Defaults to IBAN type

    iban = IBANField(blank=True, null=True)
    bic = BICField(blank=True, null=True)
    account_number = models.CharField(max_length=15, null=True, blank=True)

    # BA_US type only fields
    aba = models.CharField(max_length=9, null=True, blank=True)
    deposit_account_type = models.CharField(choices=BA_US_DEPOSIT_ACCOUNT_TYPES,
                                            max_length=8, null=True, blank=True,)

    def create(self):
        if self.account_type in BA_NOT_IMPLEMENTED:
            raise NotImplementedError(
                "Bank Account Type ({0}) not implemeneted.".format(
                    self.account_type))
        mangopay_bank_account = self._build()
        mangopay_bank_account.save()
        self.mangopay_id = mangopay_bank_account.get_pk()
        self.save()

    def _build(self):
        user = User(id=self.mangopay_user.mangopay_id)
        bank_account = BankAccount(user=user,
                                   owner_name=self.owner_name,
                                   owner_address=address_to_mangopay_address(self.address,
                                                                             self.city,
                                                                             self.region,
                                                                             self.postal_code,
                                                                             self.country_code),
                                   type=MANGOPAY_BANKACCOUNT_TYPE_DICT[self.account_type],
                                   iban=self.iban,
                                   bic=self.bic,
                                   account_number=self.account_number,
                                   aba=self.aba,
                                   deposit_account_type=self.deposit_account_type,
                                   id=self.mangopay_id)
        return bank_account

    def is_active(self):
        return BankAccount.get(self.mangopay_id, handler=handler, user_id=self.mangopay_user.mangopay_id).active

    def deactivate(self):
        return BankAccount(id=self.mangopay_id, handler=handler, user_id=self.mangopay_user.mangopay_id).deactivate()


class MangoPayWallet(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(MangoPayUser, related_name="mangopay_wallets", on_delete=models.PROTECT)
    currency = models.CharField(max_length=3, default="EUR")

    def create(self, description):
        user = User(id=self.mangopay_user.mangopay_id)
        mangopay_wallet = Wallet(owners=[user],
                                 description=description,
                                 currency=self.currency)
        mangopay_wallet.save()
        self.mangopay_id = mangopay_wallet.get_pk()
        self.save()

    def balance(self):
        wallet = Wallet.get(self.mangopay_id)
        return float(wallet.balance.amount) / 100, wallet.balance.currency

    def __str__(self):
        return "%s %s" % (self.mangopay_user.first_name, self.mangopay_user.last_name)


class MangoPayPayIn(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(MangoPayUser, related_name="mangopay_payins", on_delete=models.PROTECT)
    mangopay_wallet = models.ForeignKey(MangoPayWallet, related_name="mangopay_payins", on_delete=models.PROTECT)

    execution_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9, choices=TRANSACTION_STATUS_CHOICES,
                              blank=True, null=True)
    debited_funds = models.DecimalField(default=Decimal('0.0'), decimal_places=2, max_digits=12)
    fees = models.DecimalField(default=Decimal('0.0'), decimal_places=2, max_digits=12)
    currency = models.CharField(max_length=255, default="EUR")
    result_code = models.CharField(null=True, blank=True, max_length=6)
    result_message = models.CharField(null=True, blank=True, max_length=255)
    type = models.CharField(null=False, blank=False, choices=MANGOPAY_PAYIN_CHOICES, max_length=20, default=CARD)

    # Pay in by card via web - mangopay_card needs custom validation so it's not null on save
    mangopay_card = models.ForeignKey("MangoPayCard", related_name="mangopay_payins", null=True, blank=True,
                                      on_delete=models.PROTECT)
    secure_mode_redirect_url = models.URLField(null=True, blank=True)

    # Pay in via bank wire
    wire_reference = models.CharField(null=True, blank=True, max_length=50)
    mangopay_bank_account = JSONField(null=True, blank=True)

    def create(self):
        raise NotImplemented

    def get_mp_object(self):
        return PayIn.get(self.mangopay_id)

    def update_from_mp(self, pay_in=None):
        if pay_in is None:
            pay_in = self.get_mp_object()
        self.execution_date = date_to_datetime(pay_in.execution_date)
        self.status = pay_in.status
        self.result_code = pay_in.result_code
        self.result_message = pay_in.result_message
        self.save()

    def __str__(self):
        return "%s %s" % (self.mangopay_user.first_name, self.mangopay_user.last_name)


class MangoPayPayInByCard(MangoPayPayIn):

    class Meta:
        proxy = True

    def create(self, secure_mode_return_url):
        user = User(id=self.mangopay_user.mangopay_id)
        wallet = Wallet(id=self.mangopay_wallet.mangopay_id)
        card = Card(id=self.mangopay_card.mangopay_id)
        pay_in = DirectPayIn(author=user,
                             credited_wallet=wallet,
                             secure_mode_return_url=secure_mode_return_url,
                             card=card,
                             debited_funds=amount_and_currency_to_mangopay_money(self.debited_funds, self.currency),
                             fees=amount_and_currency_to_mangopay_money(self.fees, self.currency)
                             )
        pay_in.save()
        self.mangopay_id = pay_in.id
        self.save()
        self.update_from_mp(pay_in)

    def update_from_mp(self, pay_in):
        self.secure_mode_redirect_url = pay_in.secure_mode_redirect_url
        return super(MangoPayPayInByCard, self).update_from_mp(pay_in)

    def save(self, *args, **kwargs):
        self.type = CARD
        if self.mangopay_card is None:
            raise ValidationError("mangopay_card field is required for MangoPayPayInByCard.")
        return super(MangoPayPayInByCard, self).save(*args, **kwargs)


class MangoPayPayInBankWire(MangoPayPayIn):

    class Meta:
        proxy = True

    def create(self):
        user = User(id=self.mangopay_user.mangopay_id)
        wallet = Wallet(id=self.mangopay_wallet.mangopay_id)
        pay_in = BankWirePayIn(author=user,
                               credited_wallet=wallet,
                               declared_debited_funds=amount_and_currency_to_mangopay_money(self.debited_funds,
                                                                                            self.currency),
                               declared_fees=amount_and_currency_to_mangopay_money(self.fees, self.currency))
        pay_in.save()
        self.mangopay_id = pay_in.get_pk()
        self.update_from_mp(pay_in)

    def update_from_mp(self, pay_in):
        self.wire_reference = pay_in.wire_reference
        self.mangopay_bank_account = pay_in.bank_account
        self.debited_funds = pay_in.debited_funds
        self.fees = pay_in.fees

        return super(MangoPayPayInBankWire, self).update_from_mp(pay_in)

    def save(self, *args, **kwargs):
        self.type = BANK_WIRE
        return super(MangoPayPayInBankWire, self).save(*args, **kwargs)


class MangoPayPayOut(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(MangoPayUser, related_name="mangopay_payouts", on_delete=models.PROTECT)
    mangopay_wallet = models.ForeignKey(MangoPayWallet, related_name="mangopay_payouts", on_delete=models.PROTECT)
    mangopay_bank_account = models.ForeignKey(MangoPayBankAccount, related_name="mangopay_payouts", on_delete=models.PROTECT)
    execution_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9, choices=TRANSACTION_STATUS_CHOICES,
                              blank=True, null=True)
    debited_funds = models.DecimalField(default=Decimal('0.0'), decimal_places=2, max_digits=12)
    fees = models.DecimalField(default=Decimal('0.0'), decimal_places=2, max_digits=12)
    currency = models.CharField(max_length=255, default="EUR")
    bank_wire_ref = models.CharField(max_length=12, null=True, blank=True, default="")

    result_code = models.CharField(null=True, blank=True, max_length=6)
    result_message = models.CharField(null=True, blank=True, max_length=255)

    def create(self):
        author = User(id=self.mangopay_user.mangopay_id)
        debited_wallet = Wallet(id=self.mangopay_wallet.mangopay_id)
        bank_account = BankAccount(id=self.mangopay_bank_account.mangopay_id, handler=handler,
                                       user_id=self.mangopay_bank_account.mangopay_user.mangopay_id)
        pay_out = BankWirePayOut(author=author,
                                 debited_funds=amount_and_currency_to_mangopay_money(self.debited_funds, self.currency),
                                 fees=amount_and_currency_to_mangopay_money(self.fees, self.currency),
                                 debited_wallet=debited_wallet,
                                 bank_account=bank_account,
                                 bank_wire_ref=self.bank_wire_ref)
        pay_out.save()
        self.mangopay_id = pay_out.get_pk()
        self.save()
        return self.update_from_mp(pay_out)

    def get_mp_object(self):
        if not self.mangopay_id:
            raise ValueError("PayOut need a mangopay id to be retrieved from MangoPay's API.")
        return BankWirePayOut.get(self.mangopay_id)

    def update_from_mp(self, pay_out=None):
        if pay_out is None:
            pay_out = self.get_mp_object()
        self.execution_date = date_to_datetime(pay_out.execution_date)
        self.status = pay_out.status
        self.result_code = pay_out.result_code
        self.result_message = pay_out.result_message
        self.save()
        return self

    def __str__(self):
        return "%s %s" % (self.mangopay_user.first_name, self.mangopay_user.last_name)


class MangoPayCard(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(auth_user_model, related_name="mangopay_cards", on_delete=models.PROTECT)
    expiration_date = models.CharField(blank=True, null=True, max_length=4)
    alias = models.CharField(blank=True, null=True, max_length=19)
    provider = models.CharField(blank=True, null=True, max_length=255)
    type = models.CharField(blank=True, null=True, max_length=255)
    is_active = models.BooleanField(default=False)
    is_valid = models.NullBooleanField()

    deleted = models.BooleanField(default=False)

    def update_from_mp(self):
        if self.mangopay_id:
            card = Card.get(self.mangopay_id)
            self.expiration_date = card.expiration_date
            self.alias = card.alias
            self.is_active = card.active
            self.provider = card.card_provider
            self.type = card.card_type
            if card.validity == "UNKNOWN":
                self.is_valid = None
            else:
                self.is_valid = card.Validity == "VALID"
            self.save()

    def __str__(self):
        return str(self.pk)


class MangoPayCardRegistration(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(MangoPayUser, related_name="mangopay_card_registrations", on_delete=models.PROTECT)
    mangopay_card = models.OneToOneField(MangoPayCard, null=True, blank=True, related_name="mangopay_card_registration",
                                         on_delete=models.PROTECT)

    def create(self, currency, card_type):
        user = User(id=self.mangopay_user.mangopay_id)
        card_registration = CardRegistration(user=user,
                                             currency=currency,
                                             card_type=card_type)
        card_registration.save()
        self.mangopay_id = card_registration.get_pk()
        self.save()

    def get_preregistration_data(self):
        card_registration = CardRegistration.get(self.mangopay_id)
        preregistration_data = {
            "preregistrationData": card_registration.preregistration_data,
            "accessKey": card_registration.access_key,
            "cardRegistrationURL": card_registration.card_registration_url}
        return preregistration_data

    def save_mangopay_card_id(self, mangopay_card_id):
        self.mangopay_card.mangopay_id = mangopay_card_id
        self.mangopay_card.save()

    def save(self, *args, **kwargs):
        if not self.mangopay_card:
            mangopay_card = MangoPayCard()
            mangopay_card.user = self.mangopay_user.user
            mangopay_card.save()
            self.mangopay_card = mangopay_card
        super(MangoPayCardRegistration, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s" % (self.mangopay_user.first_name, self.mangopay_user.last_name)


class MangoPayRefund(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_user = models.ForeignKey(MangoPayUser, related_name="mangopay_refunds", on_delete=models.PROTECT)
    mangopay_pay_in = models.ForeignKey(MangoPayPayIn, related_name="mangopay_refunds", on_delete=models.PROTECT)
    debited_funds = models.DecimalField(default=Decimal('0.0'), decimal_places=2, max_digits=12)
    fees = models.DecimalField(default=Decimal('0.0'), decimal_places=2, max_digits=12)

    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)

    status = models.CharField(max_length=9, choices=TRANSACTION_STATUS_CHOICES,
                              blank=True, null=True)
    result_code = models.CharField(null=True, blank=True, max_length=6)
    result_message = models.CharField(null=True, blank=True, max_length=255)

    execution_date = models.DateTimeField(blank=True, null=True)

    def create(self, refund_reason=''):
        payin = PayIn(id=self.mangopay_pay_in.mangopay_id)
        user = User(id=self.mangopay_user.mangopay_id)
        refund = PayInRefund(payin=payin,
                             author=user,
                             debited_funds=amount_and_currency_to_mangopay_money(self.debited_funds,
                                                                                 self.mangopay_pay_in.currency),
                             fees=amount_and_currency_to_mangopay_money(self.fees, self.mangopay_pay_in.currency),
                             refund_reason=refund_reason)
        refund.save()
        self.mangopay_id = refund.get_pk()
        self.status = refund.status
        self.result_code = refund.result_code
        self.result_message = refund.result_message
        self.execution_date = date_to_datetime(refund.execution_date)
        self.save()

    def __str__(self):
        return "%s %s" % (self.mangopay_user.first_name, self.mangopay_user.last_name)


class MangoPayTransfer(models.Model):
    mangopay_id = models.PositiveIntegerField(null=True, blank=True)
    mangopay_debited_wallet = models.ForeignKey(MangoPayWallet, related_name="mangopay_debited_wallets", on_delete=models.PROTECT)
    mangopay_credited_wallet = models.ForeignKey(MangoPayWallet, related_name="mangopay_credited_wallets", on_delete=models.PROTECT)
    debited_funds = models.DecimalField(default=Decimal('0.0'), decimal_places=2, max_digits=12)
    fees = models.DecimalField(default=Decimal('0.0'), decimal_places=2, max_digits=12)
    currency = models.CharField(max_length=255, default="EUR")
    execution_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=9, choices=TRANSACTION_STATUS_CHOICES,
                              blank=True, null=True)
    result_code = models.CharField(null=True, blank=True, max_length=6)
    result_message = models.CharField(null=True, blank=True, max_length=256)

    def create(self):
        author = User(id=self.mangopay_debited_wallet.mangopay_user.mangopay_id)
        credited_user = User(id=self.mangopay_credited_wallet.mangopay_user.mangopay_id)
        credited_wallet = Wallet(id=self.mangopay_credited_wallet.mangopay_id)
        debited_wallet = Wallet(id=self.mangopay_debited_wallet.mangopay_id)
        transfer = Transfer(credited_wallet=credited_wallet,
                            debited_wallet=debited_wallet,
                            author=author,
                            credited_user=credited_user,
                            debited_funds=amount_and_currency_to_mangopay_money(self.debited_funds, self.currency),
                            fees=amount_and_currency_to_mangopay_money(self.fees, self.currency)
                            )
        transfer.save()
        self.mangopay_id = transfer.get_pk()
        self.save()
        self.update_from_mp(transfer)

    def get_mp_object(self):
        return Transfer.get(self.mangopay_id)

    def update_from_mp(self, transfer=None):
        if transfer is None:
            transfer = self.get_mp_object()
        self.status = transfer.status
        self.result_code = transfer.result_code
        self.result_message = transfer.result_message
        self.execution_date = date_to_datetime(transfer.execution_date)
        self.save()

    def __str__(self):
        return "Debited wallet's owner %s %s" % (self.mangopay_debited_wallet.mangopay_user.first_name,
                                                 self.mangopay_debited_wallet.mangopay_user.last_name)
