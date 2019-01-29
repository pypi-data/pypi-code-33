"""Holds utility functions useful in a variety of situations"""
import logging

LOGGER = logging.getLogger(__name__)

def find_function(func_path):
    '''Searches for and returns a function if it exists'''
    LOGGER.debug("Searching for function %s", func_path)
    paths = func_path.split(':')
    module = __import__(''.join(paths[:-1]), fromlist=['.'.join(paths[1:])])
    func = getattr(module, paths[-1])

    return func


class Email(object):
    '''A convenience object to create an email payload'''

    def __init__(self, subject, tos, ccs=None, bccs=None):
        '''
        Initalize an email with the recipients and subject. Content
        is not added here since its construction is a bit more complex.

        subject: This goes in the subject field
        tos, ccs, bccs: Lists of email addresses
        '''
        self.tos = tos
        self.ccs = ccs
        self.bccs = bccs
        self.subject = subject
        self.payload = {}

    def set_content(self, template='generic', **kwargs):
        '''
        Sets the content portion of the email. HTML is allowed.

        template: Email template to use. All templates have the following attributes,
                  the difference lies in how the "content" paramter is interpreted

        Recognized arguments for kwargs are:
        title: This goes at the top of the email in a large font
        header: This is a normal paragraph that starts the first portion.
        content: The template specific information goes here.
        footer: Like the header, except it comes after the content.
        '''
        self.payload = kwargs
        self.payload['template'] = template

    def set_recipients(self, tos=None, ccs=None, bccs=None):
        '''
        Sets the recipients for the email.

        Pass an empty list for recipient type to remove all recipients.
        '''
        self.tos = tos if tos != None else self.tos
        self.ccs = ccs if ccs != None else self.ccs
        self.bccs = bccs if bccs != None else self.bccs
