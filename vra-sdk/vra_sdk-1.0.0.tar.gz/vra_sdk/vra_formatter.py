# -*- coding: utf-8 -*-
import json
import sys
from dateutil.parser import parse

from vra_sdk import vra_utils


def parse_string(element):
    """parser of vRa data of string type
    
    Args:
        element (dict): vRa data
    
    Returns:
        tuple: key,value of vRa data
    """

    return element["key"], element["value"]["value"]


def parse_string_without_key(element):
    """parser of vRa data without key
    
    Args:
        element (dict): vRa data
    
    Returns:
        string: vRa return value
    """

    return element["value"]


def parse_integer(element):
    """parser of vRa data integer type
    
    Args:
        element (dict): vRa data
    
    Returns:
        tuple: key,value of vRa data
    """

    return element["key"], int(element["value"]["value"])


def parse_decimal(element):
    """parser of vRa data decimal type
    
    Args:
        element (dict): vRa data
    
    Returns:
        tuple: key, value of vRa data
    """

    return element["key"], float(element["value"]["value"])


def parse_boolean(element):
    """parser for vRa data of boolean type
    
    Args:
        element (dict): vRa data
    
    Returns:
        tuple: key, value of vRa data
    """

    return element["key"], bool(element["value"]["value"])


def parse_datetime(element):
    """parser for vRa data datetime type
    
    Args:
        element (dict): vRa data
    
    Returns:
        tuple: key, datatime of vRa data
    """

    return element["key"], parse(element["value"]["value"]).strftime("%Y-%m-%dT%H:%M:%S.000+0100")


def parse_multiple(element):
    """parser for vRa data multiple type
    
    Args:
        element (dict): vRa data
    
    Returns:
        tuple: key, value of vRa data
    """

    parsed = []
    for elt in element["value"]["items"]:
        try:
            value = parse_key(elt)[1]
        except TypeError:
            value = parse_string_without_key(elt)
        parsed.append(value)
    return element["key"], parsed


def parse_complex(element):
    """parser for vRa data complex type
    
    Args:
        element (dict): vRa data
    
    Returns:
        tuple: key,value of vRa data
    """

    parsed = {}
    if "values" in element:
        entries = element["values"]["entries"]
    else:
        entries = element["value"]["values"]["entries"]

    for elt in entries:
        key, value = parse_key(elt)
        parsed[key] = value

    key = element["key"] if "key" in element else "0"
    return key, parsed


def parse_key(element):
    """proxy  method to class the specific parser
    
    Args:
        element (dict): vRa result element
    
    Returns:
        func: parser function to call
    """

    elt_type = element["value"]["type"] if "value" in element else element["type"]
    return getattr(sys.modules[__name__], "parse_%s" % elt_type.lower())(element)


def format_result(raw_result):
    """Format raw vRa result to a more user friendly result
    
    Args:
        raw_result (dict): raw data of vRa infrastructure when getting data
    
    Returns:
        dict: user friendly vRa result
    """

    data_clean = {}
    if 'id' in raw_result:
        data_clean["id"] = raw_result['id']

    if 'name' in raw_result:
        data_clean["name"] = raw_result['name']

    if 'status' in raw_result:
        data_clean["status"] = raw_result['status']

    if 'lease' in raw_result:
        data_clean["lease"] = raw_result['lease']

    if 'description' in raw_result:
        data_clean["description"] = raw_result['description']

    if 'organization' in raw_result:
        data_clean["business_group"] = {}
        data_clean["business_group"]["id"] = raw_result["organization"]["subtenantRef"]
        data_clean["business_group"]["label"] = raw_result["organization"]["subtenantLabel"]

    value_to_iter_on = "values" if "values" in raw_result else "resourceData"
    for elt in raw_result[value_to_iter_on]["entries"]:
        key_clean = elt['key'].replace('provider-', '')

        # if the key is not already set before
        if elt["value"] is not None and (key_clean not in data_clean or key_clean == "description"):
            data_clean[key_clean] = parse_key(elt)[1]
    return vra_utils.prettify_key(data_clean)
