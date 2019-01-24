import argparse
import logging
import mimetypes
import os
import pkg_resources
import random
import smtplib
import subprocess
import threading
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pyftpdlib import servers
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler


# setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(ch)


# quotes from http://rvelthuis.de/zips/quotes.txt
quotes = []

quote = ""
for line in (
    pkg_resources.resource_string(__name__, "quotes.txt").decode("utf-8").split("\n")
):
    if line == ".\n":
        quotes.append(quote)
        quote = ""
    else:
        quote += line


class MailClient:
    def __init__(self, from_addr, to_addr, smtp_server, smtp_user, smtp_password):
        self.smtp_user = smtp_user
        self.smtp_server = smtp_server
        self.to_addr = to_addr
        self.from_addr = from_addr
        self.smtp_password = smtp_password

    def send_mail(self, file_path):
        logger.debug("emailing %s", file_path)

        msg = MIMEMultipart()
        msg["From"] = self.from_addr
        msg["To"] = self.to_addr
        msg["Subject"] = os.path.basename(file_path)

        text = MIMEText(random.choice(quotes) + "\n\n\n\n", "plain", _charset="utf-8")
        msg.attach(text)

        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check for simple things like
        # gzip'd or compressed files.
        ctype, encoding = mimetypes.guess_type(file_path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        fp = open(file_path, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)

        attachment.add_header(
            "Content-Disposition", "attachment", filename=os.path.basename(file_path)
        )
        msg.attach(attachment)

        server = smtplib.SMTP(self.smtp_server)
        server.starttls()
        server.login(self.smtp_user, self.smtp_password)
        server.sendmail(self.from_addr, self.to_addr, msg.as_string())
        server.quit()


def process_file(file_path, mail_client: MailClient, ocr_enabled, ocr_lang):
    logger.info("processing file %s", file_path)
    filename, extension = os.path.splitext(file_path)

    if ocr_enabled and extension.lower() == ".pdf":
        # run OCR for PDF files
        logger.debug("executing OCR using pdfsandwich")
        subprocess.run(["pdfsandwich", "-lang", ocr_lang, file_path], check=True)
        dir_name = os.path.dirname(file_path)
        ocr_path = os.path.join(dir_name, "%s_ocr%s" % (filename, extension))
        mail_client.send_mail(ocr_path)
    else:
        # skip OCR
        mail_client.send_mail(file_path)


class MyHandler(FTPHandler):

    mail_client = None
    ocr_enabled = False  # disabled by default
    ocr_lang = "eng"

    def on_file_received(self, file):
        assert self.mail_client is not None
        # process_file(file, self.mail_client, self.ocr_enabled, self.ocr_lang)  # synchronous call

        # asynchronous call
        my_file = file
        t = threading.Thread(
            target=process_file,
            args=(my_file, self.mail_client, self.ocr_enabled, self.ocr_lang),
        )
        t.start()


def main():
    parser = argparse.ArgumentParser(description="Send FTP uploads via SMTP.")
    parser.add_argument(
        "--from", help="Sender email address", dest="from_addr", required=True
    )
    parser.add_argument(
        "--to", help="Recipient email address", dest="to_addr", required=True
    )
    parser.add_argument("--smtp-host", help="SMTP hostname", required=True)
    parser.add_argument("--smtp-port", help="SMTP port", default=25, type=int)
    parser.add_argument("--smtp-user", help="SMTP username", required=True)
    parser.add_argument("--smtp-pass", help="SMTP password", required=True)
    parser.add_argument(
        "--ftp-addr",
        help="FTP server address which will be returned for PASV requests.",
        required=True,
    )
    parser.add_argument(
        "--ftp-port", help="FTP port to bind to.", required=True, type=int
    )
    parser.add_argument(
        "--ftp-pasv-min", help="FTP PASV minimal port.", required=True, type=int
    )
    parser.add_argument(
        "--ftp-pasv-max", help="FTP PASV maximal port.", required=True, type=int
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="enable OCR (embeds a hidden text layer in PDF files)",
        dest="ocr_enabled",
    )
    parser.add_argument(
        "--ocr-lang",
        help="OCR: language of the text; option to tesseract (defaut: eng), e.g: eng, deu, deu-frak, fra, rus, swe, "
        "spa, ita, ... Multiple languages may be specified, separated by plus characters.",
        default="eng",
    )
    parser.add_argument(
        "--ftp-home", help="Upload directory", type=str, default="./ftproot/"
    )
    args = parser.parse_args()

    authorizer = DummyAuthorizer()
    authorizer.add_anonymous(homedir=args.ftp_home, perm="ew")

    mail_client = MailClient(
        "That fat talky scanner <%s>" % args.from_addr,
        args.to_addr,
        "%s:%s" % (args.smtp_host, args.smtp_port),
        args.smtp_user,
        args.smtp_pass,
    )

    handler = MyHandler
    handler.authorizer = authorizer
    handler.masquerade_address = args.ftp_addr
    handler.passive_ports = range(args.ftp_pasv_min, args.ftp_pasv_max + 1)
    handler.mail_client = mail_client
    handler.ocr_enabled = args.ocr_enabled
    handler.ocr_lang = args.ocr_lang

    logger.info("ftpmail initializing")

    server = servers.FTPServer(("0.0.0.0", args.ftp_port), handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
