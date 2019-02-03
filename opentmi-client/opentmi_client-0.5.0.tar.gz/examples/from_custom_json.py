from opentmi_client import Result


def reducer_func(result_obj, value, key):
    # This function remap key to proper Result API
    if key == "result":
        # custom json has result -key, but right place is result.verdict
        result_obj.verdict = value.lower() # allowed values are lower level "pass"
    elif key == "test.name":
        # this is test case id ("name")
        result_obj.tcid = value
    return result_obj


custom_json = {
    "result": "PASS",
    "test": {
        "name": "hello"
    }
}
result = Result.from_dict(custom_json, reducer=reducer_func)
print(result)
