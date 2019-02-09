from __future__ import absolute_import

import os.path
import smtplib
import logging
import pkg_resources

from email.parser import Parser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders

from bs4 import BeautifulSoup

from izaber import config, app_config
from izaber.startup import request_initialize, initializer
from izaber.compat import *
from izaber.paths import paths
from izaber.templates import parse, parsestr

log = logging.getLogger('email')

class Mailer(object):
    def load_config(self,**options):
        self.options = options

    def sendmail(self,**kwargs):
        if config.get('debug') or self.options.get('debug'):
            msg = kwargs['msg']
            log.info(
                'DID NOT send email "{}" from "{}" to {}'.format(
                    msg['Subject'],
                    kwargs.get('from_addr'),
                    msg['To'],
                )
            )
            log.debug(msg.as_string())
            return

        log.info(
            'Sent email "{}" from "{}" to {}'.format(
                kwargs['msg']['Subject'],
                kwargs.get('from_addr'),
                kwargs['msg']['To'],
            )
        )
        host = self.options.get('host',config.email.host)
        server = smtplib.SMTP(host)
        kwargs['msg'] = kwargs['msg'].as_string()
        server.sendmail(**kwargs)
        server.quit()

    def attachment_create(self,fpath):
        full_fpath = paths.full_fpath(fpath)
        with open(full_fpath,'rb') as f:
            # FIXME: Do I need to handle mimetype?
            att = MIMEBase('application', "octet-stream")
            att.set_payload(f.read())
            encoders.encode_base64(att)
        att.add_header(
            'Content-Disposition',
            'attachment; filename="{}"'.format(os.path.basename(fpath))
        )
        return att

    def message_send(self,msg):
        return self.sendmail(
                    from_addr=msg['from'],
                    to_addrs=msg['to'].split(','),
                    msg=msg
                )

    def basic_send(
              self,
              from_addr,
              to_addrs,
              subject,
              body
          ):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = ", ".join(to_addrs)
        self.sendmail(
            from_addr=from_addr,
            to_addrs=to_addrs,
            msg=msg
        )

    def template_send(self,fpath,**kwargs):
        msg = self.template_parse(fpath,**kwargs)
        to = msg['to']
        if isinstance(to,basestring):
            to = [to.split(',')]
        self.sendmail(
            from_addr=msg['from'],
            to_addrs=to,
            msg=msg,
        )

    def template_parsestr(self,template,**tags):
        tags['config'] = config.dict()
        parsed_email = parsestr(template,**tags)
        if config.get('debug') or self.options.get('debug'):
            log.debug(u"---------\n"+parsed_email+"\n--------\n")
        return self.message_fromstr(parsed_email)

    def template_parse(self,fpath,**tags):
        tags['config'] = config.dict()
        parsed_email = parse(fpath,**tags)
        if config.get('debug') or self.options.get('debug'):
            log.debug(u"---------\n"+parsed_email+"\n--------\n")
        return self.message_fromstr(parsed_email)

    def template_sendstr(self,template,**kwargs):
        msg = self.template_parsestr(template,**kwargs)
        to = msg['to']
        if isinstance(to,basestring):
            to = [to.split(',')]
        self.sendmail(
            from_addr=msg['from'],
            to_addrs=to,
            msg=msg
        )

    def message_fromstr(self,parsed_email):
        # Decompose the email into constituent parts first
        elements = parsed_email.split('\n')
        headers = []
        content = []
        state = 'headers'
        for e in elements:
            if state == 'headers':
                if not e:
                    state = 'content'
                headers.append(e)
            else:
                content.append(e)

        # Parse the headers
        headers = u"\n".join(headers)+u"\n\n"
        e = Parser().parsestr(headers)

        # Reconstruct the email into mime formatted elements.
        msg = MIMEMultipart('mixed')
        for k,v in dict(e).items():
            msg[k] = v
        msg_text = MIMEMultipart('alternative')
        html = u"\n".join(content)
        text = BeautifulSoup(html,"html5lib").get_text()
        msg_text.attach(MIMEText(text,'plain',_charset='utf-8'))
        msg_text.attach(MIMEText(html,'html',_charset='utf-8'))
        msg.attach(msg_text)
        return msg

mailer = Mailer()

@initializer('email')
def load_config(**options):
    request_initialize('config',**options)
    email_config = config.email.dict()
    mailer.load_config(**email_config)

