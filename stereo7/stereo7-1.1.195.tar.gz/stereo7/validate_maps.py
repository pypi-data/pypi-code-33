import xml.etree.ElementTree as ET
import game
import os
import fileutils
from project import Project

logs = []


def log(msg):
    logs.append(msg)


def get_maps():
    result = []
    for i in xrange(100):
        file = fileutils.root_dir + '/Resources/ini/maps/map%d.xml' % i
        if os.path.isfile(file):
            result.append(file)
        for ii in xrange(100):
            file = fileutils.root_dir + '/Resources/ini/maps/map%d_%d.xml' % (i, ii)
            if os.path.isfile(file):
                result.append(file)
    return result


def validate_maps_content():
    units = game.get_units_list()
    files = get_maps()
    for file in files:
        root = ET.parse(file).getroot()

        waves = root.find('waves')
        if waves is None:
            waves = root.find('waves_survival')
        routes = root.find('routes')
        units_on_map = {}

        def validate_route(routeindex):
            try:
                int(routeindex)
            except:
                log('Route with index [{}] not is digit. {}'.format(routeindex, file))
                return False
            for route in routes:
                if route.attrib['name'] == routeindex:
                    return True
            log('Route with index [{}] not found in {}'.format(routeindex, file))
            return False

        def validate_routesubtype(rst):
            if rst not in ['main', 'left', 'right', 'random']:
                log('Unknow value of routesubtype [{}] in {}'.format(rst, file))

        for wave in waves:
            if 'defaultname' in wave.attrib:
                unit = wave.attrib['defaultname']
                if unit not in units:
                    log('Invalid name of unit [{}] in {}'.format(unit, file))
                units_on_map[unit] = 1
            if 'defaultrouteindex' in wave.attrib:
                validate_route(wave.attrib['defaultrouteindex'])
            if 'defaultroutesubtype' in wave.attrib:
                validate_routesubtype(wave.attrib['defaultroutesubtype'])
            for unitxml in wave:
                unit = unitxml.attrib['name'] if 'name' in unitxml.attrib else ''
                units_on_map[unit] = 1
                if unit and unit not in units:
                    log('Invalid name of unit [{}] in{}'.format(unit, file))
                if 'routeindex' in unitxml.attrib:
                    validate_route(unitxml.attrib['routeindex'])
                if 'routesubtype' in unitxml.attrib:
                    validate_routesubtype(unitxml.attrib['routesubtype'])
        if 'max_creeps_on_level' in Project.instance.validate:
            max_count = Project.instance.validate['max_creeps_on_level']
        else:
            max_count = 8
        if len(units_on_map) > max_count:
            log('Many creeps in {} ({}>{})'.format(file, len(units_on_map), max_count))


def validate_count():
    count_xml = 0
    count_rewards = 0
    count_locations = 0

    maps = get_maps()
    count_xml = len(maps)

    file = fileutils.root_dir + '/Resources/ini/maps/levels.xml'
    if not os.path.isfile(file):
        return
    rewards = ET.parse(fileutils.root_dir + '/Resources/ini/maps/levels.xml').getroot()
    for child in rewards:
        if child.tag.startswith('level_'):
            count_rewards += 1

    location_xml = ET.parse(fileutils.root_dir + '/Resources/ini/map/maplayer.xml')
    locations = location_xml.getroot().find('locations')
    if locations is None or len(locations) == 0:
        location_xml = ET.parse(fileutils.root_dir + '/Resources/ini/map/locations.xml')
        locations = location_xml.getroot().find('locations')
    for _ in locations:
        count_locations += 1
    for index in xrange(100):
        node = 'locations_%d' % index
        locations = location_xml.getroot().find(node)
        if locations is not None and len(locations):
            for _ in locations:
                count_locations += 1

    valid = count_locations == count_xml and count_locations == count_rewards
    if not valid:
        log('Count of levels is difference: \n\tlocations: {}\n\trewards: {}\n\txmls: {}'.
            format(count_locations, count_rewards, count_xml))


def validate():
    validate_maps_content()
    validate_count()
