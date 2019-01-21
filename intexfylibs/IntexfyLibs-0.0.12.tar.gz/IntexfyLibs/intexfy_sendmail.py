from __future__ import print_function
import httplib2
import os
import base64

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from email.mime.text import MIMEText
from googleapiclient import errors

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_known_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
# SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
# SCOPES = 'https://www.googleapis.com/auth/gmail.send'
SCOPES = 'https://mail.google.com'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Intexfy Sendmail'


class Mail:
    def __init__(self):
        pass

    def clr_error(self, to, subject, body):
        full_subject = '[ERROR] Crawler_C - %s' % subject

        self.custom_mail(to, full_subject, body)

    def techapi_error(self, to, subject, body):
        full_subject = '[ERROR] Api Tech - %s' % subject

        self.custom_mail(to, full_subject, body)

    def insuficient_credits(self, to, subject, body):
        full_subject = '[Insuficient Credits] Customer - %s' % subject

        self.custom_mail(to, full_subject, body)

    def custom_mail(self, to, subject, body):
        credentials = self.__get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)

        msg = self.__create_message('heitor@intexfy.com',
                                    to,
                                    subject,
                                    body)

        self.__send_message(service, 'me', msg)

    def __get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        # home_dir = os.path.expanduser('~')
        # credential_dir = os.path.join(home_dir, '.credentials')
        credential_dir = os.path.join('./', 'google_credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'gmail-python.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def __create_message(self, sender, to, subject, message_text):
        """Create a message for an email.

        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

        Returns:
        An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    def __send_message(self, service, user_id, message):
        """Send an email message.

        Args:
          service: Authorized Gmail API service instance.
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          message: Message to be sent.

        Returns:
          Sent Message.
        """
        try:
            message = (service.users().messages().send(userId=user_id, body=message).execute())
            print('Message Id: %s' % message['id'])
            return message
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
