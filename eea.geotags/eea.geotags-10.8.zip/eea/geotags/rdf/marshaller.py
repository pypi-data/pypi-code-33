# -*- coding: utf-8 -*-
""" RDF Marshaller module for geotags """

from eea.geotags.field.location import GeotagsFieldMixin
from eea.geotags.field.common import json2list
from eea.geotags.field.common import get_tags
from eea.geotags.interfaces import IGeoTags
from eea.geotags.rdf.country_groups import COUNTRY_GROUPS
from eea.geotags.storage.interfaces import IGeoTagged
from eea.rdfmarshaller.archetypes.fields import ATField2Surf
from eea.rdfmarshaller.archetypes.interfaces import IATField2Surf
from eea.rdfmarshaller.dexterity.fields import DXField2Surf
from eea.rdfmarshaller.dexterity.interfaces import IDXField2Surf
from eea.rdfmarshaller.interfaces import ISurfSession
from zope.component import adapts, getAdapter
from zope.interface import implements
from zope.schema import Field

import rdflib
import surf


class GeotagsField2Surf(object):

    def __init__(self, field, context, session):
        # Override init for DXField2Surf and ATField2Surf here.
        # Necessary because DXField2Surf.__init__ sets
        # self.name = field.__name__ which overwrites the class level
        # `name` property of any subclass. Making it impossible to set a
        # name different from the field name.
        super(GeotagsField2Surf, self).__init__(field, context, session)
        self.prefix = 'dcterms'
        self.name = 'spatial'

    def get_location(self):
        raise NotImplementedError('Subclassess must implement this!')

    def value(self):
        # create a GeoPoint Class
        SpatialThing = self.session.get_class(surf.ns.GEO.SpatialThing)

        geo = getAdapter(self.context, IGeoTags)

        output = []
        i = 0

        cty_names = {u'Macedonia': u'Former Yugoslav Republic of'
                                   u' Macedonia, the',
                     u'Czechia': u'Czech Republic',
                     u'Kosovo': u'Kosovo (UNSCR 1244/99)'}
        cty_names_keys = cty_names.keys()

        country_groups = COUNTRY_GROUPS
        country_groups_keys = country_groups.keys()
        country_groups_keys_index = [ki[0] for ki in country_groups_keys]
        for feature in geo.getFeatures():
            rdfp = self.session.get_resource("#geotag%s" % i, SpatialThing)

            label = feature['properties']['title']
            # do not add current countries_group locations as they
            # will be added on rdf export when adding all of the country groups
            if label in country_groups_keys_index:
                continue
            description = feature['properties']['description']
            if label in cty_names_keys:
                label = cty_names[label]
                description = label
            rdfp[surf.ns.RDFS['comment']] = description

            if label == description or not description:
                friendly_name = label
            else:
                friendly_name = label + ' (' + description + ')'
            rdfp[surf.ns.DCTERMS['title']] = friendly_name
            rdfp[surf.ns.RDFS['label']] = friendly_name

            tags = feature['properties']['tags']
            rdfp[surf.ns.DCTERMS['type']] = tags

            latitude = feature['properties']['center'][0]
            rdfp[surf.ns.GEO['lat']] = float(latitude)

            longitude = feature['properties']['center'][1]
            rdfp[surf.ns.GEO['long']] = float(longitude)

            other = feature['properties'].get('other', {})
            if other.has_key('geonameId'):
                geonamesURI = 'http://sws.geonames.org/%s/' % (
                    str(feature['properties']['other']['geonameId']))
                rdfp[surf.ns.OWL['sameAs']] = rdflib.URIRef(geonamesURI)
            rdfp.update()
            output.append(rdfp)
            i += 1

        # 85617 add country groups to rdf output
        found_groups = []
        location = self.get_location()
        correct_country_names = cty_names.values()
        for k, v in country_groups.items():
            differences = set(v).difference(location)
            if differences:
                for country_name in correct_country_names:
                    if country_name in differences:
                        differences.remove(country_name)
                if not differences:
                    found_groups.append(k)
            else:
                found_groups.append(k)
        for group in found_groups:
            label = group[0]
            if label in location:
                continue
            rdfp = self.session.get_resource("#geotag%s" % i, SpatialThing)
            title = group[1]
            full_title = label + ' (' + title + ')'
            rdfp[surf.ns.DCTERMS['title']] = full_title
            rdfp[surf.ns.RDFS['label']] = full_title
            rdfp[surf.ns.RDFS['comment']] = title + ': ' + \
                                            ', '.join(
                                                country_groups[(label, title)])
            rdfp[surf.ns.DCTERMS['type']] = 'countries_group'
            rdfp[surf.ns.SKOS['notation']] = label
            uri = 'http://rdfdata.eionet.europa.eu/eea/countries/%s' % label
            rdfp[surf.ns.OWL['sameAs']] = rdflib.URIRef(uri)
            rdfp.update()
            output.append(rdfp)
            i += 1

        return output


class GeotagsField2SurfDX(GeotagsField2Surf, DXField2Surf):
    implements(IDXField2Surf)
    adapts(Field, IGeoTagged, ISurfSession)

    def get_location(self):
        return json2list(get_tags(self.context)) or []


class GeotagsField2SurfAT(GeotagsField2Surf, ATField2Surf):
    """Adapter to express geotags field with RDF using Surf."""
    implements(IATField2Surf)
    adapts(GeotagsFieldMixin, IGeoTagged, ISurfSession)

    def get_location(self):
        location_value = self.context.location
        try:
            location = location_value.split('\n')
        except AttributeError:
            location = location_value

        return set(location)
