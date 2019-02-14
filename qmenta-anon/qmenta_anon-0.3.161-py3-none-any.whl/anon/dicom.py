import logging

import pydicom


def PatchedMultiString(val, valtype=str):
    """
        Split a bytestring by delimiters if there are any
        val -- DICOM bytestring to split up
        valtype -- default str, but can be e.g. UID to overwrite to a specific type
    """
    # Remove trailing blank used to pad to even length
    # 2005.05.25: also check for trailing 0, error made in PET files we are converting

    if val and (val.endswith(' ') or val.endswith('\x00')):
        val = val[:-1]
    splitup = val.split("\\")
    if len(splitup) == 1:
        try:
            val = splitup[0]
            return valtype(val) if val else val
        except ValueError:
            if valtype is str or valtype is pydicom.valuerep.PersonName or valtype is pydicom.uid.UID:
                return valtype("XXXX") if val else val
            elif valtype is pydicom.valuerep.DSfloat:
                return valtype(0.0) if val else val
    else:
        return pydicom.multival.MultiValue(valtype, splitup)


# overwriting an existing method in order to prevent exceptions when
# tags annonymized with data of other type (e.g. float tag gets string)
pydicom.valuerep.MultiString = PatchedMultiString

# Basic Application Level Confidentiality Profile Attributes
# ftp://medical.nema.org/medical/dicom/final/sup55_ft.pdf

# The last two values for each element indicate the anonymisation type
# where the values have the following meanings:
# - 'X': Remove tag
# - 'Z': Replace with a zero length value, or a non-zero length value that
#       may be a dummy value and consistent with the Value Representations
# - 'D': Replace with a non-zero length value that may be a dummy value and
#       consistent with the Value Representations
# - 'A': Display exact age if <=89 years, and set to blank if >89 years


DICOM_ANON_MIN_SUPP_55 = [
    ("PatientName", (0x0010, 0x0010), "Z"),
    ("PatientID", (0x0010, 0x0020), "Z"),
    ("IssuerOfPatientID", (0x0010, 0x0021), "X"),
    ("PatientBirthTime", (0x0010, 0x0032), "X"),
    ("PatientSex", (0x0010, 0x0040), "Z"),
    ("PatientBirthName", (0x0010, 0x1005), "X"),
    ("CountryOfResidence", (0x0010, 0x2150), "X"),
    ("RegionOfResidence", (0x0010, 0x2152), "X"),
    ("PatientTelephoneNumbers", (0x0010, 0x2154), "X"),
    ("CurrentPatientLocation", (0x0038, 0x0300), "X"),
    ("PatientInstitutionResidence", (0x0038, 0x0400), "X"),
    ("StudyDate", (0x0008, 0x0020), "Z"),
    ("SeriesDate", (0x0008, 0x0021), "X"),
    ("AcquisitionDate", (0x0008, 0x0022), "X"),
    ("ContentDate", (0x0008, 0x0023), "Z"),
    ("OverlayDate", (0x0008, 0x0024), "X"),
    ("CurveDate", (0x0008, 0x0024), "X"),
    ("AcquisitionDateTime", (0x0008, 0x002A), "X"),
    ("StudyTime", (0x0008, 0x0030), "Z"),
    ("SeriesTime", (0x0008, 0x0031), "X"),
    ("AcquisitionTime", (0x0008, 0x0032), "X"),
    ("ContentTime", (0x0008, 0x0033), "Z"),
    ("OverlayTime", (0x0008, 0x0034), "X"),
    ("CurveTime", (0x0008, 0x0035), "X"),
    ("InstitutionAddress", (0x0008, 0x0081), "X"),
    ("ReferringPhysicianName", (0x0008, 0x0090), "Z"),
    ("ReferringPhysicianAddress", (0x0008, 0x0092), "X"),
    ("ReferringPhysicianTelephoneNumber", (0x0008, 0x0094), "X"),
    ("InstitutionalDepartmentName", (0x0008, 0x1040), "X"),
    ("OperatorsName", (0x0008, 0x1070), "X"),
    ("StudyID", (0x0020, 0x0010), "Z"),
    ("DateTime", (0x0040, 0xA120), "X"),
    ("Date", (0x0040, 0xA121), "X"),
    ("Time", (0x0040, 0xA122), "X"),
    ("PersonName", (0x0040, 0xA123), "D"),
    ("AccessionNumber", (0x0008, 0x0050), "Z"),
    ("InstitutionName", (0x0008, 0x0080), "X"),
    ("ReferringPhysicianIDSequence", (0x0008, 0x0096), "X"),
    ("PhysiciansOfRecord", (0x0008, 0x1048), "X"),
    ("PhysiciansOfRecordIDSequence", (0x0008, 0x1049), "X"),
    ("PerformingPhysicianName", (0x0008, 0x1050), "X"),
    ("PerformingPhysicianIDSequence", (0x0008, 0x1052), "X"),
    ("NameOfPhysicianReadingStudy", (0x0008, 0x1060), "X"),
    ("PhysicianReadingStudyIDSequence", (0x0008, 0x1062), "X"),
    ("PatientBirthDate", (0x0010, 0x0030), "Z"),
    ("PatientInsurancePlanCodeSequence", (0x0010, 0x0050), "X"),
    ("PatientPrimaryLanguageCodeSeq", (0x0010, 0x0101), "X"),
    ("OtherPatientIDs", (0x0010, 0x1000), "X"),
    ("OtherPatientNames", (0x0010, 0x1001), "X"),
    ("OtherPatientIDsSequence", (0x0010, 0x1002), "X"),
    ("PatientAge", (0x0010, 0x1010), "X"),
    ("PatientAddress", (0x0010, 0x1040), "X"),
    ("PatientMotherBirthName", (0x0010, 0x1060), "X")
]


def isstr(s):
    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)


def redact_dicom_attr(header, tag):
    value = header[tag].value
    if isstr(value):
        header[tag].value = "XXXX"
    elif isinstance(value, pydicom.valuerep.PersonName) or isinstance(value, pydicom.valuerep.PersonName3):
        header[tag].value = "XXXX"
    elif isinstance(value, pydicom.valuerep.DSfloat):
        header[tag].value = 0.0
    elif isinstance(value, pydicom.uid.UID):
        header[tag].value = "XXXX"
    else:
        raise RuntimeError('Unknown type {} for tag {}'.format(type(value), tag))


def check_tag(header, tag):
    try:
        header[tag].value
        return True
    except (NotImplementedError, Exception):
        return False


def anonymise_dicom_dataset(dcm):

    anonym_action = 2  # Only strong anonymization

    logger = logging.getLogger(__name__)
    node_queue = [dcm]
    while node_queue:
        header = node_queue.pop(0)

        # anonymisation
        for tag in DICOM_ANON_MIN_SUPP_55:
            if (tag[anonym_action] != "") and check_tag(header, tag[1]):

                if tag[anonym_action] in ["Z", "D"]:
                    redact_dicom_attr(header, tag[1])
                elif tag[anonym_action] == "X":
                    try:
                        del header[tag[1]]
                    except Exception:
                        delattr(header, tag[0])

        # tail recursion
        for key in header.keys():
            if check_tag(header, key):
                elem = header[key]
                if isinstance(elem.value, pydicom.sequence.Sequence):
                    node_queue.extend(elem.value)
            else:
                template = "deleting key {!r} with invalid data from header when anonymising dicom file"
                logger.warning(template.format(key))
                try:
                    del header[key]
                except Exception:
                    delattr(header, key)


def anonymise(filename):
    header = pydicom.read_file(filename)

    anonymise_dicom_dataset(header)

    for element in [2, 3, 0x10, 0x12]:
        if not check_tag(header, (2, element)):
            if element == 0x12:
                header.file_meta.ImplementationClassUID = "1.2.3.4"
            elif element == 2:
                header.file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
            elif element == 3:
                header.file_meta.MediaStorageSOPInstanceUID = "1.2.3"

    header.save_as(filename)
    return {"OK": True, "error_tags": []}


def check_anonymised_file(input_file, options={}):
    _options = {
        "return_lines": False,
        "not_found_as_error": False
    }

    _options.update(options)

    lines = []
    not_anonymised_attr = []

    try:
        hd = pydicom.read_file(input_file)
        n_errors = 0
        for tag in DICOM_ANON_MIN_SUPP_55:
            if check_tag(hd, tag[1]):
                val = hd[tag[1]].value

                if _options["return_lines"]:
                    lines.append((tag[0], str(val)))

                try:
                    if not check_anonym_dicom_attr(hd, tag[1]):
                        not_anonymised_attr.append(tag[0])
                except Exception:
                    pass

            else:
                if _options["return_lines"]:
                    lines.append((tag[0], "!!!"))
                if _options["not_found_as_error"]:
                    n_errors += 1
    except Exception as e:
        return {"OK": False, "error": str(e)}

    ret = {"OK": True,
           "n_errors": n_errors,
           "not_anonymised_attr": not_anonymised_attr}

    if _options["return_lines"]:
        ret["lines"] = lines

    return ret


def check_anonym_dicom_attr(header, tag):
    value = header[tag].value
    if isstr(value):
        return str(header[tag].value) == "XXXX"
    elif isinstance(value, pydicom.valuerep.PersonName):
        return header[tag].value == "XXXX"
    elif isinstance(value, pydicom.valuerep.DSfloat):
        return header[tag].value == 0.0
    elif isinstance(value, pydicom.uid.UID):
        return header[tag].value == "XXXX"

    return True
