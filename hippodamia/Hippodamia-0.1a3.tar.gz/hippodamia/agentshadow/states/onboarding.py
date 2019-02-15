from hippodamia.agentshadow.states.amonitoringstate import AMonitoringState
from hippodamia.agentshadow.states.event_ids import event_ids
from hippodamia.enums import Health


class Onboarding(AMonitoringState):
    func_send_onboarding_response = None
    func_deactivate_recv_messages = None
    func_activate_recv_messages = None

    def __init__(self, update_available, set_health, logger):
        AMonitoringState.__init__(self, update_available, set_health, Health.RED, logger, __class__.__name__)

    def _on_entry(self):
        self.func_deactivate_recv_messages()

        return event_ids.ONBOARDING_RESPONSE

    def _on_exit(self):
        self.func_activate_recv_messages()
        self.func_send_onboarding_response()
