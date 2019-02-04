"""Google licensing API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class Licensing(Base):
    """Licensing class."""

    def __init__(self, http):
        """Initialize a class instance."""
        self.licensing = build('licensing', 'v1', http=http)

        # hard-coded license inventory
        self.inventory = {
            # G Suite
            'Google-Apps': {
                'Google-Apps-Lite': 3650,
                '1010020020': 1900,  # Google-Apps-Enterprise
            },
            # Chromebox for Meetings
            'Google-Chrome-Device-Management': 0,
            # Google Drive Storage Licenses - Non-Enterprise users
            'Google-Drive-storage': {
                'Google-Drive-storage-20GB': 100,
                'Google-Drive-storage-50GB': 30,
                'Google-Drive-storage-200GB': 20,
                'Google-Drive-storage-400GB': 5,
            }
        }

    def add_licensing_assignment(self, product, sku, user):
        """Add licensing assignments for a specific product sku for a user."""
        body = {
            'userId': user,
        }
        params = {
            'productId': product,
            'skuId': sku,
            'body': body,
        }
        licensing_assignments = self.licensing.licenseAssignments()
        return licensing_assignments.insert(**params).execute()

    def get_inventory(self):
        """Return the current license inventory."""
        return self.inventory

    def get_licensing_assignments(self, product, sku, user):
        """Get licensing assignments for a specific product sku for a user."""
        params = {
            'productId': product,
            'skuId': sku,
            'userId': user,
        }
        licensing_assignments = self.licensing.licenseAssignments()
        return licensing_assignments.get(**params).execute()

    def get_product_assignments(self, product):
        """Return list of licensing assignments for a product."""
        params = {
            'productId': product,
            'customerId': 'broadinstitute.org',
        }
        licensing_assignments = self.licensing.licenseAssignments()
        request = licensing_assignments.listForProduct(**params)
        google_assignments = []
        while request is not None:
            assignments_list = request.execute()
            google_assignments += assignments_list.get('items', [])
            request = licensing_assignments.listForProduct_next(
                request,
                assignments_list
            )
        return google_assignments
