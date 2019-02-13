from eggit.enums import Sex


def test_enum():
    assert Sex.unknown.value == 0
    assert Sex.male.value == 1
    assert Sex.female.value == 2
    assert Sex.unknown.name == 'unknown'
    assert Sex.male.name == 'male'
    assert Sex.female.name == 'female'
