from eggit.api_response import JsonResult


def test_json_result():
    result = JsonResult('test msg', True, 'some data', 100000).get_dict()

    assert result['msg'] == 'test msg'
    assert result['status']
    assert result['data'] == 'some data'
    assert result['error_code'] == 100000
