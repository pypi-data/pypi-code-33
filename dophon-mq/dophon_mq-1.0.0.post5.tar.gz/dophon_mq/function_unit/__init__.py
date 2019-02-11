from dophon_mq import properties
from dophon_mq.local import MsgCenter

center = MsgCenter.get_center(remote_center=properties.mq.get('remote_center', False))