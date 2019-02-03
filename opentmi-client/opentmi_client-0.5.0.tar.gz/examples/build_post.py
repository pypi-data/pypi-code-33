from opentmi_client import OpenTmiClient, Build
from opentmi_client.api.build import Ci, Target, Hardware


client = OpenTmiClient(port=3000)
build = Build()
build.name = "build-1"

ci = Ci()
ci.system = 'Jenkins'
build.ci_tool = ci

target = Target()
hw = Hardware()
hw.model = "K64F"
target.hardware = hw
build.target = target
build.target.operating_system = "win32"

print(build.data)
client.post_build(build)
