from cashmere import core
from cashmere import backends


def test_argument_cache(tmp_path):

    filepath = tmp_path / "demo"
    cache = backends.MemoryCache()

    @cache.memoize
    def write_into_file(x):
        with open(filepath, "a") as f:
            f.write(x)

    message = "Hello\n"

    # Should write into the file on first invocation.
    write_into_file(message)
    assert filepath.read_text() == message

    # Nothing has changed, so this call should be skipped.
    write_into_file(message)
    assert filepath.read_text() == message

    # Argument has changed, so should write into file.
    second_message = "World\n"
    write_into_file(second_message)
    assert filepath.read_text() == message + second_message


def test_closure_cache(tmp_path):

    filepath = tmp_path / "demo"
    cache = backends.MemoryCache()

    @cache.memoize
    def write_into_file():
        with open(filepath, "a") as f:
            f.write(message)

    message = "Hello\n"

    # Should write into the file on first invocation.
    write_into_file()
    assert filepath.read_text() == message

    # Nothing has changed, so this call should be skipped.
    write_into_file()
    assert filepath.read_text() == message

    # Closure has changed, so should write into file.
    message = "World\n"
    write_into_file()
    assert filepath.read_text() == "Hello\nWorld\n"
