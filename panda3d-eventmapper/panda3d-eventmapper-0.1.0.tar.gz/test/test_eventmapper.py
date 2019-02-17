import panda3d.core as p3d


import eventmapper


def test_prc():
    p3d.load_prc_file_data(
        '',
        'event-map-item-jump space raw-y gamepad0-face_a\n'
    )

    emapper = eventmapper.EventMapper()

    assert emapper.get_inputs_for_event('jump') == [
        'space',
        'raw-y',
        'gamepad0-face_a',
    ]
    assert emapper.get_labels_for_event('jump') == [
        'space',
        'y',
    ]

def test_add_alias():
    emapper = eventmapper.EventMapper()

    emapper.add_alias('space', 'jump')
    emapper.add_alias('raw-y', 'jump')
    emapper.add_alias('gamepad0-face_a', 'jump')

    assert emapper.get_inputs_for_event('jump') == [
        'space',
        'raw-y',
        'gamepad0-face_a',
    ]
    assert emapper.get_labels_for_event('jump') == [
        'space',
        'y',
    ]

def test_clear_aliases():
    emapper = eventmapper.EventMapper()

    emapper.add_alias('space', 'jump')

    assert emapper.get_inputs_for_event('jump')

    emapper.clear_aliases()

    assert not emapper.get_inputs_for_event('jump')
