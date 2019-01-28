from Testing.makerequest import makerequest
from plone import api
from zope.component.hooks import setHooks
from zope.component.hooks import setSite
import Zope2
import logging
import sys
import transaction

log = logging.getLogger()


class InstanceScript(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, run_as, server_url=None, context_path=None,
                 portal_id=None, **environ):
        environ['SERVER_URL'] = server_url
        self.app = makerequest(self.app, environ=environ)

        log.setLevel(0)

        # add 2 handlers: INFO to stdout, ERROR to stderr
        stdout = logging.StreamHandler(sys.stdout)
        stderr = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        stdout.setFormatter(formatter)
        stdout.setLevel(logging.INFO)
        log.addHandler(stdout)
        stderr.setFormatter(formatter)
        stderr.setLevel(logging.ERROR)
        log.addHandler(stderr)

        setHooks()
        if portal_id is not None:
            self.portal = self.app[portal_id]
        else:
            portals = self.app.objectValues('Plone Site')
            if len(portals) > 1:
                log.warn('More than one portal - using first one')
            self.portal = portals[0]
        self.portal.setupCurrentSkin(self.app.REQUEST)
        setSite(self.portal)
        self.app.REQUEST.other['PARENTS'] = [self.portal, self.app]
        self.app.REQUEST.other['VirtualRootPhysicalPath'] = (
            '', self.portal.id)

        with api.env.adopt_user(username=run_as):
            if context_path is not None:
                self.context = self.portal.restrictedTraverse(context_path)
            else:
                self.context = self.portal
            self.run()
        transaction.commit()

    def run(self):
        raise NotImplementedError


class ConsoleScript(InstanceScript):
    def __init__(self):
        pass

    def __call__(self, config_file, *args, **kwargs):
        # Zope automatically adds a StartupHandler
        # we're only interested in ERRORs during startup
        log.setLevel(logging.ERROR)

        starter = Zope2.Startup.run.configure(config_file)
        self.app = Zope2.app()

        # after startup, remove the StartupHandler
        # and init the instance's event.log
        log.handlers = []
        if starter.cfg.eventlog is not None:
            starter.cfg.eventlog()

        super(ConsoleScript, self).__call__(*args, **kwargs)
