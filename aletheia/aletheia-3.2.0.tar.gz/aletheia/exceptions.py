class AletheiaException(Exception):

    def __init__(self, message=None, *args):
        super().__init__(message or self.get_default_message(), *args)

    def get_default_message(self):
        return "An unknown error occurred.  Sorry about that."


class UnknownFileTypeError(AletheiaException):
    def get_default_message(self):
        return "Aletheia doesn't recognise that file type"


class PrivateKeyNotDefinedError(AletheiaException):
    def get_default_message(self):
        return (
            "Aletheia can't do what you ask without a private key.  You "
            "should run `aletheia generate` first."
        )


class PublicKeyNotExistsError(AletheiaException):
    def get_default_message(self):
        return (
            "The public key location contained in the file header either "
            "can't be accessed, or does not contain a public key",
        )


class UnparseableFileError(AletheiaException):
    def get_default_message(self):
        return "Aletheia can't find a signature in that file"


class DependencyMissingError(AletheiaException):
    def get_default_message(self):
        return (
            "A software dependency appears to be missing, but this should "
            "never happen.  Please report an issue at "
            "https://gitlab.com/danielquinn/aletheia-python/issues"
        )


class UnacceptableLocationError(AletheiaException):
    def get_default_message(self):
        return "The domain name provided does not appear to be valid"


class UnrecognisedKeyError(AletheiaException):
    def get_default_message(self):
        return (
            "The key data provided could not be recognised as one formatted "
            "for Aletheia"
        )


class NotJsonObjectError(AletheiaException):
    def get_default_message(self):
        return (
            "The only kind of JSON file that Aletheia is capable of signing "
            "is a file containing a single JSON object.  JSON files "
            "containing a single list for example cannot be signed as there's "
            "no clear place to put the signature.  If you want to sign this "
            "file, you'll need to restructure it as an object.\n\n"
            "For example, if your JSON file looks like this:\n\n"
            "  [\"a\", \"b\", \"c\"]\n\n"
            "You could restructure it like this for signing to work:\n\n"
            "  {\"my_list\": [\"a\", \"b\", \"c\"]}"
        )
