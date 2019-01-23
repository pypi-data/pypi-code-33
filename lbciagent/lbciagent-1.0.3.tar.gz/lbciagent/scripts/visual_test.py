import logging
from lbciagent import LbCIAgent
logging.basicConfig(level=logging.INFO)
import urllib2
import json
from datetime import datetime


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
            'priority': LbCIAgent.computePriority(slot['doc']['slot'],
                                                  str(p['platform']))
        })

results = sorted(results, key=lambda k: k['priority'], reverse=True)
for el in results:
    print("%s - %s - %s" % (el['priority'], el['slot'], el['platform']))
