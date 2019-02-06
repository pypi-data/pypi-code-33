import second_worker


def test_worker_message():
    assert 'second' in second_worker.get_worker_message().lower()


def test_print_worker_message(capsys):
    second_worker.print_worker_message()
    std_out_capture = capsys.readouterr()
    assert std_out_capture.out != ''
