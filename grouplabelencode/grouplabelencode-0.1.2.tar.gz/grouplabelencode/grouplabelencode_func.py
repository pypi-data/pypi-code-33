
def grouplabelencode_loop(data, mapping, encoding, nacode=None):
    out = list()

    for label in data:

        enc = nacode

        for idx, c in enumerate(mapping):

            j = encoding[idx]

            if isinstance(c, (str, int, float)):
                if label == c:
                    enc = j
                    break
            else:  # list
                if label in c:
                    enc = j
                    break

        out.append(enc)

    return out


def grouplabelencode(data, mapping, nacode=None, nastate=False):
    """Encode data array with grouped labels

    Parameters:
    -----------
    data : list
        array with labels

    mapping : dict, list of list
        the index of each element is used as encoding.
        Each element is a single label (str) or list
        of labels that are mapped to the encoding.

    nacode : integer
        (Default: None) Encoding for unmapped states.

    nastate : bool
        If False (Default) unmatched data labels are encoded as nacode.
        If nastate=True (and nacode=None) then unmatched data labels are
        encoded with the integer nacode=len(mapping).
    """
    # What value is used for missing data?
    if nastate:
        if nacode is None:
            nacode = len(mapping)

    # Process depending on the data type of the data mapping variable
    if isinstance(mapping, list):
        m = mapping
        e = range(len(mapping))
    elif isinstance(mapping, dict):
        m = list(mapping.values())
        e = list(mapping.keys())
    else:
        raise Exception("'data' must be list-of-list or dict.")

    # Loop over 'data' array
    return grouplabelencode_loop(data, m, e, nacode=nacode)
