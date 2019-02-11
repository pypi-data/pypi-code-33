

class TestContext:

    def __init__(self, customFields = [], tags=None):
        self.tags = tags
        self.customFields = {}
        if (len(customFields) > 0):
            for cf in customFields:
                self.customFields.update(cf.dict)
