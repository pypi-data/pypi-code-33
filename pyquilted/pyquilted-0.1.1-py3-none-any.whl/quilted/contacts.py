class ContactFactory:
    @staticmethod
    def create(key, val):
        contact = None
        if key in 'email':
            contact = EmailContact(val)
        elif key in 'phone':
            contact = PhoneContact(val)
        elif key in 'social':
            contact = SocialContact(**val)
        return contact


class EmailContact:
    def __init__(self, email, icons=None):
        self.label = 'email'
        self.value = email  # need to validate
        self.icons = icons or ['fa-envelope']


class PhoneContact:
    def __init__(self, phone, icons=None):
        self.label = 'phone'
        self.value = phone  # need to validate
        self.icons = icons or ['fa-phone']


class SocialContact:
    def __init__(self, handle=None, sites=None, **kwargs):
        self.label = 'social'
        self.value = handle
        self.icons = self._iconify(sites)

    def _iconify(self, sites):
        return list(map(lambda i: 'fa-' + i, sites))
