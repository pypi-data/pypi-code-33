from hippodamia.agentshadow.states.amonitoringstate import AMonitoringState
from hippodamia.enums import Health


class Inactive(AMonitoringState):
    def __init__(self, update_available, set_health, logger):
        AMonitoringState.__init__(self, update_available, set_health, Health.YELLOW, logger, __class__.__name__)

    def _on_entry(self):
        return None

    def _on_exit(self):
        pass
