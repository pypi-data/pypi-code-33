from core.msg.IMqttDeliveryMessage import IMqttDeliveryMessage
from core.msg.IMqttAck import IMqttAck

from abc import ABCMeta

class IMqttReply(IMqttDeliveryMessage, IMqttAck):
	__metaclass__ = ABCMeta

	pass