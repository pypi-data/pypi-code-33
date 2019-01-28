
import xml.etree.ElementTree as ET

from marketo.rfc3339 import rfc3339
from .lead_record import unwrap as lr_unwrap


def wrap(lead_selector="LastUpdateAtSelector", oldest_updated_at=None,
         latest_updated_at=None, batch_size=100, steam_position=False):
    if lead_selector == "LastUpdateAtSelector":
        stream_position_str = '' if not steam_position else '<streamPosition>{}</streamPosition>'.format(steam_position)
        resp = ('<ns1:paramsGetMultipleLeads>' +
                    '<leadSelector xsi:type="ns1:LastUpdateAtSelector">' +
                        '<oldestUpdatedAt>' + rfc3339(oldest_updated_at, utc=True, use_system_timezone=False) + '</oldestUpdatedAt>' +
                        '<latestUpdatedAt>' + rfc3339(latest_updated_at, utc=True, use_system_timezone=False) + '</latestUpdatedAt>' +
                    '</leadSelector>' +
                    '<batchSize>' + str(batch_size) + '</batchSize>' +
                    stream_position_str +
                    '</ns1:paramsGetMultipleLeads>')
        return resp
    else:
        raise NotImplementedError("Only LastUpdateAtSelector lead selector is currently supported")


def unwrap(response):
    root = ET.fromstring(response.text.encode("utf-8"))
    new_position = root.find('.//newStreamPosition').text
    remaining_count = root.find('.//remainingCount').text
    lead_records_xml = root.findall('.//leadRecord')
    return new_position, remaining_count, [lr_unwrap(lead_record_xml) for lead_record_xml in lead_records_xml]
