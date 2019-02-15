# coding=utf-8


import time
import json
from airtest_hunter import AirtestHunter, open_platform, Hunter
from poco.drivers.netease.internal import NeteasePoco

from pocounit.case import PocoTestCase
from airtest.core.api import connect_device, device as current_device
from poco.drivers.android.uiautomation import AndroidUiautomationPoco


class Case(PocoTestCase):
    @classmethod
    def setUpClass(cls):
        super(Case, cls).setUpClass()
        if not current_device():
            connect_device('Android:///')

    def runTest(self):
        from poco.drivers.cocosjs import CocosJsPoco
        poco = CocosJsPoco()
        for n in poco():
            print(n.get_name())


# if __name__ == '__main__':
#     import pocounit
#     pocounit.main()


# from hunter_cli import Hunter, open_platform
# from poco.drivers.netease.internal import NeteasePoco
#
# tokenid = open_platform.get_api_token('test')
# hunter = Hunter(tokenid, 'xy2', 'xy2_at_408d5c116536')
# poco = NeteasePoco('xy2', hunter)
#
# print poco('npc_conversation').offspring('list_options').offspring('Widget')[0].offspring('txt_content').nodes[0].node.data

from airtest.core.api import connect_device
from poco.utils.track import track_sampling, MotionTrack, MotionTrackBatch
from poco.utils.airtest.input import AirtestInput
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from poco.drivers.cocosjs import CocosJsPoco
from poco.drivers.unity3d import UnityPoco
from poco.drivers.unity3d.device import UnityEditorWindow
from poco.utils.device import VirtualDevice

# tokenid = open_platform.get_api_token('g18_new')
# hunter = Hunter(tokenid, 'g18_new', 'g18_new_at_af291ad0a0e1584b', apihost='hunter-dev.io.netease.com')
# connect_device('Android:///')
# poco = NeteasePoco('y1')
poco = AndroidUiautomationPoco()
# poco2 = poco.freeze()
ui = poco('android.widget.LinearLayout').parent()
print(ui.get_bounds())
# ui2 = ui.child('天气')
# print(ui2.get_bounds())


# print(ui.exists())
# print(ui.get_bounds())

# poco = AndroidUiautomationPoco(use_airtest_input=True)
# for ui in poco():
#     print(ui.get_name())
# poco.ime.text('test')

# meb = MotionTrackBatch([mt1, mt])
# for e in meb.discretize():
#     print e
# print len(meb.discretize())
# poco.apply_motion_tracks([mt1, mt])

time.sleep(4)

