def tiny_int(val):
    # tinyInt SQL evaluation
    return  val >= 0 and val <= 255

def validate_value(val):
    # validating if value is a integer instance
    try:
        return isinstance(int(val), int)
    except ValueError as e:
        return False
