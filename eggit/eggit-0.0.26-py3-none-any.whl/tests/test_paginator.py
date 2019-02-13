from eggit.paginator import Paginator


def test_paginator():
    page = Paginator(1, 1, None, 0, 5)
    json = page.get_dict()
    assert json['current_page'] == 1
    assert json['total_page_count'] == 1
    assert json['items'] is None
    assert json['total_item_count'] == 0
    assert json['page_size'] == 5
