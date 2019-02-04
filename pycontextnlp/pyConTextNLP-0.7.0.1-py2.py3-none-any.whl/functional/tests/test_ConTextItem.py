import sys

sys.path.append("../")

import ConTextItem 

def test_assign_regex1():
    literal = "pulmonary embolism"
    regex = ""

    assert ConTextItem._assign_regex(literal, regex) ==\
            r"\bpulmonary embolism\b"

def test_assign_regex2():
    literal = "pulmonary embolism"
    regex = "pulmonary\s(artery )?(embol[a-z]+)"

    assert ConTextItem._assign_regex(literal, regex) == \
            r"pulmonary\s(artery )?(embol[a-z]+)"

if __name__ == '__main__':
    test_assign_regex1()
    test_assign_regex2()
