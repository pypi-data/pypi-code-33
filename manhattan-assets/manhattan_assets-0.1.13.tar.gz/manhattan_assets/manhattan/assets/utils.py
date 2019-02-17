from flask import current_app
from .assets import Asset

__all__ = [
    'min_file_projection',
    'min_image_projection'
]


def min_file_projection(field):
    """Return a projection that will select minimal file info"""
    projection = {}
    projection[field] = {
        '$sub': Asset,
        'key': True
    }
    projection['.'.join([field, 'filename'])] = True
    projection['.'.join([field, 'core_meta', 'filename'])] = True
    projection['.'.join([field, 'core_meta', 'length'])] = True

    return projection

def min_image_projection(field, variations):
    """Return a projection that will only select minimal image info"""
    projection = {}
    projection[field] = {
        '$sub': Asset,
        'variations': {'$sub.': Asset}
    }
    projection['.'.join([field, 'filename'])] = True
    projection['.'.join([field, 'core_meta', 'image'])] = True
    projection['.'.join([field, 'core_meta', 'image', 'size'])] = True
    projection['.'.join([field, 'user_meta'])] = True

    for variation in variations:
        variation_path = '.'.join([field, 'variations', variation])
        projection[variation_path] = True
        projection['.'.join([variation_path, 'filename'])] = True

        core_meta_path = '.'.join([variation_path, 'core_meta'])
        projection[core_meta_path] = True
        projection['.'.join([core_meta_path, 'image'])] = True
        projection['.'.join([core_meta_path, 'image', 'size'])] = True
        projection['.'.join([core_meta_path, '__manhattan_fake__'])] = True

        user_meta_path = '.'.join([variation_path, 'user_meta'])
        projection[user_meta_path] = True

    return projection