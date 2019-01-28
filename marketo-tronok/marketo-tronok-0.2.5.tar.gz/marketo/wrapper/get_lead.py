
import xml.etree.ElementTree as ET
from .lead_record import unwrap as lr_unwrap


def wrap(email=None):
    return (
        '<ns1:paramsGetLead>' +
            '<leadKey>' +
                '<keyType>EMAIL</keyType>' +
                '<keyValue>' + email + '</keyValue>' +
            '</leadKey>' +
        '</ns1:paramsGetLead>')


def unwrap(response):
    root = ET.fromstring(response.text.encode("utf-8"))
    lead_record_xml = root.find('.//leadRecord')
    return lr_unwrap(lead_record_xml)
