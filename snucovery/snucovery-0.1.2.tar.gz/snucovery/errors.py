

class UnknownServiceCall(Exception):
    def __init__(self):
        Exception.__init__(self, "Boto3 service function does not exist.")

class InvalidServiceMappings(Exception):
    def __init__(self):
        Exception.__init__(self, "AwsService is missing a valid service mappings.")

class EmptyServiceMappings(Exception):
    def __init__(self):
        Exception.__init__(self, "AwsService service mappings are empty.")

class InvalidWorksheetName(Exception):
    def __init__(self):
        Exception.__init__(self, "Worksheet name is not a valid worksheet name.")

class WorksheetNotExists(Exception):
    def __init__(self):
        Exception.__init__(self, "Specified worksheet name does not exist.")
