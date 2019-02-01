""" Demonstrates IxNetwork API server session configuration options on a linux platform
"""

from ixnetwork_restpy.testplatform.testplatform import TestPlatform
from ixnetwork_restpy.files import Files
from ixnetwork_restpy.assistants.statistics.statviewassistant import StatViewAssistant


test_platform=TestPlatform('10.36.78.216', platform='linux', log_file_name='./system_test.log')
sessions = None

try:
    test_platform.Trace = 'none'
    test_platform.Authenticate('admin', 'admin')

    test_platform.info('add a session')
    sessions = test_platform.Sessions.add()
    test_platform.info(sessions)

    ixnetwork = sessions.Ixnetwork
    ixnetwork.info('load a configuration file')
    ixnetwork.LoadConfig(Files('C:/Users/anbalogh/AppData/Local/Ixia/sdmStreamManager/common/statistics.ixncfg', local_file=True))

    test_ports = [
        dict(Arg1='10.36.78.216', Arg2=7, Arg3=15),
        dict(Arg1='10.36.78.216', Arg2=7, Arg3=16)
    ]
    unconnected_ports = ixnetwork.AssignPorts(test_ports, [], ixnetwork.Vport.find(), True) 
    port_statistics = StatViewAssistant(ixnetwork, 'Port Statistics')
    ixnetwork.info(port_statistics)

    ixnetwork.info('start all protocols')
    ixnetwork.StartAllProtocols(Arg1='sync')

    ixnetwork.info('check that all protocols are up')
    protocols_summary = StatViewAssistant(ixnetwork, 'Protocols Summary')
    protocols_summary.CheckCondition('Sessions Not Started', StatViewAssistant.EQUAL, 0)
    protocols_summary.CheckCondition('Sessions Down', StatViewAssistant.EQUAL, 0)
    ixnetwork.info(protocols_summary)

    ixnetwork.info('start all traffic')
    ixnetwork.Traffic.Apply()
    ixnetwork.Traffic.Start()

    ixnetwork.info('check that traffic is started')
    traffic_item_statistics = StatViewAssistant(ixnetwork, 'Traffic Item Statistics')
    ixnetwork.info(traffic_item_statistics)

except Exception as e:
    test_platform.info(e)

if sessions is not None:
    sessions.info('remove session')
    sessions.remove()
