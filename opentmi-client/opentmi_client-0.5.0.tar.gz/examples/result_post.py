from opentmi_client import OpenTmiClient, Result

client = OpenTmiClient()
result = Result()
result.tcid = "test-case-a"
result.verdict = "pass"
client.post_result(result)
