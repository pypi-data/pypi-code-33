import re
import unicodedata


def remove_trailing_space(string: str) -> str:
    """
    Remove the trailing space of a string at every line.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str

    **Example:**

    .. code-block:: python

        string = "Hello \\nWorld!"
        result = remove_trailing_space(string) # "Hello\\nWorld!"
    """
    result = re.sub(r"[^\S\n]+$", "", string, flags=re.MULTILINE)
    return re.sub(r"\s+$", "", result)


def remove_leading_space(string: str) -> str:
    """
    Remove the leading space of a string at every line.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str

    **Example:**

    .. code-block:: python

        string = " Hello \\nWorld!"
        result = remove_trailing_space(string) # "Hello \\nWorld!"
    """
    return re.sub(r"^[ \t]*", "", string, flags=re.MULTILINE)


def replace_continuous_newlines(string: str) -> str:
    """
    Replace more than two continuous newline with two newline.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str

    **Example:**

    .. code-block:: python

        string = "Hello\\n\\n\\nWorld!"
        result = replace_continuous_newlines(string) # "Hello\\n\\nWorld!"
    """
    return re.sub(r"\n{3,}", "\n\n", string)


def replace_continuous_space(string: str) -> str:
    """
    Replace more than one continuous space with one space.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str

    **Example:**

    .. code-block:: python

        string = "Hello \t World!"
        result = replace_continuous_space(string) # "Hello World!"
    """
    return re.sub(r"[^\S\n]{2,}", " ", string)


def replace_tilde(string: str) -> str:
    """
    Replace different tilde characters with single kind of tilde character.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str

    **Example:**

    .. code-block:: python

        string = "~Hello World~"
        result = replace_tilde(string) # "〜Hello World〜"
    """
    return re.sub(r"[~˜⁓∼∽∿〜～]", "〜", string)


def replace_dot(string: str) -> str:
    """
    Replace different multiple dot characters with single kind of dot
    character.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str

    **Example:**

    .. code-block:: python

        string = "Hello World..."
        result = replace_dot(string) # "Hello World…"

    .. seealso::

        `Stack Overflow <https://stackoverflow.com/a/51568290/3673259>`_
    """
    string = re.sub(r"([.．、・]{3}(?![.．、・](?:[^.．、・]|$))|[.．、・]{2})",
                    "…", string)
    string = re.sub(r"([。、]{3}(?![。、](?:[^。、]|$))|[。、]{2})", "…", string)
    return string


def replace_full_stop(string: str) -> str:
    """
    Replace full width full stop character with Japanese dot character.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str

    **Example:**

    .. code-block:: python

        string = "Hello．World"
        result = replace_full_stop(string) # "Hello・World"
    """
    return string.replace("．", "・")


def replace_arrow_brackets(string: str) -> str:
    """
    Replace different arrow brackets characters with single kind arrow
    brackets characters.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str

    **Example:**

    .. code-block:: python

        string = "<Hello World>"
        result = replace_arrow_brackets(string) # "〈Hello World〉"
    """
    return re.sub(r"[＜<](.*)[>＞]", r"〈\g<1>〉", string)


def replace_ending_space(string: str) -> str:
    """
    Replace trailing space after some symbol.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str

    **Example:**

    .. code-block:: python

        string = "Hello World? Test"
        result = replace_ending_space(string) # "Hello World?Test"
    """
    return re.sub(r"([?!。])[^\S\n]+", r"\g<1>", string)


def remove_single_linebreak(string: str) -> str:
    """
    Remove single linebreak.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str

    **Example:**

    .. code-block:: python

        string = "Hello\\n\\nWorld?\\nTest"
        result = replace_ending_space(string) # "Hello\\n\\nWorld?Test"
    """
    return re.sub(r"(?<!\n)\n(?!\n)", "", string)


def normalize(string: str) -> str:
    """
    Run ``unicodedata.normalize`` with ``NFKC`` and all other formatting.

    :param string: String to be processed
    :type string: str
    :return: Result string
    :rtype: str
    """
    result = unicodedata.normalize("NFKC", string)
    result = remove_trailing_space(result)
    result = remove_leading_space(result)
    result = replace_continuous_newlines(result)
    result = replace_continuous_space(result)
    result = replace_ending_space(result)
    result = remove_single_linebreak(result)
    result = replace_tilde(result)
    result = replace_dot(result)
    result = replace_arrow_brackets(result)
    result = result.strip()
    return result
