from tala.model.device import DddDevice, DeviceAction


class RasaAnswersDevice(DddDevice):
    class Navigate(DeviceAction):
        def perform(self, origin, destination):
            return True
