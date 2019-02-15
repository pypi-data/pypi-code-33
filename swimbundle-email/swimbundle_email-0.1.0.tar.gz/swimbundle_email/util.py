import re
import quopri
import hashlib
import magic
import base64
import pendulum
import pendulum.parsing.exceptions
from types import FunctionType, MethodType, StringTypes, DictType, ListType
import warnings

# Fields: Type, Default
FIELD_TYPES = {
    "cc": (StringTypes, u""),
    "bcc": (StringTypes, u""),
    "raw_content": (StringTypes, u""),
    "raw_headers": (StringTypes, u""),
    "reply_to": (StringTypes, u""),
    "sender": (StringTypes, u""),
    "plaintext_body": (StringTypes, u""),
    "html_body": (StringTypes, u""),
    "rtf_body": (StringTypes, u""),
    "subject": (StringTypes, u""),
    "type": (StringTypes, u""),
    "recipients": (StringTypes, u""),
    "headers": (ListType, []),
    "attachments": (DictType,
                    {
                        "attach_info": [],
                        "attachments": [],
                        "attachments_md5": [],
                        "attachments_sha1": [],
                        "attachments_sha256": []
                    }),
    "id": (StringTypes, u""),
    "date": (StringTypes, u"")
}


class EmailParser(object):
    def __init__(self, filename, email_data, ignore_errors=False, exclude_attachment_extensions=None):
        self.filename = filename
        self.email_data = email_data
        self.ignore_errors = ignore_errors
        self.exclude_attachment_extensions = exclude_attachment_extensions

    def get_cc(self):
        raise NotImplementedError

    def get_bcc(self):
        raise NotImplementedError

    def get_raw_content(self):
        raise NotImplementedError

    def get_raw_headers(self):
        raise NotImplementedError

    def get_reply_to(self):
        raise NotImplementedError

    def get_sender(self):
        raise NotImplementedError

    def get_plaintext_body(self):
        raise NotImplementedError

    def get_html_body(self, decode_html=True):
        raise NotImplementedError

    def get_rtf_body(self):
        raise NotImplementedError

    def get_subject(self):
        raise NotImplementedError

    def get_type(self):
        raise NotImplementedError

    def get_recipients(self):
        raise NotImplementedError

    def get_headers(self):
        raise NotImplementedError

    def get_attachments(self):
        raise NotImplementedError

    def get_id(self):
        raise NotImplementedError

    def get_date(self):
        raise NotImplementedError

    def __getattribute__(self, item):
        """Wrap 'get_' calls to ensure some basic type checking"""
        attrib = super(EmailParser, self).__getattribute__(item)
        if isinstance(attrib, (FunctionType, MethodType)) and item.startswith("get_"):

            def wrapped(*args, **kwargs):
                output = attrib(*args, **kwargs)
                expected_type, default_val = FIELD_TYPES[item.replace("get_", "")]
                if isinstance(output, expected_type):
                    return output
                elif not output:  # Output resolves to None
                    warnings.warn("Invalid output type from Parser! Expected '{}', got '{}'".format(
                        expected_type,
                        type(output)
                    ))
                    return default_val
                else:
                    raise TypeError("Invalid type returned from Parser! Expected '{}', got '{}'".format(
                        expected_type,
                        type(output)
                    ))
            return wrapped
        else:
            return attrib

    @staticmethod
    def _parse_regex(regex, *bodies):
        text = ""
        for body in bodies:
            text = text + body if body else text
        val = list(set(re.findall(regex, text)))
        return val

    def _get_authenticated_sender(self, headers):
        return ",".join(
            self._parse_regex('(?:Authenticated sender:) ([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', headers))

    def _get_clean_emails(self, email_data):
        valid_email_regex = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        return ",".join(self._parse_regex(valid_email_regex, email_data))

    def _try_date_format(self, date_data):
        try:
            dt = pendulum.parse(date_data)
            return dt.to_iso8601_string()
        except pendulum.parsing.exceptions.ParserError:
            return date_data

    def parse(self):
        result = {
            "result": u"failure", "attachments_sha1": "", "attachments_md5": "",
            "attach_info": "", "headers": "",
            "recipients": "", "subject": "", "text_body": "", "html_body": "", "type": "", "attachments_sha256": ""
        }

        attachments = self.get_attachments()
        attachments_data = attachments.pop("attachments")  # Remove until we clean results
        if self.exclude_attachment_extensions:
            self.exclude_attachment_extensions = tuple(map(unicode.lower, self.exclude_attachment_extensions))
            attachments_data = filter(
                lambda attachment: not bool(
                    unicode(attachment["filename"]).lower().endswith(self.exclude_attachment_extensions)),
                attachments_data
            )

        result.update(attachments)

        result["cc"] = self.get_cc()
        result["bcc"] = self.get_bcc()
        result["raw_headers"] = self.get_raw_headers()
        result["raw_content"] = self.get_raw_content()

        result["headers"] = ''.join(h[0] + ": " + h[1] + "\n" for h in self.get_headers())

        sender = self.get_sender()
        result["sender"] = sender if self._get_clean_emails(sender) else self._get_authenticated_sender(
            result['headers'])
        result["valid_sender_email"] = self._get_clean_emails(sender) or self._get_authenticated_sender(
            result['headers'])

        reply_to = self.get_reply_to()
        result["reply_to"] = reply_to
        result["valid_reply_to_email"] = self._get_clean_emails(reply_to)

        result["recipients"] = self.get_recipients()
        result["valid_recipients_email"] = self._get_clean_emails(self.get_recipients())

        result["subject"] = self.get_subject()
        result["text_body"] = self.get_plaintext_body()
        result["html_body"] = self.get_html_body()

        result["rtf_body"] = self.get_rtf_body()
        result["type"] = self.get_type()

        result["date"] = self._try_date_format(self.get_date())

        result["id"] = self.get_id()

        # Convert key, values to unicode (cleaning)
        content_charset = EmailUtil.check_content_charset(self)
        for k, v in result.iteritems():
            result[k] = v if v else u""
            if not isinstance(result[k], unicode):
                result[k] = result.pop(k).decode(content_charset, errors="replace")

        result["result"] = u"success"
        result["attachments"] = attachments_data  # Add back after cleaning

        return result


class EmailAttachmentList(object):
    """Container class for attachments, to standardize the output"""

    def __init__(self):
        self.attachments = []

    def add_attachment(self, email_attachment):
        if isinstance(email_attachment, EmailAttachment):
            self.attachments.append(email_attachment)
        else:
            raise Exception("Attempted to add attachment to EmailAttachments, invalid type detected")

    def to_swimlane_output(self):
        result = {
            "attach_info": [],
            "attachments": [],
            "attachments_md5": [],
            "attachments_sha1": [],
            "attachments_sha256": []
        }

        # Add all attachments into a list
        for attachment in self.attachments:
            result["attachments"].append(attachment.attachment_data)
            result["attach_info"].append(attachment.header_info)
            result["attachments_sha1"].append(attachment.hash_sha1)
            result["attachments_md5"].append(attachment.hash_md5)
            result["attachments_sha256"].append(attachment.hash_sha256)

        # Flatten results
        for k, v in result.iteritems():
            if k != "attachments":  # Don't flatten the attachments
                result[k] = ",".join(result[k])

        return result


class EmailAttachment(object):
    """Singular Attachment"""

    def __init__(self, header_info, filename, raw_data):
        """
        Create a singular email attachment object
        :param header_info: String of header information about the email
        :param filename: Filename of the attachment
        :param raw_data: Byte-like data, will be base64encoded
        """
        self.header_info = header_info
        self.raw_data = raw_data

        self.hash_md5 = hashlib.md5(raw_data).hexdigest()
        self.hash_sha1 = hashlib.sha1(raw_data).hexdigest()
        self.hash_sha256 = hashlib.sha256(raw_data).hexdigest()
        self.attachment_data = {
            "filename": filename,
            "base64": base64.b64encode(raw_data)
        }


class EmailUtil(object):

    @staticmethod
    def parse_email_set(iterable_emails, parser_cls, parser_options, pre_hook=None, post_hook=None):
        """
        Parse a set of emails, given an iterable-like object of emails to parse
        """
        iterable_emails = iter(iterable_emails)
        results = []

        for email in iterable_emails:
            parser_inst = parser_cls(email, **parser_options)
            try:
                if pre_hook:  # Hook function for changing the email if needed
                    email = pre_hook(email)
                results.append(parser_inst.parse())
                if post_hook:  # Hook function for modifiying the email object (ie set read on a server)
                    email = post_hook(email)
            except Exception as e:
                if parser_options.get("ignore_errors", False):
                    results.append({
                        "error": str(e)
                    })
                else:
                    raise
        return results

    # Check if the email base64 object conforms to rfc822
    @staticmethod
    def check_if_rfc_822(b64):
        file_decoded = base64.b64decode(b64)
        mime_type = magic.from_buffer(file_decoded, mime=True)
        if mime_type == "message/rfc822":
            return True
        else:
            return False

    # Tries to decode a mime encoded-word syntax string
    # See https://dmorgan.info/posts/encoded-word-syntax/ for more info
    @staticmethod
    def try_decode(text):
        if not text:
            return u"(None)"

        result = u""

        for item in re.split(r'[\n\s]+', text):
            item = item.strip()
            match = re.match(r'=\?(.+)\?([B|Q])\?(.+)\?=', item)
            if match:
                charset, encoding, encoded_text = match.groups()
                if encoding is 'B':
                    byte_str = base64.b64decode(encoded_text)
                elif encoding is 'Q':
                    byte_str = quopri.decodestring(encoded_text)
                else:
                    # Can't decode this string, invalid encoding type
                    return text
                result = result + byte_str.decode(charset, errors="ignore")
            else:
                result = result + u" " + unicode(item, "utf-8", "ignore")

        return result.strip() or text  # Return result if it's been populated, else original text

    @staticmethod
    def validate_charset(charset):
        # Validate the charset to ensure it exists
        possible_charset_fixes = [
            lambda x: x,  # No fix
            lambda x: x.replace("-", ""),  # Replace 'cp-850' with 'cp850'
        ]
        for fix in possible_charset_fixes:
            try:
                content_charset = fix(charset)
                "".decode(content_charset, errors="replace")
                return content_charset
            except LookupError:
                continue
        raise Exception("Unknown charset: {}".format(charset))

    @staticmethod
    def check_content_charset(parser):
        # Try to get the charset from a given email parser
        regex = r'(?:charset=\"?)([\w-]*)(?:\"+)'
        html_body = parser.get_html_body()
        headers = parser.get_headers()
        if headers:
            try:  # Try to get content charset from headers
                for header in headers:
                    if header[0].lower() == "content-type":
                        return EmailUtil.validate_charset(re.findall(regex, " ".join(header))[0])
            except IndexError:
                pass
        if html_body:
            try:  # Try to get content charset from html_body
                return EmailUtil.validate_charset(re.findall(regex, html_body)[0])
            except IndexError:
                pass
        return "utf-8"  # Default to utf-8 if we can't find it
