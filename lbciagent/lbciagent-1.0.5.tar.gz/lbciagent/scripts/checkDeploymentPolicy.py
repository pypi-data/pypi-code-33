import logging
from lbciagent import LbCIAgent
logging.basicConfig(level=logging.INFO)
import urllib2
import json
from datetime import datetime
from lbciagent import DeploymentPolicy
import sys


def display_all_slots(lbNightlyConf_path):
    try:
        from LbNightlyTools.Configuration import loadConfig
    except:
        raise Exception("Please add LbNightlyTools to PYTHONPATH")
    slots = loadConfig(lbNightlyConf_path)
    results = []
    for k, v in slots.iteritems():
        if v.enabled and 'cvmfs' in v.deployment:
            for p in v.platforms:
                results.append({
                    'platform': p,
                    'slot': k,
                    'priority': DeploymentPolicy.computePriority(k, p)
                })
    results = sorted(results, key=lambda k: k['priority'], reverse=True)
    return results


def display_build_ready():
    url = "https://lhcb-couchdb.cern.ch/nightlies-nightly/_design/" \
          "deployment/_view/ready?key=[\"%s\",\"cvmfs\"]" \
          "&include_docs=true" % datetime.now().strftime("%Y-%m-%d")

    response = urllib2.urlopen(url)
    slots = json.loads(response.read())
    results = []
    for slot in slots['rows']:
        for p in slot['value']:
            results.append({
                'platform': str(p['platform']),
                'slot': slot['doc']['slot'],
                'priority': DeploymentPolicy.computePriority(
                    slot['doc']['slot'], str(p['platform']))
            })

    results = sorted(results, key=lambda k: k['priority'], reverse=True)
    return results


if __name__ == '__main__':
    if len(sys.argv) == 2:
        results = display_all_slots(sys.argv[1])
    else:
        results = display_build_ready()

    for el in results:
        print("%s - %s - %s" % (el['priority'], el['slot'], el['platform']))
