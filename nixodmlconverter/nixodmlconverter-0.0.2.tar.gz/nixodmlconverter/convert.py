import os
import sys

import argparse

import nixio as nix
import odml

from odml.tools.format_converter import VersionConverter
from odml.tools.odmlparser import ODMLReader
from odml.tools.parser_utils import InvalidVersionException

info = {"sections read": 0,
        "sections written": 0,
        "properties read": 0,
        "properties written": 0,
        "skipped empty properties": 0,
        "skipped binary values": 0,
        "skipped none values": 0,
        "type errors": 0}


def print_info():
    print("Conversion info")
    print("{sections read}\t Sections were read\n"
          "{sections written}\t Sections were written\n"
          "{properties read}\t Properties were read\n"
          "{properties written}\t Properties were written\n"
          "{skipped empty properties}\t Properties were skipped because they "
          "contained only None or binary values\n"
          "{skipped binary values}\t Values were skipped because they "
          "were of type 'binary'\n"
          "{skipped none values}\t Values were skipped because they were "
          "empty (None)\n"
          "{type errors}\t Type Errors were encountered\n".format(**info))


def convert_datetime(dt):
    return dt.isoformat()


def convert_value(v, dtype):
    global info
    if dtype == "binary":
        info["skipped binary values"] += 1
        return None
    if v is None:
        info["skipped none values"] += 1
        return None
    if dtype in ("date", "time", "datetime"):
        v = convert_datetime(v)
    return v


########### ODML -> NIX ##############

def odml_to_nix_recurse(odmlseclist, nixparentsec):
    global info
    for odmlsec in odmlseclist:
        info["sections read"] += 1
        secname = odmlsec.name
        definition = odmlsec.definition
        reference = odmlsec.reference
        repository = odmlsec.repository

        nixsec = nixparentsec.create_section(secname, odmlsec.type, oid=odmlsec.id)
        info["sections written"] += 1
        nixsec.definition = definition
        if reference is not None:
            nixsec.reference = reference
        if repository is not None:
            nixsec.repository = repository

        for odmlprop in odmlsec.properties:
            info["properties read"] += 1
            propname = odmlprop.name
            definition = odmlprop.definition
            odmlvalue = odmlprop.value
            nixvalues = []
            for v in odmlvalue:
                nixv = convert_value(v, odmlprop.dtype)
                if nixv is not None:
                    nixvalues.append(nixv)

            if not nixvalues:
                info["skipped empty properties"] += 1
                continue
            nixprop = nixsec.create_property(propname, nixvalues, oid=odmlprop.id)
            info["properties written"] += 1
            nixprop.definition = definition
            nixprop.unit = odmlprop.unit
            nixprop.uncertainty = odmlprop.uncertainty
            nixprop.reference = odmlprop.reference
            nixprop.odml_type = nix.property.OdmlType(odmlprop.dtype)
            nixprop.value_origin = odmlprop.value_origin
            nixprop.dependency = odmlprop.dependency
            nixprop.dependency_value = odmlprop.dependency_value

        odml_to_nix_recurse(odmlsec.sections, nixsec)


def write_odml_doc(odmldoc, nixfile):
    nixsec = nixfile.create_section('odML document', 'odML document', oid=odmldoc.id)
    info["sections written"] += 1
    if odmldoc.author:
        nixsec.create_property('odML author', [odmldoc.author])
    if odmldoc.date:
        nixsec.create_property('odML date', [convert_datetime(odmldoc.date)])
    if odmldoc.version:
        nixsec.create_property('odML version', [odmldoc.version])
    if odmldoc.repository:
        nixsec.create_property('odML repository', [odmldoc.repository])
    return nixsec


def nixwrite(odml_doc, filename, mode='append'):
    filemode = None
    if mode == 'append' or mode == 'overwrite metadata':
        filemode = nix.FileMode.ReadWrite
    elif mode == 'overwrite':
        filemode = nix.FileMode.Overwrite
    nixfile = nix.File.open(filename, filemode)

    if mode == 'overwrite metadata':
        if 'odML document' in nixfile.sections:
            del nixfile.sections['odML document']

    nix_document_section = write_odml_doc(odml_doc, nixfile)
    odml_to_nix_recurse(odml_doc.sections, nix_document_section)


############### NIX -> ODML #################

def odmlwrite(nix_file, filename):
    odml_doc, nix_section = get_odml_doc(nix_file)
    nix_to_odml_recurse(nix_section.sections, odml_doc)
    odml.save(odml_doc, filename)


def get_odml_doc(nix_file):
    # identify odml document section in nix file
    try:
        doc_section = nix_file.sections['odML document']
    except ValueError:
        raise ValueError('No odML document section present in nix file.')

    # generate odml document
    attributes = ['author', 'version', 'repository', 'date']
    doc_attributes = {attr: doc_section.props['odML {}'.format(attr)].values[0] for attr in
                      attributes if 'odML {}'.format(attr) in doc_section.props}
    doc_attributes['oid'] = doc_section.id

    return odml.Document(**doc_attributes), doc_section


def nix_to_odml_recurse(nix_section_list, odml_section):
    for nix_sec in nix_section_list:
        info["sections read"] += 1

        # extract and convert section attributes from nix
        # TODO: add 'include' here as soon as available in nix
        attributes = ['name', 'type', 'definition', 'reference', 'repository', 'link', 'id']
        nix_attributes = {attr: getattr(nix_sec, attr) for attr in attributes if
                          hasattr(nix_sec, attr)}
        nix_attributes['parent'] = odml_section
        if 'id' in nix_attributes:
            nix_attributes['oid'] = nix_attributes.pop('id')

        odml_sec = odml.Section(**nix_attributes)
        info["sections written"] += 1
        for nixprop in nix_sec.props:
            info["properties read"] += 1

            # extract and convert property attributes from nix
            prop_attributes = ['name', 'values', 'unit', 'uncertainty', 'reference', 'definition',
                               'dependency', 'dependency_value', 'odml_type', 'value_origin', 'id']
            nix_prop_attributes = {attr: getattr(nixprop, attr) for attr in prop_attributes if
                                   hasattr(nixprop, attr)}

            if 'id' in nix_prop_attributes:
                nix_prop_attributes['oid'] = nix_prop_attributes.pop('id')
            if 'odml_type' in nix_prop_attributes:
                nix_prop_attributes['dtype'] = nix_prop_attributes.pop('odml_type').value
            nix_prop_attributes['parent'] = odml_sec
            nix_prop_attributes['value'] = list(nix_prop_attributes.pop('values'))

            odml.Property(**nix_prop_attributes)
            info["properties written"] += 1

        nix_to_odml_recurse(nix_sec.sections, odml_sec)


def convert(filename, mode='append'):
    # Determine input and output format
    file_base, file_ext = os.path.splitext(filename)
    if file_ext in ['.xml', '.odml']:
        output_format = '.nix'
    elif file_ext in ['.nix']:
        output_format = '.xml'
    else:
        raise ValueError('Unknown file format {}'.format(file_ext))

    # odML files can not be appended but only be overwritten
    if mode != 'overwrite' and output_format in ['.xml', '.odml']:
        mode = 'overwrite'

    # Check output file
    outfilename = file_base + output_format
    if os.path.exists(outfilename):
        yesno = input("File {} already exists. "
                      "{} (y/n)? ".format(outfilename, mode.title()))
        if yesno.lower() not in ("y", "yes"):
            print("Aborted")
            return

    # Load, convert and save to new format
    print("Saving to {} file... ".format(output_format))
    if output_format in ['.nix']:
        try:
            odml_doc = odml.load(filename)
        except InvalidVersionException:
            yesno = input("odML file format version is outdated. Automatically convert "
                          "{} to the latest version (y/n)? ".format(outfilename,
                                                                   mode.title()))
            if yesno.lower() not in ("y", "yes"):
                print("  Use the odml.tools.VersionConverter to convert "
                      "to the latest odML file version.")
                print("  Aborted")
                return

            xml_string = VersionConverter(filename).convert()
            odml_doc = ODMLReader().from_string(xml_string)

        nixwrite(odml_doc, outfilename, mode=mode)

    elif output_format in ['.xml', '.odml']:
        nix_file = nix.File.open(filename, nix.FileMode.ReadOnly)
        odmlwrite(nix_file, outfilename)
    else:
        raise ValueError('Unknown file format {}'.format(output_format))

    print("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Converts odML to NIX file or extracts odML from NIX file,'
                                                 ' also upgrades odML to newest version.')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='NIX or odML file')
    args = parser.parse_args()
    print(args.files)
    for f in args.files:
        convert(f)
    print_info()
