
import xml.etree.ElementTree as ET
from .lead_activity import unwrap as la_unwrap
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

# For proper structure of the request, please see:
# http://developers.marketo.com/documentation/soap/getleadactivity/
# and
# http://app.marketo.com/soap/mktows/2_2?WSDL

def wrap(email=None, filters=[]):
    head = ('<ns1:paramsGetLeadActivity>' +
                '<leadKey>' +
                    '<keyType>EMAIL</keyType>' +
                        '<keyValue>')
    head += email + '</keyValue></leadKey>'

    tail = '</ns1:paramsGetLeadActivity>'

    if filters:
        head += '<activityFilter><includeTypes>'
        for f in filters:
            head += '<activityType>'+f+'</activityType>'

        head += '</includeTypes></activityFilter>'

    head += tail

    return head
    # return (
    #     '<ns1:paramsGetLeadActivity>' +
    #         '<leadKey>' +
    #             '<keyType>EMAIL</keyType>' +
    #             '<keyValue>' + email + '</keyValue>' +
    #         '</leadKey>' +
    #     '</ns1:paramsGetLeadActivity>')


def unwrap(response):
    root = ET.fromstring(response.text.encode("utf-8"))
    activities = []
    for activity_el in root.findall('.//activityRecord'):
        activity = la_unwrap(activity_el)
        activities.append(activity)
    return activities
