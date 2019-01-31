from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig
from ftw.builder.testing import BUILDER_LAYER
from ftw.calendarexport.tests import builder
from ftw.events.tests import builders

class FtwCalendarexportLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        z2.installProduct(app, 'Products.DateRecurringIndex')
        z2.installProduct(app, 'ftw.simplelayout')
        z2.installProduct(app, 'ftw.events')
        z2.installProduct(app, 'ftw.calendar')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.events:default')
        applyProfile(portal, 'ftw.calendar:default')
        applyProfile(portal, 'ftw.calendarexport:default')

FTW_CALENDAREXPORT_FIXTURE = FtwCalendarexportLayer()

FTW_CALENDAREXPORT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_CALENDAREXPORT_FIXTURE, ),
    name="ftw.calendarexport:Integration")

FTW_CALENDAREXPORT_INTEGRATION_TESTING = FunctionalTesting(
    bases=(FTW_CALENDAREXPORT_FIXTURE, ),
    name="ftw.calendarexport:Functional")
