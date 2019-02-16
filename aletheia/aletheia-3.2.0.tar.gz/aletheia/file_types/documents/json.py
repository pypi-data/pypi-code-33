import json

from ...exceptions import UnparseableFileError, NotJsonObjectError
from ..base import File


class JsonFile(File):

    SUPPORTED_TYPES = ("application/json",)

    ID_KEY = "__aletheia__"
    JSON_KWARGS = {
        "separators": (",", ":"),
        "sort_keys": True,
        "ensure_ascii": False
    }

    def __init__(self, *args, **kwargs):

        self.__raw = None
        self.__json = None

        super().__init__(*args, **kwargs)

    def get_raw_data(self) -> bytes:
        """
        To get the "raw" data, we need to extract any Aletheia data from the
        JSON data and return the remainder.  Unfortunately, we have to do this
        with a whole lot of decoding & re-encoding.
        """

        if self.__raw is not None:
            return self.__raw

        r = self._get_json()  # str → obj

        if not isinstance(r, dict):
            raise NotJsonObjectError()

        # The Aletheia data can't be included in the "raw data"
        r.pop(self.ID_KEY, None)

        self.__raw = json.dumps(r, **self.JSON_KWARGS).encode()  # obj → bytes

        return self.__raw

    def sign(self, private_key, domain: str) -> None:

        self.check_domain(domain)

        signature = self.generate_signature(private_key)

        self.logger.debug("Signature generated: %s", signature)

        data = json.loads(self.get_raw_data().decode())  # bytes → obj
        data[self.ID_KEY] = self.generate_payload(domain, signature)

        with open(self.source, "wb") as f:
            f.write(
                json.dumps(data, **self.JSON_KWARGS).encode()  # obj → bytes
            )

    def verify(self) -> str:

        metadata = self.__get_metadata()

        version = metadata["version"]
        domain = metadata["domain"]
        signature = metadata["signature"]

        self.check_schema_version(version)

        self.logger.debug("Signature found: %s", signature)

        return self.verify_signature(domain, signature)

    def _get_json(self) -> dict:
        """
        This is a little annoying, since in this particular case, the "raw
        data" should theoretically be the entire contents of the file.  However
        for Aletheia, the "raw data" is meant to be "the data of the file
        *without* the Aletheia header info", and as JSON doesn't have a
        metadata layer, that "header" info is actually in the body of the file.

        So instead, this method will return all the JSON in the file, and the
        get_raw_data() method will return everything this method returns sans
        the Aletheia "header" data.
        """

        if self.__json:
            return self.__json

        with open(self.source, "rb") as f:
            raw = f.read()

        try:
            self.__json = json.loads(raw.decode())  # str → obj
        except json.JSONDecodeError:
            raise UnparseableFileError(
                "This does not appear to be a valid JSON file"
            )

        return self.__json

    def __get_metadata(self) -> dict:
        """
        Return the portion of the JSON data that we use to verify the
        raw data.
        """

        try:
            return json.loads(self._get_json()[self.ID_KEY])
        except KeyError:
            raise UnparseableFileError(
                "The JSON data did not appear to contain \"{}\" key".format(
                    self.ID_KEY
                )
            )
