import os
from stepist.tests.test_flows import simple_flow

from stepist.tests import utils


def test_simple_flow():
    text_file_path = os.path.join(utils.get_test_data_path(),
                                  'game_of_thrones.txt')
    result = simple_flow.read_text(file=text_file_path)

    assert result['the'] == 73