from jolt.xmldom import *
from jolt import filesystem as fs


@Attribute('name')
@Attribute('identity')
class _JoltTask(SubElement):
    def __init__(self, elem=None):
        super(_JoltTask, self).__init__('task', elem=elem)


@Composition(_JoltTask, "task")
class JoltManifest(ElementTree):
    def __init__(self):
        super(JoltManifest, self).__init__(element=Element('jolt-manifest'))

    def append(self, element):
        self.getroot().append(element)

    def get(self, key):
        self.getroot().get(key)

    def set(self, key, value):
        self.getroot().set(key, value)

    def parse(self, filename="default.joltmanifestx"):
        with open(filename) as f:
            data = f.read().replace("\n  ", "")
            data = data.replace("\n", "")
            root = ET.fromstring(data)
            self._setroot(root)
            return self
        raise Exception("failed to parse xml file")

    def format(self):
        return minidom.parseString(ET.tostring(self.getroot())).toprettyxml(indent="  ")

    def write(self, filename):
        with open(filename, 'w') as f:
            f.write(self.format())

    def has_task(self, task):
        return len(self.getroot().findall(".//task[@identity='{}']".format(task.identity))) != 0
