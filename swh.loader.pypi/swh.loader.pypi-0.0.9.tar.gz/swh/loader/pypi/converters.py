# Copyright (C) 2018  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information


EMPTY_AUTHOR = {'fullname': b'', 'name': None, 'email': None}


def info(data):
    """Given a dict of a PyPI project information, returns a project
       subset.

    Args:
        data (dict): Representing either artifact information or
                     release information.

    Returns:
        A dict subset of project information.

    """
    _info = data['info']
    default = {
        'home_page': _info['home_page'],
        'description': _info['description'],
        'summary': _info['summary'],
        'license': _info['license'],
        'package_url': _info['package_url'],
        'project_url': _info['project_url'],
        'upstream': None,
    }

    project_urls = _info.get('project_urls')
    if project_urls:
        homepage = project_urls.get('Homepage')
        if homepage:
            default['upstream'] = homepage

    return default


def author(data):
    """Given a dict of project/release artifact information (coming from
       PyPI), returns an author subset.

    Args:
        data (dict): Representing either artifact information or
                     release information.

    Returns:
        swh-model dict representing a person.

    """
    name = data.get('author')
    email = data.get('author_email')

    if email:
        fullname = '%s <%s>' % (name, email)
    else:
        fullname = name

    if not fullname:
        return EMPTY_AUTHOR

    if fullname:
        fullname = fullname.encode('utf-8')

    if name:
        name = name.encode('utf-8')

    if email:
        email = email.encode('utf-8')

    return {'fullname': fullname, 'name': name, 'email': email}
