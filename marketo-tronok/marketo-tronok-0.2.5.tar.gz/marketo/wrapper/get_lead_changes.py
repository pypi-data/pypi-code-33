
import xml.etree.ElementTree as ET
from .lead_activity import unwrap as la_unwrap
from collections import namedtuple
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

# For proper structure of the request, please see:
# http://developers.marketo.com/documentation/soap/getleadactivity/
# and
# http://app.marketo.com/soap/mktows/2_2?WSDL


def wrap(oldest_created_at=None, latest_created_at=None,
         offset=False, batch_size=1000):
    return ('< ns1: paramsGetLeadChanges >' +
                '<startPosition>' +
                    '<oldestCreatedAt>' + oldest_created_at.strftime('%Y-%m-%dT%H:%M:%SZ') + '</oldestCreatedAt >' +
                    '<latestCreatedAt>' + latest_created_at.strftime('%Y-%m-%dT%H:%M:%SZ') + '</latestCreatedAt>' +
                    '' if not offset else '<offset>{}</offset>'.format(offset) +
                '</startPosition>' +
                '<batchSize>' + str(batch_size) + '</batchSize>' +
            '< / ns1: paramsGetLeadChanges >')


def unwrap(response, new_stream_position):
    root = ET.fromstring(response.text.encode("utf-8"))
    activities = []
    new_position = root.find('.//newStreamPosition')
    latest_created_at = new_position.find('.//latestCreatedAt').text
    oldest_created_at = new_position.find('.//oldestCreatedAt').text
    offset = new_position.find('.//offset').text
    remaining_count = root.find('.//remainingCount').text
    for activity_el in root.findall('.//leadChangeRecord'):
        activity = la_unwrap(activity_el)
        activities.append(activity)
    return new_stream_position(latest_created_at, oldest_created_at, offset), remaining_count, activities
