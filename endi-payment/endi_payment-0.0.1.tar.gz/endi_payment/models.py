# -*- coding: utf-8 -*-
import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    DateTime,
)
from autonomie_base.models.base import default_table_args
from endi_payment.database import ModelBase


class EndiPaymentHistory(ModelBase):
    __tablename__ = "endi_payment_history"
    __table_args__ = default_table_args
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    # ADD/UPDATE/DELETE
    action_type = Column(String(6))
    # Original payment instance id
    payment_id = Column(Integer, nullable=False)
    # Payment mode
    mode = Column(String(50))
    # The amount of the payment (* 10 000)
    amount = Column(BigInteger(), nullable=False)
    # The string identifying the bank remittance id
    bank_remittance_id = Column(String(255))
    # Date the payment has been received
    date = Column(DateTime(), nullable=False)
    # The invoice database item's id
    invoice_id = Column(Integer, nullable=False)
    # The invoice PDF sha1 hash that can be used to check pdf files
    invoice_pdf_file_hash = Column(String(255), nullable=False)
    # The bank CG account
    bank_cg = Column(String(120), default="")
    # The TVA associated to the recorded payment
    tva_value = Column(Integer, nullable=False)
    # The login of the user responsible for this modification
    user_login = Column(String(64), nullable=False)
