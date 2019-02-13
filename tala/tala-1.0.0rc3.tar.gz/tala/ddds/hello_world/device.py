from tala.model.device import DddDevice, DeviceWHQuery, DeviceAction, Validity


class HelloWorldDevice(DddDevice):
    def __init__(self):
        self._hour = 10
        self._minute = 5
        self._ringing = False
        self._alarm_is_set = False

    class current_time(DeviceWHQuery):
        def perform(self):
            time = '"%02d:%02d"' % (self.device._hour, self.device._minute)
            return [time]

    class SetTime(DeviceAction):
        def perform(self, hour, minute):
            self.device._hour = hour
            self.device._minute = minute
            return True

    class SetAlarm(DeviceAction):
        def perform(self, hour, minute):
            self.device._alarm_is_set = True
            return True

    class RemoveAlarm(DeviceAction):
        def perform(self):
            return True

    class AlarmRings(DeviceAction):
        pass

    class Snooze(DeviceAction):
        def perform(self):
            if self.device._ringing:
                return True
            else:
                self.failure_reason = "not_ringing"
                return False

    class TurnOffAlarm(DeviceAction):
        def perform(self):
            return True

    class SelectAlarm(DeviceAction):
        def perform(self, alarm_to_select):
            return True

    class HourValidity(Validity):
        def is_valid(self, hour):
            return hour < 24

    class MinuteValidity(Validity):
        def is_valid(self, minute):
            return minute < 60

    class alarm_image_url(DeviceWHQuery):
        def perform(self):
            if self.device._alarm_is_set:
                return ["http://www.clock.org/mockup_image_alarm_is_set.png"]
            else:
                return ["http://www.clock.org/mockup_image_alarm_is_not_set.png"]

    class clock_view(DeviceWHQuery):
        def perform(self):
            return ["http://mockup_clock_view_url"]
