from cloudcix.client import Client


class Training:
    """
    The Training Application exposes a REST API capable of managing Training records
    """
    _application_name = 'Training'

    cls = Client(
        _application_name,
        'Class/',
    )
    student = Client(
        _application_name,
        'Student/',
    )
    syllabus = Client(
        _application_name,
        'Syllabus/',
    )
