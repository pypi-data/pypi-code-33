class PerfectoExecutionContext:
    def __init__(self, webdriver, tags=None, job=None, project=None, customFields=[]):
        if webdriver is None:
            raise 'Missing required webdriver argument. Call your builder\'s withWebDriver() method'
        self.webdriver = webdriver
        self.job = job
        self.project = project
        clean_tags = []
        if tags is not None:
            for tag in tags:
                if not isinstance(tag, basestring):
                    print 'Warnning: perfecto tags must be strings, please change your tag:' + str(tag)
                else:
                    clean_tags.append(tag)
        self.context_tags = clean_tags
        self.customFields = {}
        if (len(customFields) > 0):
            for cf in customFields:
                self.customFields.update(cf.dict)
