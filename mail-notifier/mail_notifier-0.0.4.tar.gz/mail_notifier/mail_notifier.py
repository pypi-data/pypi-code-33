from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template
import datetime
import logging
import smtplib
import os


class Notifier:
    def __init__(self):
        self.recipients = []

    def read_recipients(self, recipients_filepath):
        """
            Return recipient list containing email addresses, phone number etc.. read from a file specified by filename.
        """
        try:
            with open(recipients_filepath, mode='r', encoding='utf-8') as contacts_file:
                for contact in contacts_file:
                    self.recipients.append(contact.split()[0])

        except Exception as err:
            logging.error(err)

    def add_recipients(self, recipients):
        """
            Add recipients to main recipient list
        """
        for recipient in recipients:
            self.recipients.append(recipient)


class EmailNotification(Notifier):
    def __init__(
            self,
            recipients=None,
            recipients_filepath=None,
            template_filepath=None,
            app_name="",
            sender="",
            message_subject="",
            message_type="html"):

        super().__init__()
        self.__default_template_keys = ["app_name", "task_name", "task_status", "task_start", "task_stop","additional_info"]
        self.default_template_filepath = "notifier_resources/html_template.txt"

        self.__host = ""
        self.__port = ""
        self.__host_email = ""
        self.__host_password = ""
        self.__smtp = smtplib.SMTP()

        self.template_filepath = template_filepath
        self.message_subject = message_subject
        self.message_type = message_type
        self.template_obj = [{}]
        self.sender = sender

        if self.template_filepath is None:
            self.tempalte_message = self.read_template(self.default_template_filepath)
            self.__set_default_template(app_name)
        else:
            self.tempalte_message = self.read_template(self.template_filepath)

        if recipients is not None and len(recipients) > 0:
            self.add_recipients(recipients)

        if recipients_filepath is not None and os.path.exists(recipients_filepath):
            self.read_recipients(recipients_filepath)

    @staticmethod
    def read_template(message_tempalte_path):
        """
            Returns a Template object comprising the contents of the file specified by filename.
        """
        try:
            with open(message_tempalte_path, 'r', encoding='utf-8') as template_file:
                template_file_content = template_file.read()

            return Template(template_file_content)

        except Exception as err:
            logging.error(err)

    def __connect_smtp(self):
        """
            Set up the SMTP server
        """
        try:
            smtp = smtplib.SMTP(host=self.__host, port=self.__port)
            smtp.starttls()
            smtp.login(self.__host_email, self.__host_password)

            return smtp

        except Exception as err:
            logging.error(err)

    def __send_email(self, subject, message, sender=""):

        if sender != "":
            self.sender = sender
        try:
            for recipient in self.recipients:
                if recipient != "":
                    msg = MIMEMultipart()
                    msg['From'] = self.sender
                    msg['To'] = recipient
                    msg['Subject'] = subject
                    # add in the message body

                    if self.message_type == "html":
                        msg.attach(MIMEText(message, 'html'))
                    else:
                        msg.attach(MIMEText(message, 'plain'))

                    # send the message via the server set up earlier.
                    self.__smtp.send_message(msg)
                    del msg

            # Terminate the SMTP session and close the connection
            self.__smtp.quit()
            logging.info("Send email success")

        except Exception as err:
            logging.error(err)

    def __set_default_template(self, app_name):
        for template_item in self.__default_template_keys:
            if template_item == 'app_name':
                self.set_template_prop(template_item, app_name)

            elif template_item == 'task_start':
                self.set_template_prop(template_item, datetime.datetime.now())
            else:
                self.set_template_prop(template_item, "")
                
    def set_smtp_settings(self, host, port, host_email, host_password):
        self.__host = host
        self.__port = port
        self.__host_email = host_email
        self.__host_password = host_password
        self.__smtp = self.__connect_smtp()

    def set_template_prop(self, key, value):
        """
            Add value to template_obj
        """
        self.template_obj[0][key] = value

    def send_failed_message(self, msg="", task_name=""):
        """
            Send default failed message
        """
        self.set_template_prop("task_status", "FAILED")
        self.set_template_prop("task_name", task_name)
        self.send_message(msg=msg)

    def send_success_message(self, msg="", task_name=""):
        """
            Send default success message
        """
        self.set_template_prop("task_status", "SUCCESS")
        self.set_template_prop("task_name", task_name)
        self.send_message(msg=msg)

    def send_message(self, msg, subject="", message_type=""):
        """
            Send HTML message, can use a different template than default one
        """
        if subject != "":
            self.message_subject = subject
        if message_type != "":
            self.message_type = message_type

        if self.message_type == 'html':
            if self.template_filepath is None:
                self.set_template_prop("task_stop", datetime.datetime.now())
                self.set_template_prop("additional_info", msg)

                if self.message_subject == "" and subject == "":
                    self.message_subject = self.template_obj[0]["app_name"] + " Notification"

                try:
                    msg = self.tempalte_message.substitute(self.template_obj[0])
                except Exception as err:
                    logging.error("{0} field is undefined in selected template".format(err))

        self.__send_email(subject=self.message_subject, message=msg)
