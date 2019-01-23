from email.mime.text import MIMEText
from typing import List, Dict

import aiosmtplib
from sanic.log import logger

from longitude import config
from jinja2 import Environment, PackageLoader


class Mailer:

    smtp = None

    async def connect(self):
        self.smtp = aiosmtplib.SMTP(
            hostname=config.MAIL_HOSTNAME,
            port=config.MAIL_PORT,
            timeout=config.MAIL_TIMEOUT,

        )
        await self.smtp.connect(use_tls=config.MAIL_USE_TLS)

        if config.MAIL_USERNAME:
            await self.smtp.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)

    async def send_tpl_email(
            self,
            subject: str,
            body_template: str,
            addressee: str,
            context: Dict
    ):
        application, template = body_template.split('|')

        env = Environment(loader=PackageLoader(application, 'templates'))

        template = env.get_template(template)

        body = template.render(**context)

        message = MIMEText(body)
        message['From'] = config.MAIL_FROM_DEFAULT
        message['To'] = addressee
        message['Subject'] = subject

        if config.DEBUG:
            logger.debug('Sending email\n' + str(message))

        return await self.smtp.send_message(message)

    def close(self):

        self.smtp.close()
