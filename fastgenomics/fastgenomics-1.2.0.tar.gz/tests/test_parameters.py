from pytest import raises


def test_checker_true(fgprocess):
    fgprocess.parameters.check("str_value", lambda x: True, "All good!")
    fgprocess.parameters.check("int_value", lambda x: x == 150, "All good!")


def test_cheker_raises(fgprocess):
    with raises(ValueError, match=r".*Failed!"):
        fgprocess.parameters.check("str_value", lambda x: False, "Failed!")

    with raises(ValueError, match=r".*Number of dimensions.*"):
        fgprocess.parameters.check(
            "int_value",
            lambda x: x > 150,
            "Number of dimensions has to be greater then 150",
        )
