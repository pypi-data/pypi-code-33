# -*- coding: utf-8 -*-
from urllib.parse import urlparse, urlencode
import hashlib
import datetime


class Render:
    @staticmethod
    def to_html(pio, personaliseResultWrapper):
        """ Renders results to an HTML table, fundamentally flawed at this point as there is no support for blends with more then 2 models"""
        html = "<h2>Results for group {label}</h2>".format(
            label=personaliseResultWrapper.experiment["abvariant"]["label"]
        )
        html += "<table>"
        html += "<tr><th>model1.name</th><th>model1.weight</th><th>model1.score</th><th>model2.name</th><th>model2.weight</th><th>model2.score</th><th>wscore</th><th>value</th></tr>"
        for res in personaliseResultWrapper._results:
            html += "<tr>"
            if len(res.components) == 0:
                # control
                html += "<td></td><td></td><td></td><td></td><td></td><td></td><td>{score}</td><td>{url}</td>".format(
                    score=res.fscore, url=res.target["value"]["url"]
                )
            elif len(res.components) == 1:
                # no blend
                html += "<td>{0}</td><td>{1}</td><td>{2:.2f}</td><td></td><td></td><td></td><td>{3}</td><td>{4}</td>".format(
                    res.components[0]["model"]["name"],
                    res.components[0]["weight"],
                    res.components[0]["cscore"],
                    res.fscore,
                    res.target["value"]["url"],
                )
            elif len(res.components) == 2:
                # blend
                html += "<td>{0}</td><td>{1}</td><td>{2:.2f}</td><td>{3}</td><td>{4}</td><td>{5:.2f}</td><td>{6}</td><td>{7}</td>".format(
                    res.components[0]["model"]["name"],
                    res.components[0]["weight"],
                    res.components[0]["cscore"],
                    res.components[1]["model"]["name"],
                    res.components[1]["weight"],
                    res.components[1]["cscore"],
                    res.fscore,
                    res.target["value"]["url"],
                )
            else:
                print(
                    "we don't support to_html() for results of blends with more then two models"
                )
                pass
            html += "</tr>"
        return html


class Dictionary:
    @staticmethod
    def merge(a, b):
        """Returns a new dictionary with merged contents of `a` and `b`

        :param a: first dictionary
        :type a: dictionary
        :param b: second dictionary
        :type b: dictionary
        :returns: merged dictionary
        :rtype: dictionary
        """

        x = a.copy()
        x.update(b)
        return x


class Uri:
    @staticmethod
    def query_params_from_dict(dic):
        """Returns a string of URL query params

        :param dic: input dictionary
        :type dic: dictionary
        :returns: URL query params
        :rtype: string
        """
        return urlencode(dic)

    @staticmethod
    def filter_default_setter(dic, splitter="__", default="exact"):
        """Prefixes Django style operators dictionary with a default 
        operator, only applies the default where there is no operator 
        specified (absence of the `splitter` token)

        :param dic: Django style operators dictionary
        :type dic: dictionary
        :param splitter: Django style splitter between property name and operator, defaults to "__"
        :type splitter: string, optional
        :param default: default operator, defaults to "exact"
        :type default: string, optional
        :returns: Django style operators dictionary with default operator prefixed 
        :rtype: dictionary
        """

        ndic = {}
        for key, value in dic.items():
            if splitter not in key:
                ndic["{}{}{}".format(key, splitter, default)] = value
            else:
                ndic[key] = value

        return ndic


class Connection:
    def __init__(self, scheme, hostname, port, username, password, version):
        self._scheme = scheme
        self._hostname = hostname
        self._port = int(port)
        self._username = username
        self._password = password
        self._version = version

    @property
    def baseurl(self):
        return "{scheme}://{hostname}:{port}/api/v{version}".format(
            scheme=self._scheme,
            hostname=self._hostname,
            port=self._port,
            version=self._version,
        )

    @staticmethod
    def from_uri(uri, version="1"):
        """Creates a Connection instance from a URI string

        Example URI: `http://user:password@localhost:5000`
        :param uri: PrimedIO URI
        :type uri: string
        :raises: ValueError if URI format does not match expectations
        :returns: Connection instance
        :rtype: Connection
        """
        u = urlparse(uri)

        if u.netloc.find("@") > -1 and (u.scheme == "http" or u.scheme == "https"):
            if u.scheme == "http":
                credentials, hostport = u.netloc.rsplit("@", 1)
                username, password, = credentials.split(":")
                if ":" in hostport:
                    hostname, port, = hostport.split(":")
                else:
                    raise ValueError(
                        "when specifying the http scheme you need to also specify a port"
                    )
            elif u.scheme == "https":
                credentials, hostport = u.netloc.rsplit("@", 1)
                username, password, = credentials.split(":")
                if ":" in hostport:
                    hostname, port, = hostport.split(":")
                else:
                    hostname = hostport
                    port = 443
            else:
                raise ValueError(
                    "unsupported scheme, only http and https are supported, you provided {}".format(
                        u.scheme
                    )
                )

            if len(username) == 0 or len(password) == 0:
                raise ValueError("you must provide a username and password")
        else:
            raise ValueError(
                "Expecting uri format: http://user:password@localhost:5000 got {}".format(
                    uri
                )
            )

        return Connection(
            scheme=u.scheme,
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            version=version,
        )

    def hmac_header(
        self,
        pubkey,
        secretkey,
        nonce=int(datetime.datetime.now(datetime.timezone.utc).timestamp()),
    ):
        """Returns an HMAC signed header for `personalize` calls

        :param pubkey: PrimedIO provided public key
        :type pubkey: string
        :param secretkey: PrimedIO provided secret key
        :type secretkey: string
        :param nonce: UTC timestamp in seconds, defaults to current timestamp
        :type nonce: integer, optional
        :returns: HMAC header
        :rtype: dictionary
        """
        local = hashlib.sha512()
        signature = "{}{}{}".format(pubkey, secretkey, nonce)

        local.update(signature.encode("utf-8"))

        return {
            "X-Authorization-Key": pubkey,
            "X-Authorization-Signature": local.hexdigest(),
            "X-Authorization-Nonce": str(nonce),
        }
