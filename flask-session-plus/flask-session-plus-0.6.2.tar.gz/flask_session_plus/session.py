from flask.sessions import SessionInterface as FlaskSessionInterface
from flask_session_plus.backends import SecureCookieSessionInterface, FirestoreSessionInterface
from flask_session_plus.backends import RedisSessionInterface, MongoDBSessionInterface, MemcachedSessionInterface
from flask_session_plus.core import MultiSession


class MultiSessionInterface(FlaskSessionInterface):

    backends = {
        'secure_cookie': SecureCookieSessionInterface,
        'firestore': FirestoreSessionInterface,
        'redis': RedisSessionInterface,
        'mongodb': MongoDBSessionInterface,
        'memcache': MemcachedSessionInterface,
    }

    def __init__(self, sessions_config):
        all_includes = []  # store all the defined includes
        check_auto = []  # store any 'session_fields' auto
        for i, session_conf in enumerate(sessions_config):
            session_fields = session_conf.get('session_fields')
            if session_fields is None:
                continue
            if isinstance(session_fields, dict):
                all_includes.extend(session_fields.get('include', []))
            elif isinstance(session_fields, list):
                all_includes.extend(session_fields)
            elif isinstance(session_fields, str) and session_fields == 'auto':
                check_auto.append(i)
            else:
                raise ValueError('session_fields type is incorrect')

        for auto in check_auto:
            sessions_config[auto]['session_fields'] = {'exclude': all_includes}

        self.session_interfaces = []
        for session_conf in sessions_config:
            session_fields = session_conf.get('session_fields')
            session_type = session_conf.pop('session_type')

            backend = self.backends.get(session_type)
            if backend:
                session_interface = (backend(**session_conf), session_fields)
                self.session_interfaces.append(session_interface)
            else:
                raise ValueError('Specified session_type not recognized as a valid one.')

    @staticmethod
    def get_session_for(session_interface, session, session_fields):
        """ Returns all the sessions configured for a particular session interface """

        if isinstance(session_fields, dict):
            include = session_fields.get('include', [])
            exclude = session_fields.get('exclude', [])
        else:
            include = session_fields
            exclude = []

        new_dict = {}
        if len(include) == 0:
            new_dict = dict(session)
        else:
            for field in include:
                if field in session:
                    new_dict[field] = session.get(field)

        for field in exclude:
            new_dict.pop(field, None)

        modified = False
        for field in include:
            modified = modified or field in session.tracked_status
            if modified:
                break

        new_session = session_interface.session_class(new_dict)  # new session
        new_session.modified = modified  # assign modified flag
        cookie_name = session_interface.cookie_name
        new_session.sid = {cookie_name: session.get_sid(cookie_name)}  # assign session id
        if session.is_permanent(session_interface.cookie_name):
            new_session.set_permanent(session_interface.cookie_name)  # assign permanent status
        return new_session

    def open_session(self, app, request):
        """ Opens all the inner session interfaces and integrates all the sessions into one """
        common_dict = {}
        session_sids = {}
        permanents = set()
        for si, _ in self.session_interfaces:
            session = si.open_session(app, request)
            if session is not None:
                # 1st: update dict values
                common_dict.update(dict(session))
                # 2nd: integrate session sid if available
                session_sids[si.cookie_name] = session.get_sid(si.cookie_name)
                # 3rd: add permanent status
                if session.is_permanent(si.cookie_name):
                    permanents.add(si.cookie_name)
        multi_session = MultiSession(common_dict, sid=session_sids)
        for cookie_name in permanents:
            multi_session.set_permanent(cookie_name)
        return multi_session

    def save_session(self, app, session, response):
        """ Saves all session info into each of the session interfaces """
        for si, session_fields in self.session_interfaces:
            interface_session = self.get_session_for(si, session, session_fields)
            si.save_session(app, interface_session, response)


class Session(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.session_interface = self.create_session_interface(app)

    @staticmethod
    def create_session_interface(app):
        sessions_config = app.config.get('SESSION_CONFIG', [])
        if not sessions_config:
            # add the default session
            sessions_config.append({
                'cookie_name': app.config.get('SESSION_COOKIE_NAME'),
                'cookie_domain': app.config.get('SESSION_COOKIE_DOMAIN'),
                'cookie_path': app.config.get('SESSION_COOKIE_PATH'),
                'cookie_httponly': app.config.get('SESSION_COOKIE_HTTPONLY'),
                'cookie_secure': app.config.get('SESSION_COOKIE_SECURE'),
                'cookie_max_age': None,
            })

        for session in sessions_config:
            if not session.get('cookie_name'):
                raise ValueError('Each session configuration must define a cookie name')
            session.setdefault('session_type', 'secure_cookie')  # the session Interface to be used
            session.setdefault('session_fields', [])  # the list of fields used for this session

        return MultiSessionInterface(sessions_config)
