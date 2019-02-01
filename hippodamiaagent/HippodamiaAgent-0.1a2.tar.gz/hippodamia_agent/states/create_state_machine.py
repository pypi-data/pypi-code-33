from tantamount.machine import Machine
from hippodamia_agent.states.active import Active
from hippodamia_agent.states.initialized import Initialized
from hippodamia_agent.states.onboarding import Onboarding
from hippodamia_agent.states.onboarded import Onboarded
from hippodamia_agent.states.terminiating import Terminating
from hippodamia_agent.states.uninitialized import Uninitialized
from hippodamia_agent.states.event_ids import event_ids
from hippodamia_agent.states.state_ids import state_ids


def create(sigint, onboarding_timeout, heartbeat_timeout, logger):
    logger.info("creating state machine - start")

    logger.info("creating state machine - creating states")
    states = {
        state_ids.Uninitialized: Uninitialized(logger, sigint),
        state_ids.Initialized: Initialized(logger, sigint),
        state_ids.Onboarding: Onboarding(logger, sigint),
        state_ids.Onboarded: Onboarded(logger, sigint),
        state_ids.Active: Active(logger, sigint),
        state_ids.Terminating: Terminating(logger),
    }

    machine = Machine()

    logger.info("creating state machine - adding states")
    machine.addstate(state_ids.Active, states[state_ids.Active])
    machine.addstate(state_ids.Initialized, states[state_ids.Initialized])
    machine.addstate(state_ids.Onboarding, states[state_ids.Onboarding])
    machine.addstate(state_ids.Onboarded, states[state_ids.Onboarded])
    machine.addstate(state_ids.Terminating, states[state_ids.Terminating])
    machine.addstate(state_ids.Uninitialized, states[state_ids.Uninitialized])

    logger.info("creating state machine - set start states")
    machine.setstartstate(state_ids.Uninitialized)

    logger.info("creating state machine - adding transitions")
    machine.addtransition(state_ids.Uninitialized, event_ids.new_uuid, state_ids.Initialized)
    machine.addtransition(state_ids.Uninitialized, event_ids.sigint, state_ids.Terminating)

    machine.addtransition(state_ids.Initialized, event_ids.sigint, state_ids.Terminating)
    machine.addtransition(state_ids.Initialized, event_ids.onboarding_request, state_ids.Onboarding)

    machine.addtransition(state_ids.Onboarding, event_ids.sigint, state_ids.Terminating)
    machine.addtransition(state_ids.Onboarding, event_ids.timeout, state_ids.Initialized)
    machine.addtransition(state_ids.Onboarding, event_ids.onboarding_response, state_ids.Active)

    machine.addtransition(state_ids.Onboarded, event_ids.sigint, state_ids.Terminating)
    machine.addtransition(state_ids.Onboarded, event_ids.activate, state_ids.Active)

    machine.addtransition(state_ids.Active, event_ids.sigint, state_ids.Terminating)
    machine.addtransition(state_ids.Active, event_ids.reonboarding_request, state_ids.Uninitialized)
    machine.addtransition(state_ids.Active, event_ids.timeout, state_ids.Uninitialized)

    logger.info("creating state machine - set timeout events")
    machine.addtimeoutevent(state_ids.Onboarding, event_ids.timeout, onboarding_timeout)
    machine.addtimeoutevent(state_ids.Active, event_ids.timeout, heartbeat_timeout)

    logger.info("creating state machine - done")
    return machine, states
