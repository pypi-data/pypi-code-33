import pytest
from src.output_processor import img


@pytest.mark.parametrize('test_input', [
    'happy',
    '행복하다'
    ])
def test_img(test_input):
    rslt_dict = img.get_output_dict(test_input)
    print('Image of ' + test_input + ' : ' +
          rslt_dict['image'].__str__())
    assert rslt_dict['image'] is not None
    print('Link of ' + test_input + ' : ' +
          rslt_dict['link'].__str__())
    assert rslt_dict['link'] is not None
    print('Thumbnail of ' + test_input + ' : ' +
          rslt_dict['thumbnail'].__str__())
    assert rslt_dict['thumbnail'] is not None
