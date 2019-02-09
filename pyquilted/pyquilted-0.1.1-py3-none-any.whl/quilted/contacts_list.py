class ContactsList:
    def __init__(self):
        self.contacts = []

    def __len__(self):
        return len(self.contacts)

    def __iter__(self):
        return iter(self.contacts)

    def append(self, contact):
        self.contacts.append(vars(contact))

    def serialize(self):
        return self.contacts
