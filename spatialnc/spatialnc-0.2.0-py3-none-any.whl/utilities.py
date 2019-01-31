
def strip_chars(edit_str, bad_chars='[(){}<>,"_]=\nns'):
    """
    Written to strip out unwanted chars from the proj strings received
    back from the URL for the EPSG requests.

    Args:
        edit_str: String containing unwanted chars
        bad_chars: String of chars to be removed

    Returns:
        result: The edit_str without any of the chars in bad_chars
    """

    result = ''.join([s for s in edit_str if s not in bad_chars])
    return result
