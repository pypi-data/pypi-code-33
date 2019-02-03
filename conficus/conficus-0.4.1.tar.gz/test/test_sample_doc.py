import conficus
from datetime import datetime


def test_sample_doc(cfg_pth):
    pth = cfg_pth['sample']
    config = conficus.load(str(pth), inheritance=True)

    assert config['integer'] == 102
    assert config['float'] == 10.12

    assert config['boolean-yes']
    assert not config['boolean-no']
    assert config['boolean-true']
    assert not config['boolean-false']

    assert config['date'] == datetime(2017, 10, 12, 0, 0, 0)
    assert config['time'] == datetime(1900, 1, 1, 10, 12, 9)
    assert config['date-and-time'] == datetime(2017, 10, 12, 10, 12, 9)

    assert config['single-line-list'] == [99, 66, 84, 9, 'bill']
    assert config['multiline-list-no-commas'] == ['Herb', 'Mary', 'John', 'Sarah']
    assert config['multiline-list-with-commas'] == ['Herb', 'Mary', 'John', 'Sarah']
    assert config['single-line-tuple'] == ('Herb', 'Mary', 'John', 'Sarah')
    assert config['multiline-tuple'] == ('Herb', 'Mary', 'John', 'Sarah')

    assert config['string'] == "A wealthy gentleman waved his umbrella."
    assert config['string-multiline'] == "A wealthy gentleman waved his umbrella."
    assert config['string-multiline-preserve-new-lines'] == "A wealthy gentleman...\nwaved his umbrella.\n"
    assert config['string-multiline-preserve-space'] == "A wealthy gentleman...\n    waved his umbrella."

    assert str(config['unix-file-path']) == r'/Users/mgemmill/.vimrc'
    assert str(config['windows-file-path']) == r'C:\Users\mgemmill\_vimrc'

    assert config['email.server'] == 'smtp.server.com'

    assert config['email.notify.to'] == 'notify@home.biz'
    assert config['email.notify.subject'] == 'Notification from Ficus'
    assert config['email.notify.server'] == 'smtp.server.com'

    assert config['email.errors.to'] == 'admin@home.biz'
    assert config['email.errors.subject'] == 'Fatal Error Has Occurred'
    assert config['email.errors.server'] == 'smtp.server.com'
