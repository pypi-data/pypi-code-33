
import re
import json
import traceback
import requests

from search_all import search
from search_engine.util import headers

from util import get_page

import logging
logging.basicConfig(filename='/tmp/search_mail.log', level=logging.INFO)

mail_regex = r"[a-zA-Z0-9\.\-_]+@"

def mail_fetch(mail_domain):
    regex_domain = mail_domain.replace(".", "\\.").replace("-", "\\-")
    this_regex = mail_regex + regex_domain

    keyword = '"@%s"' % mail_domain

    mails = []
    for result in search(keyword):
        logging.info(result)
        try:
            text = get_page(result)
        except:
            logging.info(traceback.format_exc())
            pass
        matchs = re.findall(this_regex, text)
        matchs = list(set(matchs))
        for match in matchs:
            logging.info(match)
            mails.append(match)

    return list(set(mails))
