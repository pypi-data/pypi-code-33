#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

# Import flask dependencies
from flask import Blueprint, render_template, request, jsonify, current_app as app

from requests import get
from bs4 import BeautifulSoup

# Define a blueprint
scrapper = Blueprint('scrapper', __name__, url_prefix='/')

################################################################################
# home blueprint functions
################################################################################


@scrapper.route('scrappe', methods=['GET'])
def scrappe():
    url = request.args.get('url', default=None)
    res = dict(imgs=[])

    if url is not None:
        body = get(url.rstrip('/'), timeout=3)
        soup = BeautifulSoup(body.content, "html.parser")
        imgs = soup.find_all("img")

        for img in imgs:
            src = img['src']

            app.logger.debug(src)

            if re.match(r'//(\w+)', src):
                res['imgs'].append(dict(src="http:{}".format(src)))
            elif re.match(r'/(\w+)', src):
                res['imgs'].append(dict(src="{}{}".format(url, src)))
            elif re.match(r'^http(s)?', src):
                res['imgs'].append(dict(src="{}".format(src)))

    res['status'] = 'success'
    res['hit'] = len(res['imgs'])
    return jsonify(res)
