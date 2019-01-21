#!/usr/bin/env python3
"""Classes and methods for working with deterministic pushdown automata."""

import copy

import automata.base.exceptions as exceptions
import automata.pda.exceptions as pda_exceptions
import automata.pda.pda as pda
from automata.pda.configuration import PDAConfiguration
from automata.pda.stack import PDAStack


class DPDA(pda.PDA):
    """A deterministic pushdown automaton."""

    def __init__(self, *, states, input_symbols, stack_symbols,
                 transitions, initial_state,
                 initial_stack_symbol, final_states):
        """Initialize a complete DPDA."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.stack_symbols = stack_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.initial_stack_symbol = initial_stack_symbol
        self.final_states = final_states.copy()
        self.validate()

    def _validate_transition_invalid_symbols(self, start_state, paths):
        """Raise an error if transition symbols are invalid."""
        for input_symbol, symbol_paths in paths.items():
            self._validate_transition_invalid_input_symbols(
                start_state, input_symbol)
            for stack_symbol in symbol_paths:
                self._validate_transition_isolated_lambda_transitions(
                    start_state, input_symbol, stack_symbol)
                self._validate_transition_invalid_stack_symbols(
                    start_state, stack_symbol)

    def _validate_transition_lambda_transition_sibling(self, start_state,
                                                       sib_path):
        """Check the given sibling path for adjacent lambda transitions."""
        for other_stack_symbol in sib_path:
            if (other_stack_symbol in
                    self.transitions[start_state]['']):
                raise pda_exceptions.NondeterminismError(
                    'A symbol transition is adjacent to a '
                    'lambda transition for this DPDA.')

    def _validate_transition_isolated_lambda_transitions(self, start_state,
                                                         input_symbol,
                                                         stack_symbol):
        """Raise an error if a lambda transition has no sibling transitions."""
        if input_symbol == '':
            sib_transitions = self.transitions[start_state]
            for sib_input_symbol, sib_path in sib_transitions.items():
                if sib_input_symbol != '':
                    self._validate_transition_lambda_transition_sibling(
                        start_state, sib_path)

    def _validate_transition_invalid_input_symbols(self, start_state,
                                                   input_symbol):
        """Raise an error if transition input symbols are invalid."""
        if input_symbol not in self.input_symbols and input_symbol != '':
            raise exceptions.InvalidSymbolError(
                'state {} has invalid transition input symbol {}'.format(
                    start_state, input_symbol))

    def _validate_transition_invalid_stack_symbols(self, start_state,
                                                   stack_symbol):
        """Raise an error if transition stack symbols are invalid."""
        if stack_symbol not in self.stack_symbols:
            raise exceptions.InvalidSymbolError(
                'state {} has invalid transition stack symbol {}'.format(
                    start_state, stack_symbol))

    def _validate_initial_stack_symbol(self):
        """Raise an error if initial stack symbol is invalid."""
        if self.initial_stack_symbol not in self.stack_symbols:
            raise exceptions.InvalidSymbolError(
                'initial stack symbol {} is invalid'.format(
                    self.initial_stack_symbol))

    def validate(self):
        """Return True if this DPDA is internally consistent."""
        for start_state, paths in self.transitions.items():
            self._validate_transition_invalid_symbols(start_state, paths)
        self._validate_initial_state()
        self._validate_initial_stack_symbol()
        self._validate_final_states()
        return True

    def _has_lambda_transition(self, state, stack_symbol):
        """Return True if the current config has any lambda transitions."""
        return (state in self.transitions and
                '' in self.transitions[state] and
                stack_symbol in self.transitions[state][''])

    def _get_transition(self, state, input_symbol, stack_symbol):
        """Get the transiton tuple for the given state and symbols."""
        if (state in self.transitions and
                input_symbol in self.transitions[state] and
                stack_symbol in self.transitions[state][input_symbol]):
            return (
                input_symbol,
            ) + self.transitions[state][input_symbol][stack_symbol]

    def _replace_stack_top(self, stack, new_stack_top):
        if new_stack_top == '':
            new_stack = stack.pop()
        else:
            new_stack = stack.replace(new_stack_top)
        return new_stack

    def _has_accepted(self, current_configuration):
        """Check whether the given config indicates accepted input."""
        # If there's input left, we're not finished.
        if current_configuration.remaining_input:
            return False
        # If the stack is empty, we accept.
        if not current_configuration.stack:
            return True
        # If current state is a final state, we accept.
        if current_configuration.state in self.final_states:
            return True
        # Otherwise, not.
        return False

    def _check_for_input_rejection(self, current_configuration):
        """Raise an error if the given config indicates rejected input."""
        if not self._has_accepted(current_configuration):
            raise exceptions.RejectionException(
                'the DPDA stopped in a non-accepting configuration '
                '({state}, {stack})'
                .format(**current_configuration._asdict())
            )

    def _get_next_configuration(self, old_config):
        """Advance to the next configuration."""
        transitions = set()
        if old_config.remaining_input:
            transitions.add(self._get_transition(
                old_config.state,
                old_config.remaining_input[0],
                old_config.stack.top()
            ))
        transitions.add(self._get_transition(
            old_config.state,
            '',
            old_config.stack.top()
        ))
        if None in transitions:
            transitions.remove(None)
        if len(transitions) == 0:
            raise exceptions.RejectionException(
                'The automaton entered a configuration for which no '
                'transition is defined ({}, {}, {})'.format(
                    old_config.state,
                    old_config.remaining_input[0],
                    old_config.stack.top()
                )
            )
        if len(transitions) > 1:
            raise pda_exceptions.NondeterminismError(
                'The automaton entered a configuration for which more'
                'than one transition is defined ({}, {}'.format(
                    old_config.state,
                    old_config.stack.top()
                )
            )
        input_symbol, new_state, new_stack_top = transitions.pop()
        remaining_input = old_config.remaining_input
        if input_symbol:
            remaining_input = remaining_input[1:]
        new_config = PDAConfiguration(
            new_state,
            remaining_input,
            self._replace_stack_top(old_config.stack, new_stack_top)
        )
        return new_config

    def read_input_stepwise(self, input_str):
        """
        Check if the given string is accepted by this DPDA.

        Yield the DPDA's current configuration at each step.
        """
        current_configuration = PDAConfiguration(
            self.initial_state,
            input_str,
            PDAStack([self.initial_stack_symbol])
        )

        yield current_configuration
        while (
            current_configuration.remaining_input
            or self._has_lambda_transition(
                current_configuration.state,
                current_configuration.stack.top()
            )
        ):
            current_configuration = self._get_next_configuration(
                current_configuration
            )
            yield current_configuration
            if self._has_accepted(current_configuration):
                return
        self._check_for_input_rejection(current_configuration)
