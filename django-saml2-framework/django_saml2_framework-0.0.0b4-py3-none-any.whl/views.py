import logging
from hashlib import sha1

import saml2.xmldsig as ds
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseRedirect, \
    HttpResponseServerError
from django.shortcuts import reverse
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from saml2 import BINDING_HTTP_ARTIFACT, element_to_extension_element
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_SOAP
from saml2.client import Saml2Client
from saml2.extension.pefim import SPCertEnc
from saml2.httputil import Redirect
from saml2.ident import NameID, code
from saml2.metadata import entity_descriptor
from saml2.response import VerificationError
from saml2.s_utils import UnknownPrincipal
from saml2.s_utils import UnsupportedBinding
from saml2.s_utils import rndstr
from saml2.saml import AUTHN_PASSWORD
from saml2.samlp import Extensions
from saml2.server import Server
from saml2.sigver import SignatureError
from saml2.sigver import verify_redirect_signature
from six import text_type

from django_saml2_framework.ident import UserIdentity
from django_saml2_framework.models import IdentityProvider, ServiceProvider
from django_saml2_framework.session import SessionStorage

logger = logging.getLogger('django')


# todo: why Cache class?
class Cache(object):
    def __init__(self):
        self.uid2user = {}
        self.cookie_name = "spauthn"
        self.outstanding_queries = {}
        self.outstanding_certs = {}
        self.relay_state = {}
        self.user = {}
        self.result = {}

    def get_user(self, environ):
        cookie = environ.get("HTTP_COOKIE", "")
        logger.debug("Cookie: %s", cookie)
        if cookie:
            cookie_obj = SimpleCookie(cookie)
            morsel = cookie_obj.get(self.cookie_name, None)
            if morsel:
                try:
                    return self.uid2user[morsel.value]
                except KeyError:
                    return None
            else:
                logger.debug("No %s cookie", self.cookie_name)

        return None

    def delete_cookie(self, environ):
        cookie = environ.get("HTTP_COOKIE", "")
        logger.debug("delete cookie: %s", cookie)
        if cookie:
            _name = self.cookie_name
            cookie_obj = SimpleCookie(cookie)
            morsel = cookie_obj.get(_name, None)
            cookie = SimpleCookie()
            cookie[_name] = ""
            cookie[_name]["path"] = "/"
            logger.debug("Expire: %s", morsel)
            cookie[_name]["expires"] = _expiration("now")
            return cookie.output().split(": ", 1)
        return None

    def set_cookie(self, user):
        uid = rndstr(32)
        self.uid2user[uid] = user
        cookie = SimpleCookie()
        cookie[self.cookie_name] = uid
        cookie[self.cookie_name]["path"] = "/"
        cookie[self.cookie_name]["expires"] = _expiration(480)
        logger.debug("Cookie expires: %s", cookie[self.cookie_name]["expires"])
        return cookie.output().split(": ", 1)


CACHE = Cache()


class Saml2Mixin(object):
    model = None

    def dispatch(self, request, entity_id=None, *args, **kwargs):
        self.entity_id = entity_id or ''
        return super(Saml2Mixin, self).dispatch(request, *args, **kwargs)

    @property  # todo: cached
    def provider(self):
        query = {'is_default': True}
        if self.entity_id:
            query = {'entity': self.entity_id}
        return self.model._default_manager.get(**query)

    @property
    def config(self):
        return self.provider.config

    def unpack_redirect(self):
        # return self.request.GET
        return dict([(k, v) for k, v in self.request.GET.items()])

    def unpack_post(self):
        return dict([(k, v) for k, v in self.request.POST.items()])

    def unpack_soap(self):
        try:
            query = self.request.body
            return {"SAMLRequest": query, "RelayState": ""}
        except Exception:
            return None

    def unpack_either(self):
        if self.request.method == "GET":
            _dict = self.unpack_redirect()
        elif self.request.method == "POST":
            _dict = self.unpack_post()
        else:
            _dict = None
        logger.debug("_dict: %s", _dict)
        return _dict

    def operation(self, _dict, binding):
        logger.debug("_operation: %s", _dict)
        if not _dict and not ('SAMLRequest' in _dict or 'SAMLResponce' in _dict):
            return HttpResponseBadRequest('Error parsing request or no request')
        else:
            # try:
            #     return self.do(_dict["SAMLRequest"], binding,
            #                    _dict["RelayState"])
            # except KeyError:
            #     # Can live with no relay state
            #     return self.do(_dict["SAMLRequest"], binding)
            try:
                _relay_state = _dict["RelayState"]
            except KeyError:
                _relay_state = ""
            if "SAMLResponse" in _dict:
                return self.do(_dict["SAMLResponse"], binding, relay_state=_relay_state, mtype="response")
            elif "SAMLRequest" in _dict:
                return self.do(_dict["SAMLRequest"], binding, relay_state=_relay_state, mtype="request")

    def artifact_operation(self, _dict):
        if not _dict:
            return HttpResponseBadRequest("Missing query")
        else:
            # exchange artifact for request
            request = self.idp.artifact2message(_dict["SAMLart"], "spsso")
            try:
                return self.do(request, BINDING_HTTP_ARTIFACT,
                               _dict["RelayState"])
            except KeyError:
                return self.do(request, BINDING_HTTP_ARTIFACT)

    def response(self, binding, http_args):
        if binding == BINDING_HTTP_ARTIFACT:
            # todo: why?
            resp = Redirect()
        elif binding == BINDING_HTTP_REDIRECT:
            resp = HttpResponse(content=http_args["data"], status=307)
        else:
            resp = HttpResponse(content=http_args["data"])

        for header, value in http_args['headers']:
            resp[header] = value

        return resp

    def do(self, query, binding, relay_state="", mtype=None):
        raise NotImplementedError("todo: saml not implemented")

    def get(self, request, *args, **kwargs):
        _dict = self.unpack_redirect()
        return self.operation(_dict, BINDING_HTTP_REDIRECT)

    # def redirect(self):
    #     """ Expects a HTTP-redirect request """

    #     _dict = self.unpack_redirect()
    #     return self.operation(_dict, BINDING_HTTP_REDIRECT)

    def post(self, request, *args, **kwargs):
        """ Expects a HTTP-POST request """

        _dict = self.unpack_post()
        return self.operation(_dict, BINDING_HTTP_POST)

    def artifact(self):
        # Can be either by HTTP_Redirect or HTTP_POST
        _dict = self.unpack_either()
        return self.artifact_operation(_dict)

    def soap(self):
        """
        Single log out using HTTP_SOAP binding
        """
        logger.debug("- SOAP -")
        _dict = self.unpack_soap()
        logger.debug("_dict: %s", _dict)
        return self.operation(_dict, BINDING_SOAP)

    def uri(self):
        _dict = self.unpack_either()
        return self.operation(_dict, BINDING_SOAP)

    # def not_authn(self, key):
    #     """
    #
    #
    #     :return:
    #     """
    #     loc = "http://%s/login" % (self.environ["HTTP_HOST"])
    #     loc += "?%s" % urllib.urlencode({"came_from": self.environ[
    #         "PATH_INFO"], "key": key})
    #     headers = [('Content-Type', 'text/plain')]
    #
    #     logger.debug("location: %s", loc)
    #     logger.debug("headers: %s", headers)
    #
    #     resp = Redirect(loc, headers=headers)
    #
    #     return resp(self.environ, self.start_response)


TICKETS = {}


class Saml2IdpMixin(Saml2Mixin):
    model = IdentityProvider

    @property
    def idp(self) -> Server:
        # todo: get idp from self.provider
        server = Server(config=self.config)
        server.ticket = TICKETS
        server.session_db = SessionStorage()
        return server

    def not_authn(self, key, requested_authn_context):
        return HttpResponseRedirect(self.provider.reverse('idp_login') + '?key=' + key)
        # ruri = geturl(self.environ, query=False)
        # return do_authentication(self.environ, self.start_response,
        #                          authn_context=requested_authn_context,
        #                          key=key, redirect_uri=ruri)


CLIENT_STATE = {}

_SP_CLIENT = None


class Saml2SpMixin(Saml2Mixin):
    model = ServiceProvider
    # todo: build a new cache
    cache = CACHE

    @cached_property  # todo: cache
    def sp(self) -> Saml2Client:
        global _SP_CLIENT

        if _SP_CLIENT is None:
            logger.info('I am building a new client for the SP.')
            _SP_CLIENT = Saml2Client(config=self.config, )  # state_cache=CLIENT_STATE)
        return _SP_CLIENT
        # return Saml2Client(config=self.config, state_cache=CLIENT_STATE)


class IdpMetadataView(Saml2IdpMixin, View):
    def get(self, request, *args, **kwargs):
        metadata = entity_descriptor(self.config)
        return HttpResponse(content=text_type(metadata).encode('utf-8'), content_type="text/xml; charset=utf8")


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class IdpSsoView(Saml2IdpMixin, View):
    response_bindings = None  # todo: why is this here.

    def get(self, request, *args, **kwargs):
        """ This is the HTTP-redirect endpoint """

        logger.info("--- In SSO Redirect ---")
        _info = self.unpack_redirect()
        # logger.info(_info)
        try:
            _key = _info["key"]
            _info = self.idp.ticket[_key]
            self.req_info = _info["req_info"]
            del self.idp.ticket[_key]
        except KeyError:
            try:
                self.req_info = self.idp.parse_authn_request(_info["SAMLRequest"], BINDING_HTTP_REDIRECT)
            except KeyError:
                raise Exception('297')
                return HttpResponseBadRequest("Message signature verification failure")

            _req = self.req_info.message

            if "SigAlg" in _info and "Signature" in _info:  # Signed request
                issuer = _req.issuer.text
                _certs = self.idp.metadata.certs(issuer, "any", "signing")
                verified_ok = False
                for cert in _certs:
                    if verify_redirect_signature(_info, self.idp.sec.sec_backend, cert):
                        verified_ok = True
                        break
                if not verified_ok:
                    return HttpResponseBadRequest("Message signature verification failure")

            if request.user.is_authenticated:
                if _req.force_authn:
                    _info["req_info"] = self.req_info
                    key = self._store_request(_info)
                    return self.not_authn(key, _req.requested_authn_context)
                else:
                    return self.operation(_info, BINDING_HTTP_REDIRECT)
            else:
                _info["req_info"] = self.req_info
                key = self._store_request(_info)
                return self.not_authn(key, _req.requested_authn_context)
        else:
            return self.operation(_info, BINDING_HTTP_REDIRECT)

    def do(self, query, binding_in, relay_state="", mtype='request'):
        try:
            resp_args, _resp = self.verify_request(query, binding_in)
        except UnknownPrincipal as excp:
            logger.error("UnknownPrincipal: %s", excp)
            return HttpResponseNotAllowed("UnknownPrincipal: %s" % (excp,))
        except UnsupportedBinding as excp:
            logger.error("UnsupportedBinding: %s", excp)
            return HttpResponseNotAllowed("UnsupportedBinding: %s" % (excp,))

        if not _resp:
            # logger.info(['SIGN REPO', resp_args])
            # identity = USERS[self.user].copy()
            # # identity["eduPersonTargetedID"] = get_eptid(IDP, query, session)
            # logger.info("Identity: %s", identity)
            #
            # if REPOZE_ID_EQUIVALENT:
            #     identity[REPOZE_ID_EQUIVALENT] = self.request.user

            # todo: some kind of auth check?
            logger.info(resp_args.keys())
            # logger.info(resp_args.get('name_id_policy'))
            # logger.info([self.idp.config.policy, self.idp.config.name_form, self.idp.config.name_id_format, self.idp.config.name_qualifier])
            # if not resp_args.get('name_id_policy', None):
            #     resp_args.update(name_id_policy=NAMEID_FORMAT_EMAILADDRESS)
            # to change
            try:
                sign_assertion = self.idp.config.getattr("sign_assertion", "idp")
                # logger.info(['sign_assertion', sign_assertion])
                if sign_assertion is None:
                    sign_assertion = False

                logger.info(self.idp.config.getattr("attribute_converters", "idp"))
                logger.info(self.idp.config.attribute_converters)

                for attr_conv in self.idp.config.attribute_converters[-1:]:
                    logger.info([attr_conv.name_format, attr_conv._to])
                    logger.info([attr_conv.name_format, attr_conv._fro])

                # user = {'username': self.request.user.username,
                #         'email_addr': self.request.user.email,
                #         'first_name': self.request.user.first_name,
                #         'last_name': self.request.user.last_name,
                #         # 'FirstName': self.request.user.first_name,
                #         'LastName': self.request.user.last_name,
                #         }
                user = UserIdentity().create_authn_identity(None, self.request.user)

                logger.info(['USER', user])

                name_id = NameID(text=self.request.user.email)
                # logger.info(['self.idp.sec.cert_handler.generate_cert()', self.idp.sec.cert_handler.generate_cert()])
                # logger.info(['self.idp.sec.cert_handler.generate_cert()', self.idp.class_refsec.cert_handler])
                # logger.info(['self.idp.sec.cert_handler.generate_cert()', self.idp.sec.cert_handler.cert_file])
                _resp = self.idp.create_authn_response(user, userid=str(self.request.user.pk),
                                                       #   name_id_policy=NAMEID_FORMAT_EMAILADDRESS,
                                                       authn={'class_ref': AUTHN_PASSWORD},
                                                       # AUTHN_BROKER[self.environ["idp.authn_ref"]], # todo why does this work?
                                                       #   name_id=name_id,
                                                       sign_assertion=sign_assertion,
                                                       # todo: how should sign_response get set?
                                                       sign_response=True, **resp_args)
            except Exception as excp:
                raise excp
                logging.exception(excp)
                return HttpResponseServerError("Exception: %s" % (excp,))

        logger.info("AuthNResponse: %s", _resp)
        http_args = self.idp.apply_binding(self.binding_out,
                                           "%s" % _resp, self.destination,
                                           relay_state, response=True)
        # logger.debug("HTTPargs: %s", http_args)
        # print('&&&&&&&&&&&&&&&')
        # print(self.binding_out)
        # print('&&&&&&&&&&&&&&&')
        return HttpResponse(content=http_args['data'])
        # return self.response(self.binding_out, http_args)

    def verify_request(self, query, binding):
        """
        :param query: The SAML query, transport encoded
        :param binding: Which binding the query came in over
        """
        resp_args = {}
        if not query:
            logger.info("Missing QUERY")
            resp = HttpResponseNotAllowed('Unknown user')
            return resp_args, resp

        if not self.req_info:
            print('was not')
            self.req_info = self.idp.parse_authn_request(query, binding)

        logger.info("parsed OK")
        _authn_req = self.req_info.message
        logger.info("%s", _authn_req)

        # print('-------------------')
        # # pprint(IDP.metadata)
        # print('-------------------')
        # print(self.req_info)
        # print('-------------------')
        # print(_authn_req)
        # print('*****')
        # print(_authn_req.name_id_policy)
        # print('-------------------')
        self.binding_out, self.destination = self.idp.pick_binding(
            "assertion_consumer_service",
            bindings=self.response_bindings,
            entity_id=_authn_req.issuer.text)
        # # todo: hard coded
        # self.binding_out, self.destination = (BINDING_HTTP_POST,  'https://sso-sp-dev.edustaff.org/')

        logger.debug("Binding: %s, destination: %s", self.binding_out, self.destination)

        resp_args = {}
        try:
            resp_args = self.idp.response_args(_authn_req)
            _resp = None
        except UnknownPrincipal as excp:
            _resp = self.idp.create_error_response(_authn_req.id, self.destination, excp)
        except UnsupportedBinding as excp:
            _resp = self.idp.create_error_response(_authn_req.id, self.destination, excp)

        return resp_args, _resp

    def _store_request(self, _dict):
        logger.debug("_store_request: %s", _dict)
        key = sha1(_dict["SAMLRequest"].encode()).hexdigest()
        # store the AuthnRequest
        self.idp.ticket[key] = _dict
        return key


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class IdpSloView(Saml2IdpMixin, View):
    def do(self, request, binding, relay_state="", mtype=None):
        logger.info("--- Single Log Out Service ---")
        # logger.info(request)
        try:
            # _, body = request.split("\n")
            logger.debug("req: '%s'", request)
            req_info = self.idp.parse_logout_request(request, binding)
        except Exception as exc:
            logger.error("Bad request: %s", exc)
            return HttpResponseBadRequest("%s" % exc)

        msg = req_info.message
        if msg.name_id:
            # todo: is this local logout?
            # lid = self.idp.ident.find_local_id(msg.name_id)
            # logger.info("local identifier: %s", lid)
            # if lid in self.idp.cache.user2uid:
            #     uid = self.idp.cache.user2uid[lid]
            #     if uid in self.idp.cache.uid2user:
            #         del self.idp.cache.uid2user[uid]
            #     del self.idp.cache.user2uid[lid]
            # # remove the authentication
            try:
                self.idp.session_db.remove_authn_statements(msg.name_id)
            except KeyError as exc:
                logger.error("ServiceError: %s", exc)
                return HttpResponseServerError("%s" % exc)

        # todo: this could raise a SAMLError("Unknown entity or unsupported bindings")
        resp = self.idp.create_logout_response(msg, [binding])

        if binding == BINDING_SOAP:
            destination = ""
            response = False
        else:
            binding, destination = self.idp.pick_binding(
                "single_logout_service", [binding], "spsso", req_info
            )
            response = True

        try:
            hinfo = self.idp.apply_binding(binding, "%s" % resp, destination, relay_state, response=response)
        except Exception as exc:
            logger.error("ServiceError: %s", exc)
            return HttpResponseServerError("%s" % exc)

        # _tlh = dict2list_of_tuples(hinfo["headers"])
        # delco = delete_cookie(self.environ, "idpauthn")
        # if delco:
        #     hinfo["headers"].append(delco)
        #
        # todo: how to log the user out?
        #
        logout(self.request)

        # logger.info("Header: %s", hinfo["headers"])
        # resp = Response(hinfo["data"], headers=hinfo["headers"])
        return self.response(binding, hinfo)


class IdpLoginView(LoginView):
    template_name = 'django_saml2_framework/registration/login.html'

    def get_redirect_url(self):
        # todo: store in session
        # todo: what if there is no key?
        return reverse('idp_sso') + "?key=" + self.request.GET.get('key')


class IdpLogoutView(LogoutView):
    template_name = 'django_saml2_framework/registration/logged_out.html'


class SpMetadataView(Saml2SpMixin, View):
    def get(self, request, *args, **kwargs):
        metadata = entity_descriptor(self.config)
        return HttpResponse(content=text_type(metadata).encode('utf-8'), content_type="text/xml; charset=utf8")


class SpLoginView(Saml2SpMixin, View):
    # todo: what about this?
    bindings = [
        BINDING_HTTP_REDIRECT,
        BINDING_HTTP_POST,
        # BINDING_HTTP_ARTIFACT,
    ]

    def get(self, request, *args, **kwargs):
        came_from = request.META.get('HTTP_REFERER', None)

        logger.debug("[sp.challenge] RelayState >> '%s'", came_from)

        # If more than one idp and if none is selected, I have to do wayf
        (done, response) = self._pick_idp(came_from)
        # Three cases: -1 something went wrong or Discovery service used
        #               0 I've got an IdP to send a request to
        #               >0 ECP in progress
        logger.debug("_idp_pick returned: %s", done)
        if done == -1:
            return response
        elif done > 0:
            self.cache.outstanding_queries[done] = came_from
            raise Exception('SAML ECP handling?')
            # return ECPResponse(response)
        else:
            entity_id = response
            # Do the AuthnRequest
            resp = self.redirect_to_auth(self.sp, entity_id, came_from)
            return resp  # resp(self.environ, self.start_response)

    def _pick_idp(self, came_from):
        idps = self.sp.metadata.with_descriptor("idpsso")
        idp_entity_id = None
        if len(idps) == 1:
            # idps is a dictionary
            idp_entity_id = list(idps.keys())[0]
        elif not len(idps):
            return -1, HttpResponseServerError("Misconfiguration")
        else:
            return -1, HttpResponseServerError("No WAYF or DS present!")

        logger.info("Chosen IdP: '%s'", idp_entity_id)
        return 0, idp_entity_id

        # def _pick_idp(self, came_from):
        #     """
        #     If more than one idp and if none is selected, I have to do wayf or
        #     disco
        #     """

        #     # _cli = self.sp

        #     logger.debug("[_pick_idp] %s", self.environ)
        #     # if "HTTP_PAOS" in self.environ:
        #     #     if self.environ["HTTP_PAOS"] == PAOS_HEADER_INFO:
        #     #         if MIME_PAOS in self.environ["HTTP_ACCEPT"]:
        #     #             # Where should I redirect the user to
        #     #             # entityid -> the IdP to use
        #     #             # relay_state -> when back from authentication

        #     #             logger.debug("- ECP client detected -")

        #     #             _rstate = rndstr()
        #     #             self.cache.relay_state[_rstate] = geturl(self.environ)
        #     #             _entityid = _cli.config.ecp_endpoint(self.environ["REMOTE_ADDR"])

        #     #             if not _entityid:
        #     #                 return -1, ServiceError("No IdP to talk to")
        #     #             logger.debug("IdP to talk to: %s", _entityid)
        #     #             return ecp.ecp_auth_request(_cli, _entityid, _rstate)
        #     #         else:
        #     #             return -1, ServiceError("Faulty Accept header")
        #     #     else:
        #     #         return -1, ServiceError("unknown ECP version")

        #     # Find all IdPs
        #     idps = self.sp.metadata.with_descriptor("idpsso")

        #     idp_entity_id = None

        #     kaka = self.environ.get("HTTP_COOKIE", "")
        #     if kaka:
        #         try:
        #             (idp_entity_id, _) = parse_cookie("ve_disco", "SEED_SAW", kaka)
        #         except ValueError:
        #             pass
        #         except TypeError:
        #             pass

        #     # Any specific IdP specified in a query part
        #     query = self.environ.get("QUERY_STRING")
        #     if not idp_entity_id and query:
        #         try:
        #             _idp_entity_id = dict(parse_qs(query))[self.idp_query_param][0]
        #             if _idp_entity_id in idps:
        #                 idp_entity_id = _idp_entity_id
        #         except KeyError:
        #             logger.debug("No IdP entity ID in query: %s", query)
        #             pass

        #     if not idp_entity_id:

        #         if self.wayf:
        #             if query:
        #                 try:
        #                     wayf_selected = dict(parse_qs(query))["wayf_selected"][0]
        #                 except KeyError:
        #                     return self._wayf_redirect(came_from)
        #                 idp_entity_id = wayf_selected
        #             else:
        #                 return self._wayf_redirect(came_from)
        #         elif self.discosrv:
        #             if query:
        #                 idp_entity_id = _cli.parse_discovery_service_response(
        #                     query=self.environ.get("QUERY_STRING")
        #                 )
        #             if not idp_entity_id:
        #                 sid_ = sid()
        #                 self.cache.outstanding_queries[sid_] = came_from
        #                 logger.debug("Redirect to Discovery Service function")
        #                 eid = _cli.config.entityid
        #                 ret = _cli.config.getattr("endpoints", "sp")["discovery_response"][
        #                     0
        #                 ][0]
        #                 ret += "?sid=%s" % sid_
        #                 loc = _cli.create_discovery_service_request(
        #                     self.discosrv, eid, **{"return": ret}
        #                 )
        #                 return -1, SeeOther(loc)
        #         elif len(idps) == 1:
        #             # idps is a dictionary
        #             idp_entity_id = list(idps.keys())[0]
        #         elif not len(idps):
        #             return -1, ServiceError("Misconfiguration")
        #         else:
        #             return -1, NotImplemented("No WAYF or DS present!")

        #     logger.info("Chosen IdP: '%s'", idp_entity_id)
        #     return 0, idp_entity_id

    def redirect_to_auth(self, _cli, entity_id, came_from, sigalg=""):
        try:
            # Picks a binding to use for sending the Request to the IDP
            _binding, destination = _cli.pick_binding(
                "single_sign_on_service", self.bindings, "idpsso", entity_id=entity_id
            )
            logger.debug("binding: %s, destination: %s", _binding, destination)
            # Binding here is the response binding that is which binding the
            # IDP should use to return the response.
            acs = _cli.config.getattr("endpoints", "sp")["assertion_consumer_service"]
            # just pick one
            endp, return_binding = acs[0]

            extensions = None
            cert = None
            if _cli.config.generate_cert_func is not None:
                cert_str, req_key_str = _cli.config.generate_cert_func()
                cert = {"cert": cert_str, "key": req_key_str}
                spcertenc = SPCertEnc(
                    x509_data=ds.X509Data(
                        x509_certificate=ds.X509Certificate(text=cert_str)
                    )
                )
                extensions = Extensions(
                    extension_elements=[element_to_extension_element(spcertenc)]
                )

            req_id, req = _cli.create_authn_request(
                destination,
                binding=return_binding,
                extensions=extensions,
                # nameid_format=NAMEID_FORMAT_PERSISTENT,
            )
            _rstate = rndstr()
            self.cache.relay_state[_rstate] = came_from
            ht_args = _cli.apply_binding(
                _binding, "%s" % req, destination, relay_state=_rstate, sigalg=sigalg
            )
            _sid = req_id
            # logger.info(['request_id', _sid])

            if cert is not None:
                self.cache.outstanding_certs[_sid] = cert

        except Exception as exc:
            logger.exception(exc)
            resp = HttpResponseServerError("Failed to construct the AuthnRequest: %s" % exc)
            return resp

        # remember the request
        self.cache.outstanding_queries[_sid] = came_from

        # logger.info(ht_args['method'])
        resp = HttpResponse(content=ht_args['data'])
        for key, value in ht_args['headers']:
            logger.error(['KEY:', key, value])
            resp[key] = value
        # return resp
        return self.response(_binding, ht_args)


class SpLogoutView(Saml2SpMixin, View):
    def get(self, request, *args, **kwargs):
        name_id = self.request.session['saml2_name_id']  # todo: not always email

        logger.info(['USERS', self.sp.users.cache.subjects()])
        logger.info(self.request.session['saml2_name_id'])

        # What if more than one
        data = self.sp.global_logout(name_id)
        logger.info("[logout] global_logout > %s", data)

        for entity_id, logout_info in data.items():
            if isinstance(logout_info, tuple):
                binding, http_info = logout_info
                # todo: apply binding?????
                if binding == BINDING_HTTP_POST:
                    return self.response(binding, http_info)
                elif binding == BINDING_HTTP_REDIRECT:
                    for key, value in http_info["headers"]:
                        if key.lower() == "location":
                            return self.response(binding, http_info)

                    return HttpResponseServerError("missing Location header")
                else:
                    return HttpResponseServerError("unknown logout binding: %s", binding)
            else:  # result from logout, should be OK
                pass

        return HttpResponseServerError('no bindings')


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class SpAcsView(Saml2SpMixin, View):
    def do(self, response, binding, relay_state="", mtype="response"):
        """
        :param response: The SAML response, transport encoded
        :param binding: Which binding the query came in over
        """
        # tmp_outstanding_queries = dict(self.outstanding_queries)
        # logger.info(['response', response])
        if not response:
            logger.info("Missing Response")
            return HttpResponseNotAllowed("Unknown user")

        try:
            # logger.info(self.cache.outstanding_queries)
            conv_info = {
                "remote_addr": self.request.META["REMOTE_ADDR"],
                "request_uri": self.request.build_absolute_uri(),  # .META["REQUEST_URI"],
                "entity_id": self.sp.config.entityid,
                "endpoints": self.sp.config.getattr("endpoints", "sp"),
            }

            self.response = self.sp.parse_authn_request_response(
                response,
                binding,
                outstanding=self.cache.outstanding_queries,
                outstanding_certs=self.cache.outstanding_certs,
                conv_info=conv_info,
            )
        except UnknownPrincipal as excp:
            logger.error("UnknownPrincipal: %s", excp)
            return HttpResponseBadRequest("UnknownPrincipal: %s" % (excp,))
        except UnsupportedBinding as excp:
            logger.error("UnsupportedBinding: %s", excp)
            return HttpResponseBadRequest("UnsupportedBinding: %s" % (excp,))
        except VerificationError as err:
            return HttpResponseBadRequest("Verification error: %s" % (err,))
        except SignatureError as err:
            raise err
            return HttpResponseBadRequest("Signature error: %s" % (err,))
        except Exception as err:
            raise err
            return HttpResponseBadRequest("Other error: %s" % (err,))
        logger.info("AVA: %s", self.response.ava)
        # for cls in self.response.attribute_converters:
        #     logger.info([cls.name_format , cls, cls])

        for _assertion in self.response.assertions:
            if _assertion.attribute_statement:
                logger.info("Assertion contains %s attribute statement(s)",
                             (len(self.response.assertion.attribute_statement)))
                for _attr_statem in _assertion.attribute_statement:
                    # logger.info("Attribute Statement: %s" % (_attr_statem,))
                    logger.info(self.response.read_attribute_statement(_attr_statem))
        # logger.info(self.response)

        # todo: authentication backend stuffs

        User = get_user_model()
        query = {getattr(User, self.provider.name_id_user_field): self.response.name_id.text}
        try:
            user = User._default_manager.get(**query)  # (self.response.name_id, self.response.ava, self.response)
        except User.DoesNotExist as ex:
            if not self.provider.create_user:
                raise ex
            user = User._default_manager.create(**query)

        # login user
        login(self.request, user)

        # save name_id for later
        self.request.session['saml2_name_id'] = code(self.response.name_id)
        self.request.session['saml2_ava'] = str(self.response.ava)
        logger.info(self.response.ava)

        return HttpResponseRedirect('/')


@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class SpSloView(Saml2SpMixin, View):
    def do(self, message, binding, relay_state="", mtype="response"):
        # logger.info(message)
        # logger.info(binding)
        # try:
        #     txt = decode_base64_and_inflate(message)
        #     is_logout_request = "LogoutRequest" in txt.split(">", 1)[0]
        # except:  # TODO: parse the XML correctly
        #     is_logout_request = Falsen

        try:
            self.sp.parse_logout_request(message, binding)
        except Exception as ex:
            logger.info(ex)
            self.sp.parse_logout_request_response(message, binding)

        logout(self.request)

        return HttpResponseRedirect('/')
