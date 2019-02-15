from tantamount.machine import Machine
from tantamount.fsm2dot import GetDotNotation

from hippodamia.agentshadow.states.active import Active
from hippodamia.agentshadow.states.inactive import Inactive
from hippodamia.agentshadow.states.onboarding import Onboarding
from hippodamia.agentshadow.states.onboarded import Onboarded
from hippodamia.agentshadow.states.stopped import Stopped
from hippodamia.agentshadow.states.archived import Archived
from hippodamia.agentshadow.states.event_ids import event_ids
from hippodamia.agentshadow.states.state_ids import state_ids

import threading


def create(update_available, timings, set_health, logger):
    logger.info("creating state machine - start")

    logger.debug("creating state machine - creating states")
    states = {
        state_ids.ACTIVE: Active(update_available, set_health, logger),
        state_ids.INACTIVE: Inactive(update_available, set_health, logger),
        state_ids.ONBOARDING: Onboarding(update_available, set_health, logger),
        state_ids.ONBOARDED: Onboarded(update_available, set_health, logger),
        state_ids.STOPPED: Stopped(update_available, set_health, logger),
        state_ids.ARCHIVED: Archived(update_available, set_health, logger),
    }

    machine = Machine()

    logger.debug("creating state machine - adding states")
    machine.addstate(state_ids.ACTIVE, states[state_ids.ACTIVE])
    machine.addstate(state_ids.INACTIVE, states[state_ids.INACTIVE])
    machine.addstate(state_ids.ONBOARDING, states[state_ids.ONBOARDING])
    machine.addstate(state_ids.ONBOARDED, states[state_ids.ONBOARDED])
    machine.addstate(state_ids.STOPPED, states[state_ids.STOPPED])
    machine.addstate(state_ids.ARCHIVED, states[state_ids.ARCHIVED])

    logger.debug("creating state machine - set start states")
    machine.setstartstate(state_ids.STOPPED)

    logger.debug("creating state machine - adding transitions")
    machine.addtransition(state_ids.ONBOARDING, event_ids.TIMEOUT, state_ids.STOPPED)
    machine.addtransition(state_ids.ONBOARDING, event_ids.ONBOARDING_REQUEST, state_ids.ONBOARDING)
    machine.addtransition(state_ids.ONBOARDING, event_ids.ONBOARDING_RESPONSE, state_ids.ONBOARDED)

    machine.addtransition(state_ids.ONBOARDED, event_ids.TIMEOUT, state_ids.STOPPED)
    machine.addtransition(state_ids.ONBOARDED, event_ids.REGULAR_MESSAGE, state_ids.ACTIVE)
    machine.addtransition(state_ids.ONBOARDED, event_ids.ONBOARDING_REQUEST, state_ids.ONBOARDING)

    machine.addtransition(state_ids.ACTIVE, event_ids.REGULAR_MESSAGE, state_ids.ACTIVE)
    machine.addtransition(state_ids.ACTIVE, event_ids.TIMEOUT, state_ids.INACTIVE)
    machine.addtransition(state_ids.ACTIVE, event_ids.ONBOARDING_REQUEST, state_ids.ONBOARDING)
    machine.addtransition(state_ids.ACTIVE, event_ids.OFFBOARDING, state_ids.STOPPED)

    machine.addtransition(state_ids.INACTIVE, event_ids.TIMEOUT, state_ids.STOPPED)
    machine.addtransition(state_ids.INACTIVE, event_ids.ONBOARDING_REQUEST, state_ids.ONBOARDING)
    machine.addtransition(state_ids.INACTIVE, event_ids.OFFBOARDING, state_ids.STOPPED)
    machine.addtransition(state_ids.INACTIVE, event_ids.REGULAR_MESSAGE, state_ids.ACTIVE)

    machine.addtransition(state_ids.STOPPED, event_ids.ONBOARDING_REQUEST, state_ids.ONBOARDING)
    machine.addtransition(state_ids.STOPPED, event_ids.TIMEOUT, state_ids.ARCHIVED)

    machine.addtransition(state_ids.ARCHIVED, event_ids.ONBOARDING_REQUEST, state_ids.ONBOARDING)

    logger.debug("creating state machine - set timeout events")
    machine.addtimeoutevent(state_ids.ONBOARDED, event_ids.TIMEOUT, timings["onboarding_timeout"])
    machine.addtimeoutevent(state_ids.ONBOARDING, event_ids.TIMEOUT, timings["onboarding_timeout"])
    machine.addtimeoutevent(state_ids.ACTIVE, event_ids.TIMEOUT, timings["wait_for_message_timeout"])
    machine.addtimeoutevent(state_ids.INACTIVE, event_ids.TIMEOUT, timings["deactivation_timeout"])
    machine.addtimeoutevent(state_ids.STOPPED, event_ids.TIMEOUT, timings["archivation_timeout"])

    logger.info("creating state machine - done")
    return machine, states


def dot2file(filename):
    class NoLogger:
        def info(self, message):
            pass

        def debug(self, message):
            pass

        def warning(self, message):
            pass

        def error(self, message):
            pass

        def getChild(self, name):
            return self

    logger = NoLogger()
    updateavailable = threading.Event()
    timings = {
        "onboarding_timeout": 60,
        "wait_for_message_timeout": 180,
        "deactivation_timeout": 360,
        "heartbeat_interval": 120,
        "archivation_timeout": 86400
    }
    machine, states = create(updateavailable, timings, None, logger)

    gdn = GetDotNotation(machine, getStateId=(lambda x:x.name), getStateName=(lambda x:x.name),
                         getTransitionName=(lambda x:x.name))
    new_dotnotation = gdn.getdotnotation()

    try:
        with open(filename, 'r') as f:
            old_dotnotation = f.read()
    except OSError:
        old_dotnotation = ""

    if new_dotnotation != old_dotnotation:
        print("updating {} to latest version.".format(filename))
        with open(filename, "w") as f:
            f.write(new_dotnotation)
