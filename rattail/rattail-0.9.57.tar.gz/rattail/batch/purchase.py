# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Handler for purchase order batches
"""

from __future__ import unicode_literals, absolute_import

import logging

import six
from sqlalchemy import orm

from rattail.db import model, api
from rattail.gpc import GPC
from rattail.batch import BatchHandler
from rattail.time import make_utc
from rattail.vendors.invoices import require_invoice_parser


log = logging.getLogger(__name__)


class PurchaseBatchHandler(BatchHandler):
    """
    Handler for purchase order batches.
    """
    batch_model_class = model.PurchaseBatch

    def allow_cases(self):
        """
        Must return boolean indicating whether "cases" should be generally
        allowed, for sake of quantity input etc.
        """
        return self.config.getbool('rattail.batch', 'purchase.allow_cases',
                                   default=True)

    def allow_expired_credits(self):
        """
        Must return boolean indicating whether "expired" credits should be
        tracked.  In practice, this should either en- or dis-able various UI
        elements which involves expired product.
        """
        return self.config.getbool('rattail.batch', 'purchase.allow_expired_credits',
                                   default=True)

    def should_populate(self, batch):
        # TODO: this probably should change soon, for now this works..
        return batch.purchase and batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                                                 self.enum.PURCHASE_BATCH_MODE_COSTING)

    def populate(self, batch, progress=None):
        assert batch.purchase and batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                                                 self.enum.PURCHASE_BATCH_MODE_COSTING)
        batch.order_quantities_known = True

        def append(item, i):
            row = model.PurchaseBatchRow()
            product = item.product
            row.item = item
            row.product = product
            if product:
                row.upc = product.upc
                row.item_id = product.item_id
            else:
                row.upc = item.upc
                row.item_id = item.item_id
            row.cases_ordered = item.cases_ordered
            row.units_ordered = item.units_ordered
            row.cases_received = item.cases_received
            row.units_received = item.units_received
            row.po_unit_cost = item.po_unit_cost
            row.po_total = item.po_total
            if batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
                row.invoice_unit_cost = item.invoice_unit_cost
                row.invoice_total = item.invoice_total
            self.add_row(batch, row)

        self.progress_loop(append, batch.purchase.items, progress,
                           message="Adding initial rows to batch")

        # TODO: should(n't) this be handled elsewhere?
        session = orm.object_session(batch)
        session.flush()
        self.refresh_batch_status(batch)

    def populate_from_truck_dump_invoice(self, batch, progress=None):
        parser = require_invoice_parser(batch.invoice_parser_key)

        session = orm.object_session(batch)
        parser.session = session

        parser.vendor = api.get_vendor(session, parser.vendor_key)
        if parser.vendor is not batch.vendor:
            raise RuntimeError("Parser is for vendor '{}' but batch is for: {}".format(
                parser.vendor_key, batch.vendor))

        path = batch.filepath(self.config, batch.invoice_file)
        batch.invoice_date = parser.parse_invoice_date(path)
        batch.order_quantities_known = True

        def append(invoice_row, i):
            row = self.make_row_from_invoice(batch, invoice_row)
            self.add_row(batch, row)

        self.progress_loop(append, list(parser.parse_rows(path)), progress,
                           message="Adding initial rows to batch")

        self.make_truck_dump_claims_for_child_batch(batch, progress=progress)
        self.refresh_batch_status(batch.truck_dump_batch)

    def make_row_from_invoice(self, batch, invoice_row):
        row = model.PurchaseBatchRow()
        row.item_entry = invoice_row.item_entry
        row.upc = invoice_row.upc
        row.vendor_code = invoice_row.vendor_code
        row.brand_name = invoice_row.brand_name
        row.description = invoice_row.description
        row.size = invoice_row.size
        row.case_quantity = invoice_row.case_quantity
        row.cases_ordered = invoice_row.ordered_cases
        row.units_ordered = invoice_row.ordered_units
        row.cases_shipped = invoice_row.shipped_cases
        row.units_shipped = invoice_row.shipped_units
        row.out_of_stock = invoice_row.out_of_stock
        row.invoice_unit_cost = invoice_row.unit_cost
        row.invoice_total = invoice_row.total_cost
        row.invoice_case_cost = invoice_row.case_cost
        return row

    def make_truck_dump_claims_for_child_batch(self, batch, progress=None):
        """
        Make all "claims" against a truck dump, for the given child batch.
        This assumes no claims exist for the child batch at time of calling,
        and that the truck dump batch is complete and not yet executed.
        """
        session = orm.object_session(batch)
        truck_dump_rows = batch.truck_dump_batch.active_rows()
        child_rows = batch.active_rows()

        # organize truck dump by product and UPC
        truck_dump_by_product = {}
        truck_dump_by_upc = {}

        def organize_parent(row, i):
            if row.product:
                truck_dump_by_product.setdefault(row.product.uuid, []).append(row)
            if row.upc:
                truck_dump_by_upc.setdefault(row.upc, []).append(row)

        self.progress_loop(organize_parent, truck_dump_rows, progress,
                           message="Organizing truck dump parent rows")

        # organize child batch by product and UPC
        child_by_product = {}
        child_by_upc = {}

        def organize_child(row, i):
            if row.product:
                child_by_product.setdefault(row.product.uuid, []).append(row)
            if row.upc:
                child_by_upc.setdefault(row.upc, []).append(row)

        self.progress_loop(organize_child, child_rows, progress,
                           message="Organizing truck dump child rows")

        # okay then, let's go through all our organized rows, and make claims

        def make_claims(child_product, i):
            uuid, child_product_rows = child_product
            if uuid in truck_dump_by_product:
                truck_dump_product_rows = truck_dump_by_product[uuid]
                for truck_dump_row in truck_dump_product_rows:
                    self.make_truck_dump_claims(truck_dump_row, child_product_rows)

        self.progress_loop(make_claims, child_by_product.items(), progress,
                           count=len(child_by_product),
                           message="Claiming parent rows for child") # (pass #1)

    def make_truck_dump_claims(self, truck_dump_row, child_rows):

        # first we go through the truck dump parent row, and calculate all
        # "present", and "claimed" vs. "pending" product quantities

        # cases_received
        cases_received = truck_dump_row.cases_received or 0
        cases_received_claimed = sum([claim.cases_received or 0
                                      for claim in truck_dump_row.claims])
        cases_received_pending = cases_received - cases_received_claimed

        # units_received
        units_received = truck_dump_row.units_received or 0
        units_received_claimed = sum([claim.units_received or 0
                                      for claim in truck_dump_row.claims])
        units_received_pending = units_received - units_received_claimed

        # cases_damaged
        cases_damaged = truck_dump_row.cases_damaged or 0
        cases_damaged_claimed = sum([claim.cases_damaged or 0
                                     for claim in truck_dump_row.claims])
        cases_damaged_pending = cases_damaged - cases_damaged_claimed

        # units_damaged
        units_damaged = truck_dump_row.units_damaged or 0
        units_damaged_claimed = sum([claim.units_damaged or 0
                                     for claim in truck_dump_row.claims])
        units_damaged_pending = units_damaged - units_damaged_claimed

        # cases_expired
        cases_expired = truck_dump_row.cases_expired or 0
        cases_expired_claimed = sum([claim.cases_expired or 0
                                     for claim in truck_dump_row.claims])
        cases_expired_pending = cases_expired - cases_expired_claimed

        # units_expired
        units_expired = truck_dump_row.units_expired or 0
        units_expired_claimed = sum([claim.units_expired or 0
                                     for claim in truck_dump_row.claims])
        units_expired_pending = units_expired - units_expired_claimed

        # TODO: should be calculating mispicks here too, right?

        def make_claim(child_row):
            c = model.PurchaseBatchRowClaim()
            c.claiming_row = child_row
            truck_dump_row.claims.append(c)
            return c

        for child_row in child_rows:

            # stop now if everything in this parent row is accounted for
            if not (cases_received_pending or units_received_pending
                    or cases_damaged_pending or units_damaged_pending
                    or cases_expired_pending or units_expired_pending):
                break

            # for each child row we also calculate all "present", and "claimed"
            # vs. "pending" product quantities

            # cases_ordered
            cases_ordered = child_row.cases_ordered or 0
            cases_ordered_claimed = sum([(claim.cases_received or 0)
                                         + (claim.cases_damaged or 0)
                                         + (claim.cases_expired or 0)
                                         for claim in child_row.truck_dump_claims])
            cases_ordered_pending = cases_ordered - cases_ordered_claimed

            # units_ordered
            units_ordered = child_row.units_ordered or 0
            units_ordered_claimed = sum([(claim.units_received or 0)
                                         + (claim.units_damaged or 0)
                                         + (claim.units_expired or 0)
                                         for claim in child_row.truck_dump_claims])
            units_ordered_pending = units_ordered - units_ordered_claimed

            # skip this child row if everything in it is accounted for
            if not (cases_ordered_pending or units_ordered_pending):
                continue

            # there should only be one claim for this parent/child combo
            claim = None

            # let's cache this
            case_quantity = child_row.case_quantity

            # make case claims
            if cases_ordered_pending and cases_received_pending:
                claim = claim or make_claim(child_row)
                if cases_received_pending >= cases_ordered_pending:
                    claim.cases_received = (claim.cases_received or 0) + cases_ordered_pending
                    child_row.cases_received = (child_row.cases_received or 0) + cases_ordered_pending
                    cases_received_pending -= cases_ordered_pending
                    cases_ordered_pending = 0
                else: # ordered > received
                    claim.cases_received = (claim.cases_received or 0) + cases_received_pending
                    child_row.cases_received = (child_row.cases_received or 0) + cases_received_pending
                    cases_ordered_pending -= cases_received_pending
                    cases_received_pending = 0
                self.refresh_row(child_row)
            if cases_ordered_pending and cases_damaged_pending:
                claim = claim or make_claim(child_row)
                if cases_damaged_pending >= cases_ordered_pending:
                    claim.cases_damaged = (claim.cases_damaged or 0) + cases_ordered_pending
                    child_row.cases_damaged = (child_row.cases_damaged or 0) + cases_ordered_pending
                    cases_damaged_pending -= cases_ordered_pending
                    cases_ordered_pending = 0
                else: # ordered > damaged
                    claim.cases_damaged = (claim.cases_damaged or 0) + cases_damaged_pending
                    child_row.cases_damaged = (child_row.cases_damaged or 0) + cases_damaged_pending
                    cases_ordered_pending -= cases_damaged_pending
                    cases_damaged_pending = 0
                self.refresh_row(child_row)
            if cases_ordered_pending and cases_expired_pending:
                claim = claim or make_claim(child_row)
                if cases_expired_pending >= cases_ordered_pending:
                    claim.cases_expired = (claim.cases_expired or 0) + cases_ordered_pending
                    child_row.cases_expired = (child_row.cases_expired or 0) + cases_ordered_pending
                    cases_expired_pending -= cases_ordered_pending
                    cases_ordered_pending = 0
                else: # ordered > expired
                    claim.cases_expired = (claim.cases_expired or 0) + cases_expired_pending
                    child_row.cases_expired = (child_row.cases_expired or 0) + cases_expired_pending
                    cases_ordered_pending -= cases_expired_pending
                    cases_expired_pending = 0
                self.refresh_row(child_row)

            # make unit claims
            if units_ordered_pending and units_received_pending:
                claim = claim or make_claim(child_row)
                if units_received_pending >= units_ordered_pending:
                    claim.units_received = (claim.units_received or 0) + units_ordered_pending
                    child_row.units_received = (child_row.units_received or 0) + units_ordered_pending
                    units_received_pending -= units_ordered_pending
                    units_ordered_pending = 0
                else: # ordered > received
                    claim.units_received = (claim.units_received or 0) + units_received_pending
                    child_row.units_received = (child_row.units_received or 0) + units_received_pending
                    units_ordered_pending -= units_received_pending
                    units_received_pending = 0
                self.refresh_row(child_row)
            if units_ordered_pending and units_damaged_pending:
                claim = claim or make_claim(child_row)
                if units_damaged_pending >= units_ordered_pending:
                    claim.units_damaged = (claim.units_damaged or 0) + units_ordered_pending
                    child_row.units_damaged = (child_row.units_damaged or 0) + units_ordered_pending
                    units_damaged_pending -= units_ordered_pending
                    units_ordered_pending = 0
                else: # ordered > damaged
                    claim.units_damaged = (claim.units_damaged or 0) + units_damaged_pending
                    child_row.units_damaged = (child_row.units_damaged or 0) + units_damaged_pending
                    units_ordered_pending -= units_damaged_pending
                    units_damaged_pending = 0
                self.refresh_row(child_row)
            if units_ordered_pending and units_expired_pending:
                claim = claim or make_claim(child_row)
                if units_expired_pending >= units_ordered_pending:
                    claim.units_expired = (claim.units_expired or 0) + units_ordered_pending
                    child_row.units_expired = (child_row.units_expired or 0) + units_ordered_pending
                    units_expired_pending -= units_ordered_pending
                    units_ordered_pending = 0
                else: # ordered > expired
                    claim.units_expired = (claim.units_expired or 0) + units_expired_pending
                    child_row.units_expired = (child_row.units_expired or 0) + units_expired_pending
                    units_ordered_pending -= units_expired_pending
                    units_expired_pending = 0
                self.refresh_row(child_row)

            # claim units from parent, as cases for child.  note that this
            # crosses the case/unit boundary, but is considered "safe" because
            # we assume the child row has correct case quantity even if parent
            # row has a different one.
            if cases_ordered_pending and units_received_pending:
                received = units_received_pending // case_quantity
                if received:
                    claim = claim or make_claim(child_row)
                    if received >= cases_ordered_pending:
                        claim.cases_received = (claim.cases_received or 0) + cases_ordered_pending
                        child_row.cases_received = (child_row.units_received or 0) + cases_ordered_pending
                        units_received_pending -= (cases_ordered_pending * case_quantity)
                        cases_ordered_pending = 0
                    else: # ordered > received
                        claim.cases_received = (claim.cases_received or 0) + received
                        child_row.cases_received = (child_row.units_received or 0) + received
                        cases_ordered_pending -= received
                        units_received_pending -= (received * case_quantity)
                    self.refresh_row(child_row)
            if cases_ordered_pending and units_damaged_pending:
                damaged = units_damaged_pending // case_quantity
                if damaged:
                    claim = claim or make_claim(child_row)
                    if damaged >= cases_ordered_pending:
                        claim.cases_damaged = (claim.cases_damaged or 0) + cases_ordered_pending
                        child_row.cases_damaged = (child_row.units_damaged or 0) + cases_ordered_pending
                        units_damaged_pending -= (cases_ordered_pending * case_quantity)
                        cases_ordered_pending = 0
                    else: # ordered > damaged
                        claim.cases_damaged = (claim.cases_damaged or 0) + damaged
                        child_row.cases_damaged = (child_row.units_damaged or 0) + damaged
                        cases_ordered_pending -= damaged
                        units_damaged_pending -= (damaged * case_quantity)
                    self.refresh_row(child_row)
            if cases_ordered_pending and units_expired_pending:
                expired = units_expired_pending // case_quantity
                if expired:
                    claim = claim or make_claim(child_row)
                    if expired >= cases_ordered_pending:
                        claim.cases_expired = (claim.cases_expired or 0) + cases_ordered_pending
                        child_row.cases_expired = (child_row.units_expired or 0) + cases_ordered_pending
                        units_expired_pending -= (cases_ordered_pending * case_quantity)
                        cases_ordered_pending = 0
                    else: # ordered > expired
                        claim.cases_expired = (claim.cases_expired or 0) + expired
                        child_row.cases_expired = (child_row.units_expired or 0) + expired
                        cases_ordered_pending -= expired
                        units_expired_pending -= (expired * case_quantity)
                    self.refresh_row(child_row)

            # if necessary, try to claim cases from parent, as units for child.
            # this also crosses the case/unit boundary but is considered safe
            # only if the case quantity matches between child and parent rows.
            # (otherwise who knows what could go wrong.)
            if case_quantity == truck_dump_row.case_quantity:
                if units_ordered_pending and cases_received_pending:
                    received = cases_received_pending * case_quantity
                    claim = claim or make_claim(child_row)
                    if received >= units_ordered_pending:
                        claim.units_received = (claim.units_received or 0) + units_ordered_pending
                        child_row.units_received = (child_row.units_received or 0) + units_ordered_pending
                        leftover = received % units_ordered_pending
                        if leftover == 0:
                            cases_received_pending -= (received // units_ordered_pending)
                        else:
                            cases_received_pending -= (received // units_ordered_pending) - 1
                            units_received_pending += leftover
                        units_ordered_pending = 0
                    else: # ordered > received
                        claim.units_received = (claim.units_received or 0) + received
                        child_row.units_received = (child_row.units_received or 0) + received
                        units_ordered_pending -= received
                        cases_received_pending = 0
                    self.refresh_row(child_row)
                if units_ordered_pending and cases_damaged_pending:
                    damaged = cases_damaged_pending * case_quantity
                    claim = claim or make_claim(child_row)
                    if damaged >= units_ordered_pending:
                        claim.units_damaged = (claim.units_damaged or 0) + units_ordered_pending
                        child_row.units_damaged = (child_row.units_damaged or 0) + units_ordered_pending
                        leftover = damaged % units_ordered_pending
                        if leftover == 0:
                            cases_damaged_pending -= (damaged // units_ordered_pending)
                        else:
                            cases_damaged_pending -= (damaged // units_ordered_pending) - 1
                            units_damaged_pending += leftover
                        units_ordered_pending = 0
                    else: # ordered > damaged
                        claim.units_damaged = (claim.units_damaged or 0) + damaged
                        child_row.units_damaged = (child_row.units_damaged or 0) + damaged
                        units_ordered_pending -= damaged
                        cases_damaged_pending = 0
                    self.refresh_row(child_row)
                if units_ordered_pending and cases_expired_pending:
                    expired = cases_expired_pending * case_quantity
                    claim = claim or make_claim(child_row)
                    if expired >= units_ordered_pending:
                        claim.units_expired = (claim.units_expired or 0) + units_ordered_pending
                        child_row.units_expired = (child_row.units_expired or 0) + units_ordered_pending
                        leftover = expired % units_ordered_pending
                        if leftover == 0:
                            cases_expired_pending -= (expired // units_ordered_pending)
                        else:
                            cases_expired_pending -= (expired // units_ordered_pending) - 1
                            units_expired_pending += leftover
                        units_ordered_pending = 0
                    else: # ordered > expired
                        claim.units_expired = (claim.units_expired or 0) + expired
                        child_row.units_expired = (child_row.units_expired or 0) + expired
                        units_ordered_pending -= expired
                        cases_expired_pending = 0
                    self.refresh_row(child_row)

            # refresh the parent row, to reflect any new claim(s) made
            self.refresh_row(truck_dump_row)

    def clone_truck_dump_credit(self, truck_dump_credit, child_row):
        """
        Clone a credit record from a truck dump, onto the given child row.
        """
        child_batch = child_row.batch
        child_credit = model.PurchaseBatchCredit()
        self.copy_credit_attributes(truck_dump_credit, child_credit)
        child_credit.date_ordered = child_batch.date_ordered
        child_credit.date_shipped = child_batch.date_shipped
        child_credit.date_received = child_batch.date_received
        child_credit.invoice_date = child_batch.invoice_date
        child_credit.invoice_number = child_batch.invoice_number
        child_credit.invoice_line_number = child_row.invoice_line_number
        child_credit.invoice_case_cost = child_row.invoice_case_cost
        child_credit.invoice_unit_cost = child_row.invoice_unit_cost
        child_credit.invoice_total = child_row.invoice_total
        child_row.credits.append(child_credit)
        return child_credit

    # TODO: surely this should live elsewhere
    def calc_best_fit(self, units, case_quantity):
        case_quantity = case_quantity or 1
        if case_quantity == 1:
            return 0, units
        cases = units // case_quantity
        if cases:
            return cases, units - (cases * case_quantity)
        return 0, units

    def refresh(self, batch, progress=None):

        # reset PO total for ordering batch
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            batch.po_total = 0

        # reset invoice total for receiving and costing batch
        elif batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                            self.enum.PURCHASE_BATCH_MODE_COSTING):
            batch.invoice_total = 0

        # refresh all rows etc. per usual
        result = super(PurchaseBatchHandler, self).refresh(batch, progress=progress)
        if result:

            # here begins some extra magic for truck dump receiving batches
            if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
                session = orm.object_session(batch)
                session.flush()

                if batch.is_truck_dump_parent():

                    # will try to establish new claims against the parent
                    # batch, where possible
                    unclaimed = [row for row in batch.active_rows()
                                 if row.status_code in (row.STATUS_TRUCKDUMP_UNCLAIMED,
                                                        row.STATUS_TRUCKDUMP_PARTCLAIMED)]
                    for row in unclaimed:
                        if row.product_uuid: # only support rows with product for now
                            for child in batch.truck_dump_children:
                                child_rows = [child_row for child_row in child.active_rows()
                                              if child_row.product_uuid == row.product_uuid]
                                self.make_truck_dump_claims(row, child_rows)
                                if row.status_code not in (row.STATUS_TRUCKDUMP_UNCLAIMED,
                                                           row.STATUS_TRUCKDUMP_PARTCLAIMED):
                                    break

                    # all rows should be refreshed now, but batch status still needs it
                    self.refresh_batch_status(batch)
                    for child in batch.truck_dump_children:
                        self.refresh_batch_status(child)

                elif batch.is_truck_dump_child():

                    # will try to establish claims against the parent batch,
                    # for each "incomplete" row (i.e. those with unclaimed
                    # order quantities)
                    incomplete = [row for row in batch.active_rows()
                                  if row.status_code in (row.STATUS_INCOMPLETE,
                                                         row.STATUS_ORDERED_RECEIVED_DIFFER)]
                    for row in incomplete:
                        if row.product_uuid: # only support rows with product for now
                            parent_rows = [parent_row for parent_row in batch.truck_dump_batch.active_rows()
                                           if parent_row.product_uuid == row.product_uuid]
                            for parent_row in parent_rows:
                                self.make_truck_dump_claims(parent_row, [row])
                                if row.status_code not in (row.STATUS_INCOMPLETE,
                                                           row.STATUS_ORDERED_RECEIVED_DIFFER):
                                    break

                    # all rows should be refreshed now, but batch status still needs it
                    self.refresh_batch_status(batch.truck_dump_batch)
                    self.refresh_batch_status(batch)

        return result

    def refresh_batch_status(self, batch):
        rows = batch.active_rows()

        # "unknown product" is the most egregious status; we'll "prefer" it
        # over all others in order to bring it to user's attention
        if any([row.status_code == row.STATUS_PRODUCT_NOT_FOUND for row in rows]):
            batch.status_code = batch.STATUS_UNKNOWN_PRODUCT

        # truck dump parent batch status should reflect how much is (un)claimed
        elif batch.is_truck_dump_parent():

            # empty batch is considered "ok"
            if not rows:
                batch.status_code = batch.STATUS_OK

            # batch is "claimed" only if all rows are
            elif all([row.status_code == row.STATUS_TRUCKDUMP_CLAIMED for row in rows]):
                batch.status_code = batch.STATUS_TRUCKDUMP_CLAIMED

            # otherwise just call it "unclaimed"
            else:
                batch.status_code = batch.STATUS_TRUCKDUMP_UNCLAIMED

        # for now anything else is considered ok
        else:
            batch.status_code = batch.STATUS_OK

    def locate_product_for_entry(self, session, entry, lookup_by_code=True):
        """
        Try to locate the product represented by the given "entry" - which is
        assumed to be a "raw" string, e.g. as obtained from scanner or other
        user input, or from a vendor-supplied spreadsheet etc.  (In other words
        this method is not told "what" sort of entry it is being given.)

        :param lookup_by_code: If set to ``False``, then the method will
           attempt a lookup *only* on the product key field (either ``upc`` or
           ``item_id`` depending on config).  If set to ``True`` (the default)
           then the method will also attempt a lookup in the ``ProductCode``
           table, aka. alternate codes.
        """
        # try to locate product by uuid before other, more specific key
        product = session.query(model.Product).get(entry)
        if product:
            return product

        product_key = self.config.product_key()
        if product_key == 'upc':

            if entry.isdigit():

                # we first assume the user entry *does* include check digit
                provided = GPC(entry, calc_check_digit=False)
                product = api.get_product_by_upc(session, provided)
                if product:
                    return product

                # but we can also calculate a check digit and try that
                checked = GPC(entry, calc_check_digit='upc')
                product = api.get_product_by_upc(session, checked)
                if product:
                    return product

        elif product_key == 'item_id':

            # try to locate product by item_id
            product = api.get_product_by_item_id(session, entry)
            if product:
                return product

        # if we made it this far, lookup by product key failed.

        # okay then, let's maybe attempt lookup by "alternate" code
        if lookup_by_code:
            product = api.get_product_by_code(session, entry)
            if product:
                return product

    def locate_product(self, row, session=None, vendor=None):
        """
        Try to locate the product represented by the given row.  Default
        behavior here, is to do a simple lookup on either ``Product.upc`` or
        ``Product.item_id``, depending on which is configured as your product
        key field.
        """
        if not session:
            session = orm.object_session(row)
        product_key = self.config.product_key()

        if product_key == 'upc':
            if row.upc:
                product = api.get_product_by_upc(session, row.upc)
                if product:
                    return product

        elif product_key == 'item_id':
            if row.item_id:
                product = api.get_product_by_item_id(session, row.item_id)
                if product:
                    return product

        # product key didn't work, but vendor item code just might
        if row.vendor_code:
            product = api.get_product_by_vendor_code(session, row.vendor_code,
                                                     vendor=vendor or row.batch.vendor)
            if product:
                return product

        # before giving up, let's do a lookup on alt codes too
        if row.item_entry:
            product = api.get_product_by_code(session, row.item_entry)
            if product:
                return product

    def transform_pack_to_unit(self, row):
        """
        Transform the given row, which is assumed to associate with a "pack"
        item, such that it associates with the "unit" item instead.
        """
        if not row.product:
            return
        if not row.product.is_pack_item():
            return

        assert row.batch.is_truck_dump_parent()

        # remove any existing claims for this (parent) row
        if row.claims:
            session = orm.object_session(row)
            del row.claims[:]
            # set temporary status for the row, if needed.  this is to help
            # with claiming logic below
            if row.status_code in (row.STATUS_TRUCKDUMP_PARTCLAIMED,
                                   row.STATUS_TRUCKDUMP_CLAIMED,
                                   row.STATUS_TRUCKDUMP_OVERCLAIMED):
                row.status_code = row.STATUS_TRUCKDUMP_UNCLAIMED
            session.flush()
            session.refresh(row)

        # pretty sure this is the only status we're expecting at this point...
        assert row.status_code == row.STATUS_TRUCKDUMP_UNCLAIMED

        # replace the row's product association
        pack = row.product
        unit = pack.unit
        row.product = unit
        row.item_id = unit.item_id
        row.upc = unit.upc

        # set new case quantity, per preferred cost
        cost = unit.cost_for_vendor(row.batch.vendor)
        row.case_quantity = (cost.case_size or 1) if cost else 1

        # must recalculate "units received" since those were for the pack item
        if row.units_received:
            row.units_received *= pack.pack_size

        # try to establish "claims" between parent and child(ren)
        for child in row.batch.truck_dump_children:
            child_rows = [child_row for child_row in child.active_rows()
                          if child_row.product_uuid == row.product.uuid]
            self.make_truck_dump_claims(row, child_rows)
            if row.status_code not in (row.STATUS_TRUCKDUMP_UNCLAIMED,
                                       row.STATUS_TRUCKDUMP_PARTCLAIMED):
                break

        # refresh the row itself, so product attributes will be updated
        self.refresh_row(row)

        # refresh status for the batch(es) proper, just in case this changed things
        self.refresh_batch_status(row.batch)
        for child in row.batch.truck_dump_children:
            self.refresh_batch_status(child)

    def refresh_row(self, row, initial=False):
        """
        Refreshing a row will A) assume that ``row.product`` is already set to
        a valid product, or else will attempt to locate the product, and B)
        update various other fields on the row (description, size, etc.)  to
        reflect the current product data.  It also will adjust the batch PO
        total per the row PO total.
        """
        batch = row.batch

        # first identify the product, or else we have nothing more to do
        product = row.product
        if not product:
            product = self.locate_product(row)
            if product:
                row.product = product
            else:
                row.status_code = row.STATUS_PRODUCT_NOT_FOUND
                return

        # update various (cached) product attributes for the row
        cost = row.product.cost_for_vendor(batch.vendor)
        row.upc = product.upc
        row.item_id = product.item_id
        row.brand_name = six.text_type(product.brand or '')
        row.description = product.description
        row.size = product.size
        if product.department:
            row.department_number = product.department.number
            row.department_name = product.department.name
        else:
            row.department_number = None
            row.department_name = None
        row.vendor_code = cost.code if cost else None

        # figure out the effective case quantity, and whether it differs with
        # what we previously had on file
        case_quantity_differs = False
        if cost and cost.case_size:
            if not row.case_quantity:
                row.case_quantity = cost.case_size
            elif row.case_quantity != cost.case_size:
                if batch.is_truck_dump_parent():
                    # always overwrite case quantity for truck dump, since its
                    # value should only come from master cost (right?)
                    row.case_quantity = cost.case_size
                else:
                    case_quantity_differs = True

        self.refresh_totals(row, cost, initial)

        # all that's left should be setting status for the row...and that logic
        # will primarily depend on the 'mode' for this purchase batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            row.status_code = row.STATUS_OK

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

            # first check to see if we have *any* confirmed items
            if not (row.cases_received or row.units_received or
                    row.cases_damaged or row.units_damaged or
                    row.cases_expired or row.units_expired or
                    row.cases_mispick or row.units_mispick):
                # TODO: is this right? should row which ordered nothing just be removed?
                if batch.order_quantities_known and not (row.cases_ordered or row.units_ordered):
                    row.status_code = row.STATUS_OK
                # TODO: is this right? should out of stock just be a filter for
                # the user to specify, or should it affect status?
                elif row.out_of_stock:
                    row.status_code = row.STATUS_OUT_OF_STOCK
                else:
                    row.status_code = row.STATUS_INCOMPLETE
            else:
                if batch.is_truck_dump_parent():
                    confirmed = self.get_units_confirmed(row)
                    claimed = self.get_units_claimed(row)
                    if claimed == confirmed:
                        row.status_code = row.STATUS_TRUCKDUMP_CLAIMED
                    elif not claimed:
                        row.status_code = row.STATUS_TRUCKDUMP_UNCLAIMED
                    elif claimed < confirmed:
                        row.status_code = row.STATUS_TRUCKDUMP_PARTCLAIMED
                    elif claimed > confirmed:
                        row.status_code = row.STATUS_TRUCKDUMP_OVERCLAIMED
                    else:
                        raise NotImplementedError
                else: # not truck_dump parent; either "normal" receiving or TD child
                    if case_quantity_differs:
                        row.status_code = row.STATUS_CASE_QUANTITY_DIFFERS
                        row.status_text = "batch has {} but master cost has {}".format(
                            repr(row.case_quantity), repr(cost.case_size))
                    elif batch.order_quantities_known and (
                            self.get_units_ordered(row) != self.get_units_accounted_for(row)):
                        row.status_code = row.STATUS_ORDERED_RECEIVED_DIFFER
                    # TODO: is this right? should out of stock just be a filter for
                    # the user to specify, or should it affect status?
                    elif row.out_of_stock:
                        row.status_code = row.STATUS_OUT_OF_STOCK
                    else:
                        row.status_code = row.STATUS_OK

        else:
            raise NotImplementedError("can't refresh row for batch of mode: {}".format(
                self.enum.PURHASE_BATCH_MODE.get(batch.mode, "unknown ({})".format(batch.mode))))

    def remove_row(self, row):
        """
        When removing a row from purchase batch, (maybe) must also update some
        totals for the batch.
        """
        batch = row.batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            if row.po_total:
                batch.po_total -= row.po_total

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if row.invoice_total:
                batch.invoice_total -= row.invoice_total

        super(PurchaseBatchHandler, self).remove_row(row)

    def refresh_totals(self, row, cost, initial):
        batch = row.batch

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            row.po_unit_cost = self.get_unit_cost(row.product, batch.vendor)
            if row.po_unit_cost:
                row.po_total = row.po_unit_cost * self.get_units_ordered(row)
                batch.po_total = (batch.po_total or 0) + row.po_total
            else:
                row.po_total = None

        elif batch.mode in (self.enum.PURCHASE_BATCH_MODE_RECEIVING,
                            self.enum.PURCHASE_BATCH_MODE_COSTING):
            row.invoice_unit_cost = (cost.unit_cost if cost else None) or row.po_unit_cost
            if row.invoice_unit_cost:
                row.invoice_total = row.invoice_unit_cost * self.get_units_accounted_for(row)
                batch.invoice_total = (batch.invoice_total or 0) + row.invoice_total
            else:
                row.invoice_total = None

    def get_unit_cost(self, product, vendor):
        """
        Must return the PO unit cost for the given product, from the given vendor.
        """
        cost = product.cost_for_vendor(vendor) or product.cost
        if cost:
            return cost.unit_cost

    def get_units(self, cases, units, case_quantity):
        case_quantity = case_quantity or 1
        return (units or 0) + case_quantity * (cases or 0)

    def get_units_ordered(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_ordered, row.units_ordered, case_quantity)

    # TODO: we now have shipped quantities...should return sum of those instead?
    def get_units_shipped(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        units_damaged = (row.units_damaged or 0) + case_quantity * (row.cases_damaged or 0)
        units_expired = (row.units_expired or 0) + case_quantity * (row.cases_expired or 0)
        return self.get_units_received(row) + units_damaged + units_expired

    def get_units_received(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_received, row.units_received, case_quantity)

    def get_units_damaged(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_damaged, row.units_damaged, case_quantity)

    def get_units_expired(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_expired, row.units_expired, case_quantity)

    def get_units_confirmed(self, row, case_quantity=None):
        received = self.get_units_received(row, case_quantity=case_quantity)
        damaged = self.get_units_damaged(row, case_quantity=case_quantity)
        expired = self.get_units_expired(row, case_quantity=case_quantity)
        return received + damaged + expired

    def get_units_mispick(self, row, case_quantity=None):
        case_quantity = case_quantity or row.case_quantity or 1
        return self.get_units(row.cases_mispick, row.units_mispick, case_quantity)

    def get_units_accounted_for(self, row, case_quantity=None):
        confirmed = self.get_units_confirmed(row, case_quantity=case_quantity)
        mispick = self.get_units_mispick(row, case_quantity=case_quantity)
        return confirmed + mispick

    def get_units_shorted(self, obj, case_quantity=None):
        case_quantity = case_quantity or obj.case_quantity or 1
        if hasattr(obj, 'cases_shorted'):
            # obj is really a credit
            return self.get_units(obj.cases_shorted, obj.units_shorted, case_quantity)
        else:
            # obj is a row, so sum the credits
            return sum([self.get_units(credit.cases_shorted, credit.units_shorted, case_quantity)
                        for credit in obj.credits])

    def get_units_claimed(self, row, case_quantity=None):
        """
        Returns the total number of units which are "claimed" by child rows,
        for the given truck dump parent row.
        """
        claimed = 0
        for claim in row.claims:
            # prefer child row's notion of case quantity, over parent row
            case_qty = case_quantity or claim.claiming_row.case_quantity or row.case_quantity
            claimed += self.get_units_confirmed(claim, case_quantity=case_qty)
        return claimed

    def get_units_claimed_received(self, row, case_quantity=None):
        return sum([self.get_units_received(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_claimed_damaged(self, row, case_quantity=None):
        return sum([self.get_units_damaged(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_claimed_expired(self, row, case_quantity=None):
        return sum([self.get_units_expired(claim, case_quantity=row.case_quantity)
                    for claim in row.claims])

    def get_units_available(self, row, case_quantity=None):
        confirmed = self.get_units_confirmed(row, case_quantity=case_quantity)
        claimed = self.get_units_claimed(row, case_quantity=case_quantity)
        return confirmed - claimed

    def update_order_counts(self, purchase, progress=None):

        def update(item, i):
            if item.product:
                inventory = item.product.inventory or model.ProductInventory(product=item.product)
                inventory.on_order = (inventory.on_order or 0) + (item.units_ordered or 0) + (
                    (item.cases_ordered or 0) * (item.case_quantity or 1))

        self.progress_loop(update, purchase.items, progress,
                           message="Updating inventory counts")

    def update_receiving_inventory(self, purchase, consume_on_order=True, progress=None):

        def update(item, i):
            if item.product:
                inventory = item.product.inventory or model.ProductInventory(product=item.product)
                count = (item.units_received or 0) + (item.cases_received or 0) * (item.case_quantity or 1)
                if count:
                    if consume_on_order:
                        if (inventory.on_order or 0) < count:
                            raise RuntimeError("Received {} units for {} but it only had {} on order".format(
                                count, item.product, inventory.on_order or 0))
                        inventory.on_order -= count
                    inventory.on_hand = (inventory.on_hand or 0) + count

        self.progress_loop(update, purchase.items, progress,
                           message="Updating inventory counts")

    def why_not_execute(self, batch):
        """
        This method should return a string indicating the reason why the given
        batch should not be considered executable.  By default it returns
        ``None`` which means the batch *is* to be considered executable.

        Note that it is assumed the batch has not already been executed, since
        execution is globally prevented for such batches.
        """
        # not all receiving batches are executable
        if batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:

            if batch.is_truck_dump_parent() and batch.status_code != batch.STATUS_TRUCKDUMP_CLAIMED:
                return ("Can't execute a Truck Dump (parent) batch until "
                        "it has been fully claimed by children")

            if batch.is_truck_dump_child():
                return ("Can't directly execute batch which is child of a truck dump "
                        "(must execute truck dump instead)")

    def execute(self, batch, user, progress=None):
        """
        Default behavior for executing a purchase batch will create a new
        purchase, by invoking :meth:`make_purchase()`.
        """
        session = orm.object_session(batch)

        if batch.mode == self.enum.PURCHASE_BATCH_MODE_ORDERING:
            purchase = self.make_purchase(batch, user, progress=progress)
            self.update_order_counts(purchase, progress=progress)
            return purchase

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_RECEIVING:
            if self.allow_truck_dump and batch.is_truck_dump_parent():
                self.execute_truck_dump(batch, user, progress=progress)
                return True
            else:
                with session.no_autoflush:
                    return self.receive_purchase(batch, progress=progress)

        elif batch.mode == self.enum.PURCHASE_BATCH_MODE_COSTING:
            # TODO: finish this...
            # with session.no_autoflush:
            #     return self.cost_purchase(batch, progress=progress)
            purchase = batch.purchase
            purchase.invoice_date = batch.invoice_date
            purchase.status = self.enum.PURCHASE_STATUS_COSTED
            return purchase

        assert False

    def execute_truck_dump(self, batch, user, progress=None):
        now = make_utc()
        for child in batch.truck_dump_children:
            if not self.execute(child, user, progress=progress):
                raise RuntimeError("Failed to execute child batch: {}".format(child))
            child.executed = now
            child.executed_by = user

    def make_credits(self, batch, progress=None):
        session = orm.object_session(batch)
        mapper = orm.class_mapper(model.PurchaseBatchCredit)

        def copy(row, i):
            for batch_credit in row.credits:
                credit = model.PurchaseCredit()
                for prop in mapper.iterate_properties:
                    if isinstance(prop, orm.ColumnProperty) and hasattr(credit, prop.key):
                        setattr(credit, prop.key, getattr(batch_credit, prop.key))
                credit.status = self.enum.PURCHASE_CREDIT_STATUS_NEW
                session.add(credit)

        return self.progress_loop(copy, batch.active_rows(), progress,
                                  message="Creating purchase credits")

    def make_purchase(self, batch, user, progress=None):
        """
        Effectively clones the given batch, creating a new Purchase in the
        Rattail system.
        """
        session = orm.object_session(batch)
        purchase = model.Purchase()

        # TODO: should be smarter and only copy certain fields here
        skip_fields = [
            'date_received',
        ]
        for prop in orm.object_mapper(batch).iterate_properties:
            if prop.key in skip_fields:
                continue
            if hasattr(purchase, prop.key):
                setattr(purchase, prop.key, getattr(batch, prop.key))

        def clone(row, i):
            item = model.PurchaseItem()
            # TODO: should be smarter and only copy certain fields here
            for prop in orm.object_mapper(row).iterate_properties:
                if hasattr(item, prop.key):
                    setattr(item, prop.key, getattr(row, prop.key))
            purchase.items.append(item)

        with session.no_autoflush:
            self.progress_loop(clone, batch.active_rows(), progress,
                               message="Creating purchase items")

        purchase.created = make_utc()
        purchase.created_by = user
        purchase.status = self.enum.PURCHASE_STATUS_ORDERED
        session.add(purchase)
        batch.purchase = purchase
        return purchase

    def receive_purchase(self, batch, progress=None):
        """
        Update the purchase for the given batch, to indicate received status.
        """
        session = orm.object_session(batch)
        purchase = batch.purchase
        if not purchase:
            batch.purchase = purchase = model.Purchase()

            # TODO: should be smarter and only copy certain fields here
            skip_fields = [
                'uuid',
                'date_received',
            ]
            with session.no_autoflush:
                for prop in orm.object_mapper(batch).iterate_properties:
                    if prop.key in skip_fields:
                        continue
                    if hasattr(purchase, prop.key):
                        setattr(purchase, prop.key, getattr(batch, prop.key))

        purchase.invoice_number = batch.invoice_number
        purchase.invoice_date = batch.invoice_date
        purchase.invoice_total = batch.invoice_total
        purchase.date_received = batch.date_received

        # determine which fields we'll copy when creating new purchase item
        copy_fields = []
        for prop in orm.class_mapper(model.PurchaseItem).iterate_properties:
            if hasattr(model.PurchaseBatchRow, prop.key):
                copy_fields.append(prop.key)

        def update(row, i):
            item = row.item
            if not item:
                row.item = item = model.PurchaseItem()
                for field in copy_fields:
                    setattr(item, field, getattr(row, field))
                purchase.items.append(item)

            item.cases_received = row.cases_received
            item.units_received = row.units_received
            item.cases_damaged = row.cases_damaged
            item.units_damaged = row.units_damaged
            item.cases_expired = row.cases_expired
            item.units_expired = row.units_expired
            item.invoice_line_number = row.invoice_line_number
            item.invoice_case_cost = row.invoice_case_cost
            item.invoice_unit_cost = row.invoice_unit_cost
            item.invoice_total = row.invoice_total

        with session.no_autoflush:
            self.progress_loop(update, batch.active_rows(), progress,
                               message="Updating purchase line items")

        purchase.status = self.enum.PURCHASE_STATUS_RECEIVED
        return purchase

    def clone_row(self, oldrow):
        newrow = super(PurchaseBatchHandler, self).clone_row(oldrow)

        for oldcredit in oldrow.credits:
            newcredit = model.PurchaseBatchCredit()
            self.copy_credit_attributes(oldcredit, newcredit)
            newrow.credits.append(newcredit)

        return newrow

    def copy_credit_attributes(self, source_credit, target_credit):
        mapper = orm.class_mapper(model.PurchaseBatchCredit)
        for prop in mapper.iterate_properties:
            if prop.key not in ('uuid', 'row_uuid'):
                if isinstance(prop, orm.ColumnProperty):
                    setattr(target_credit, prop.key, getattr(source_credit, prop.key))
