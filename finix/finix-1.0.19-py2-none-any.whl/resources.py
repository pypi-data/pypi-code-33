from __future__ import unicode_literals
from . import config
from os.path import basename

import wac


class User(config.Resource):
    type = "users"
    uri_gen = wac.URIGen("users", "")

    def create_application(self, application):
        attrs = application.__dict__.copy()
        return self.applications.create(attrs)


class Application(config.Resource):
    type = "applications"
    uri_gen = wac.URIGen("applications", "")

    def create_partner_user(self, partner):
        attrs = partner.__dict__.copy()
        return self.users.create(attrs)

    def create_processor(self, processor):
        attrs = processor.__dict__.copy()
        return self.processors.create(attrs)

    def create_token(self, token):
        attrs = token.__dict__.copy()
        return self.tokens.create(attrs)


class Processor(config.Resource):
    type = "processors"


class Merchant(config.Resource):
    type = "merchants"
    uri_gen = wac.URIGen("merchants", "")


class Identity(config.Resource):
    type = "identities"
    uri_gen = wac.URIGen("identities", "")

    def provision_merchant_on(self, merchant):
        attrs = merchant.__dict__.copy()
        return self.merchants.create(attrs)

    def create_payment_instrument(self, payment_instrument):
        attrs = payment_instrument.__dict__.copy()
        attrs["identity"] = self.id
        return self.payment_instruments.create(attrs)

    def create_settlement(self, settlement):
        attrs = settlement.__dict__.copy()
        return self.settlements.create(attrs)


class PaymentInstrument(config.Resource):
    type = "payment_instruments"
    uri_gen = wac.URIGen("payment_instruments", "")

    @classmethod
    def instance_cls(cls, **kwargs):
        if kwargs:
            instrument_type = kwargs['instrument_type'] or kwargs[type]
            if instrument_type == "PAYMENT_CARD":
                return PaymentCard
            elif instrument_type == "BANK_ACCOUNT":
                return BankAccount
        return PaymentInstrument


class PaymentCard(PaymentInstrument):
    type = None

    def __init__(self, **kwargs):
        super(PaymentInstrument, self).__init__(**kwargs)
        self.type = "PAYMENT_CARD"

    def update(self, merchant_id):
        if isinstance(merchant_id, Merchant):
            merchant_id = merchant_id.id
        return self.updates.create({'merchant': merchant_id})


class BankAccount(PaymentInstrument):
    type = None

    def __init__(self, **kwargs):
        super(PaymentInstrument, self).__init__(**kwargs)
        self.type = "BANK_ACCOUNT"


class InstrumentUpdate(config.Resource):
    type = "updates"
    uri_gen = wac.URIGen('updates', '')


class Transfer(config.Resource):
    type = "transfers"
    uri_gen = wac.URIGen("transfers", "")

    def reverse(self, refund_amount):
        refund = Refund(refund_amount=refund_amount)
        attrs = refund.__dict__.copy()
        return self.reversals.create(attrs)


class Refund(config.Resource):
    type = "reversals"


class Authorization(config.Resource):
    type = "authorizations"
    uri_gen = wac.URIGen("authorizations", "")

    def void(self):
        self.void_me = True
        return self.save()

    def capture(self, **kwargs):
        [setattr(self, k, v) for k, v in kwargs.items()]
        return self.save()


class Webhook(config.Resource):
    type = "webhooks"
    uri_gen = wac.URIGen("webhooks", "")


class Settlement(config.Resource):
    type = "settlements"
    uri_gen = wac.URIGen("settlements", "")


class Verification(config.Resource):
    type = "verifications"
    uri_gen = wac.URIGen("verifications", "")


class Dispute(config.Resource):
    type = "disputes"

    def upload_evidence(self, evidence_file_path):
        files = {'file': (basename(evidence_file_path), open(evidence_file_path, 'rb'), 'image/jpeg', {'Expires': '0'})}
        return self.evidence.create(files=files)


class Evidence(config.Resource):
    type = "evidence"


class Token(config.Resource):
    type = "tokens"


class RiskProfile(config.Resource):
    type = "risk_profiles"
    uri_gen = wac.URIGen("risk_profiles", "")


class RiskProfileRule(config.Resource):
    type = "risk_profile_rules"
    uri_gen = wac.URIGen("risk_profile_rules", "")


class ReviewQueue(config.Resource):
    type = "review_queue_items"
    uri_gen = wac.URIGen("review_queue", "")


class MerchantProfile(config.Resource):
    type = "merchant_profiles"
    uri_gen = wac.URIGen("merchant_profiles", "")


class TransferCollection(wac.ResourceCollection):
    def __init__(self, resource_cls, uri, page=None):
        super(TransferCollection, self).__init__(Transfer, uri, page)


class FundingTransfer(config.Resource):
    type = "funding_transfers"
    uri_gen = wac.URIGen("funding_transfers", "")
    collection_cls = TransferCollection


class BlackListedInstrument(config.Resource):
    type = "black_listed_instruments"
    uri_gen = wac.URIGen("black_listed_instruments", "")

    def delete(self):
        self.client.delete("/black_listed_instruments/" + self.fingerprint)

    def refresh(self):
        resp = self.client.get("/black_listed_instruments/" + self.fingerprint)
        instance = self.__class__(**resp.data)
        self.__dict__.clear()
        self.__dict__.update(instance.__dict__)
        return self
