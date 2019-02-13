from tala.model.device import DddDevice, EntityRecognizer, DeviceAction


class PartialParsingDevice(DddDevice):
    class KeywordRecognizer(EntityRecognizer):
        def recognize_entity(self, string):
            if "new york" in string.lower():
                return [{"name": "city_new_york", "sort": "city", "grammar_entry": "new york"}]
            return []

    class StartNavigation(DeviceAction):
        def perform(self):
            return True
