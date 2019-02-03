from opentmi_client import OpenTmiClient, Result

client = OpenTmiClient()

result = Result.from_dict({"tcid": "abc", "execution": {"verdict": "pass"}})
print(result.data)
