import conficus


def test_inheritence(raw_cfg):
    conficus._inherit(raw_cfg)

    assert raw_cfg['inherited.one'].value == '1'
    assert raw_cfg['inherited.two'].value == '2'
    assert raw_cfg['inherited.three'].value == '3'

    assert raw_cfg['inherited.parent.one'].value == '1'
    assert raw_cfg['inherited.parent.two'].value == '1'
    assert raw_cfg['inherited.parent.three'].value == '2'

    assert raw_cfg['inherited.parent.child.one'].value == '1'
    assert raw_cfg['inherited.parent.child.two'].value == '1'
    assert raw_cfg['inherited.parent.child.three'].value == '1'
