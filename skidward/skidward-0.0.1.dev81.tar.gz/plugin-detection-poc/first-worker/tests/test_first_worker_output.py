import first_worker


def test_worker_message():
    assert 'first' in first_worker.get_worker_message().lower()


def test_print_worker_message(capsys):
    first_worker.print_worker_message()
    std_out_capture = capsys.readouterr()
    assert std_out_capture.out != ''
