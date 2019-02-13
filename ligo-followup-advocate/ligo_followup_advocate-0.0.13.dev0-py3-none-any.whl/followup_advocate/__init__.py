import os
import tempfile
import urllib
import webbrowser

import astropy.coordinates as coord
import astropy.time
import astropy.units as u
import healpy as hp
import lxml.etree
import numpy as np
from ligo.gracedb import rest
from ligo.skymap.io.fits import read_sky_map
from ligo.skymap.postprocess.ellipse import find_ellipse
from ligo.skymap.postprocess.find_injection import find_injection_moc

from .jinja import env
from .version import __version__  # noqa


def authors(authors, service=rest.DEFAULT_SERVICE_URL):
    """Write GCN Circular author list"""
    return env.get_template('authors.txt').render(authors=authors).strip()


def guess_skyloc_pipeline(comments):
    comments = comments.upper()
    skyloc_pipelines = ['cWB', 'BAYESTAR', 'LIB', 'LALInference', 'UNKNOWN']
    for skyloc_pipeline in skyloc_pipelines:
        if skyloc_pipeline.upper() in comments:
            break
    return skyloc_pipeline


def compose(gracedb_id, authors=(), mailto=False,
            service=rest.DEFAULT_SERVICE_URL, client=None):
    """Compose GCN Circular draft"""

    if client is None:
        client = rest.GraceDb(service)
    event = client.superevent(gracedb_id).json()
    preferred_event_id = event['preferred_event']
    preferred_event = client.event(preferred_event_id).json()
    voevents = client.voevents(gracedb_id).json()['voevents']
    log = client.logs(gracedb_id).json()['log']
    files = client.files(gracedb_id).json()

    gpstime = float(preferred_event['gpstime'])
    event_time = astropy.time.Time(gpstime, format='gps').utc

    skymaps = {}
    for voevent in voevents:
        voevent_text = client.files(gracedb_id, voevent['filename']).read()
        root = lxml.etree.fromstring(voevent_text)
        alert_type = root.find(
            './What/Param[@name="AlertType"]').attrib['value'].lower()
        url = root.find('./What/Group/Param[@name="skymap_fits"]')
        if url is None:
            continue
        url = url.attrib['value']
        _, filename = os.path.split(url)
        comments = '\n'.join(entry['comment'].upper() for entry in log
                             if entry['filename'] == filename)
        skyloc_pipeline = guess_skyloc_pipeline(comments)
        issued_time = astropy.time.Time(root.find('./Who/Date').text).datetime
        if filename not in skymaps:
            for message in log:
                if filename == message['filename']:
                    tag_names = message['tag_names']
                    if 'sky_loc' in tag_names and 'lvem' in tag_names:
                        skymaps[filename] = dict(
                            alert_type=alert_type,
                            pipeline=skyloc_pipeline,
                            filename=filename,
                            latency=issued_time-event_time.datetime)
                    break
    skymaps = list(skymaps.values())
    em_brightfile = 'source_classification.json'
    if em_brightfile in files:
        source_classification = client.files(
            gracedb_id, em_brightfile).json()
    else:
        source_classification = {}

    # adding the p_atro informations if available
    preferred_event_files = client.files(preferred_event_id).json()
    p_astro_file = 'p_astro.json'
    if p_astro_file in preferred_event_files:
        p_astro = client.files(preferred_event_id,
                               p_astro_file).json()
        p_BBH = p_astro["BBH"]
        p_BNS = p_astro["BNS"]
        p_NSBH = p_astro["NSBH"]
        p_Terr = p_astro["Terr"]

    else:
        p_astro = None
        p_BBH = None
        p_BNS = None
        p_NSBH = None
        p_Terr = None

    o = urllib.parse.urlparse(client.service_url)

    kwargs = dict(
        gracedb_id=gracedb_id,
        gracedb_service_url=urllib.parse.urlunsplit(
            (o.scheme, o.netloc, '/superevents/', '', '')),
        group=preferred_event['group'],
        pipeline=preferred_event['pipeline'],
        gpstime='{0:.03f}'.format(round(float(preferred_event['gpstime']), 3)),
        search=preferred_event.get('search', ''),
        far=preferred_event['far'],
        utctime=event_time.iso,
        authors=authors,
        instruments=preferred_event['instruments'].split(','),
        skymaps=skymaps,
        prob_has_ns=source_classification.get('Prob NS2'),
        prob_has_remnant=source_classification.get('Prob EMbright'),
        include_ellipse=None,
        p_astro=p_astro,
        p_BBH=p_BBH,
        p_BNS=p_BNS,
        p_NSBH=p_NSBH,
        p_Terr=p_Terr)

    if skymaps:
        preferred_skymap = skymaps[-1]['filename']
        cl = 90
        include_ellipse, ra, dec, a, b, pa, area = uncertainty_ellipse(
            gracedb_id, preferred_skymap, client, cl=cl)
        kwargs.update(
            preferred_skymap=preferred_skymap,
            cl=cl,
            include_ellipse=include_ellipse,
            ra=coord.Longitude(ra*u.deg),
            dec=coord.Latitude(dec*u.deg),
            a=coord.Angle(a*u.deg),
            b=coord.Angle(b*u.deg),
            pa=coord.Angle(pa*u.deg),
            ellipse_area=area)

    subject = env.get_template('subject.txt').render(**kwargs).strip()
    body = env.get_template('circular.txt').render(**kwargs).strip()

    if mailto:
        pattern = 'mailto:emfollow@ligo.org,dac@ligo.org?subject={0}&body={1}'
        url = pattern.format(
            urllib.parse.quote(subject),
            urllib.parse.quote(body))
        webbrowser.open(url)
    else:
        return '{0}\n{1}'.format(subject, body)


def read_map_gracedb(graceid, filename, client, moc_table=False):
    with tempfile.NamedTemporaryFile(mode='w+b') as localfile:
        remotefile = client.files(graceid, filename, raw=True).read()
        localfile.write(remotefile)
        localfile.flush()
        return read_sky_map(localfile.name, moc=moc_table)


def read_map_from_path(path, client):
    return read_map_gracedb(*path.split('/'), client)[0]


def mask_cl(p, level=90):
    pflat = p.ravel()
    i = np.flipud(np.argsort(p))
    cs = np.cumsum(pflat[i])
    cls = np.empty_like(pflat)
    cls[i] = cs
    cls = cls.reshape(p.shape)
    return cls <= 1e-2 * level


def compare_skymaps(paths, service=rest.DEFAULT_SERVICE_URL, client=None):
    """Produce table of sky map overlaps"""
    if client is None:
        client = rest.GraceDb(service)
    filenames = [path.split('/')[1] for path in paths]
    pipelines = [guess_skyloc_pipeline(filename) for filename in filenames]
    probs = [read_map_from_path(path, client) for path in paths]
    npix = max(len(prob) for prob in probs)
    nside = hp.npix2nside(npix)
    deg2perpix = hp.nside2pixarea(nside, degrees=True)
    probs = [hp.ud_grade(prob, nside, power=-2) for prob in probs]
    masks = [mask_cl(prob) for prob in probs]
    areas = [mask.sum() * deg2perpix for mask in masks]
    joint_areas = [(mask & masks[-1]).sum() * deg2perpix for mask in masks]

    kwargs = dict(params=zip(filenames, pipelines, areas, joint_areas))

    return env.get_template('compare_skymaps.txt').render(**kwargs)


def uncertainty_ellipse(graceid, filename, client, cl=90):
    """Compute uncertainty ellipses for a given skymap"""
    skymap_table = read_map_gracedb(graceid, filename, client, moc_table=True)
    result = find_injection_moc(skymap_table, contours=[cl/100])
    greedy_area = result.contour_areas[0]
    prob = read_map_gracedb(graceid, filename, client)[0]
    ra, dec, a, b, pa, ellipse_area = find_ellipse(prob, cl=cl,
                                                   projection='ARC',
                                                   nest=False)
    return ellipse_area <= 1.35*greedy_area, ra, dec, a, b, pa, ellipse_area
