from cmd import Cmd
import cmd
import shlex
import datetime
import threading
from hippodamia.enums import StatType
import pprint
from hippodamia.getch import getch
from hippodamia.enums import ViewDetails


def _parse(arg):
    return tuple(map(str, shlex.split(arg)))


def more(text):
    _MAX_LINES = 35
    TEXT = "   --- Press ENTER to continue / ESC to abort ---"
    max_lines = _MAX_LINES
    lines = text.split("\n")
    i = 0
    for line in lines:
        print(line)
        i += 1
        if i == max_lines:
            i = 0
            print(TEXT, end='\r')
            while True:
                ch = getch()
                if ord(ch) == 27:
                    print(" " * len(TEXT), end='\r')
                    return  # ESC
                elif ord(ch) == 32:
                    max_lines = 1  # SPACE - single line feed
                    break
                elif ord(ch) == 13:
                    max_lines = _MAX_LINES  # ENTER - feed max lines
                    break
            print(" " * len(TEXT), end='\r')


class UI(Cmd):
    intro = None
    prompt = None

    _logger = None
    _shadows = None
    _hierarchical_view = None
    _request_ping = None
    _request_runtime = None
    _request_config = None
    _request_reonboarding = None
    _request_end = None
    _stop_service = None
    _heartbeat = None
    _onboarding = None
    _config = None

    _main_thread = None

    def __init__(self, version, config, shadows, heartbeat, health_view, onboarding, request_ping, request_runtime,
                 request_config, request_reonboarding, request_end, stop_service, logger):
        self.intro = "Hippodamia - Monitoring Service {}.   Type help or ? to list commands.\n".format(version)
        self.prompt = '(monitor) '

        Cmd.__init__(self)

        self._shadows = shadows
        self._config = config
        self._hierarchical_view = health_view
        self._request_ping = request_ping
        self._request_runtime = request_runtime
        self._request_config = request_config
        self._request_reonboarding = request_reonboarding
        self._request_end = request_end
        self._stop_service = stop_service
        self._logger = logger
        self._heartbeat = heartbeat
        self._onboarding = onboarding

        self._main_thread = threading.Thread(target=self._wrapper)

    def start(self):
        self._main_thread.start()

    def stop(self):
        self._main_thread.join()

    def _wrapper(self):
        self.cmdloop()
        stop_daemon = threading.Thread(target=self._stop_service)
        stop_daemon.daemon = True
        stop_daemon.start()

    def _check_gid(self, gid):
        if gid not in self._shadows:
            raise KeyError("gid {} not in {}".format(gid, self._shadows.keys()))
        return gid

    def _request_extract_gid(self, name, arg):
        args = _parse(arg)

        gid = None
        if len(args) == 1 and str(args[0]).lower() == "all":
            print("Sending {} request to all monitored services\n".format(name))
        elif len(args) == 2 and str(args[0]).lower() == "gid":
            gid = self._check_gid(args[1])
            print("Send {} regest to monitoring service with gid == {}\n".format(name, gid))
        else:
            raise ValueError("Wrong arguments: {}. expected '{} [all|gid gid]'.\n".format(args, name))

        return gid

    def do_exit(self, arg):
        """exit - stops the monitoring service: EXIT"""
        return True

    def do_request_ping(self, arg):
        """request_ping [all|gid gid] - publish ping request either to all monitored services or to a specific one: REQUEST_PING GID 1"""
        try:
            self._request_ping(self._request_extract_gid("ping", arg))
        except (KeyError, ValueError) as e:
            print("{}\n".format(e))

    def do_request_runtime(self, arg):
        """request_runtime [all|gid gid] - publish runtime request either to all monitored services or to a specific one: REQUEST_RUNTIME GID 1"""
        try:
            self._request_runtime(self._request_extract_gid("runtime", arg))
        except (KeyError, ValueError) as e:
            print("{}\n".format(e))
            
    def do_request_config(self, arg):
        """request_config [all|gid gid] - publish config request either to all monitored services or to a specific one: REQUEST_CONFIG GID 1"""
        try:
            self._request_config(self._request_extract_gid("config", arg))
        except (KeyError, ValueError) as e:
            print("{}\n".format(e))
            
    def do_request_reonboarding(self, arg):
        """request_reonboarding [all|gid gid] - publish reonboarding request either to all monitored services or to a specific one: REQUEST_REONBOARDING GID 1"""
        try:
            self._request_reonboarding(self._request_extract_gid("reonboarding", arg))
        except (KeyError, ValueError) as e:
            print("{}\n".format(e))
            
    def do_request_end(self, arg):
        """request_end [all|gid gid] - publish end request either to all monitored services or to a specific one: REQUEST_END GID 1"""
        try:
            self._request_end(self._request_extract_gid("end", arg))
        except (KeyError, ValueError) as e:
            print("{}\n".format(e))

    def do_list(self, arg):
        """list - list all known services: LIST"""
        m = ""
        for gid, shadow in self._shadows.items():
            m += "gid: {}, state: {}, health:{}, necessity: {}, name: {}\n"\
                .format(gid, shadow.get_state_id().name, shadow.properties.health.name,
                        shadow.properties.necessity.name, shadow.properties.name)
        more(m)

    def do_hierarchical(self, arg):
        """hierarchical [location location|room room|device device|service service]*
 - show all monitored services: HIERARCHICAL
 - show one location: HIERARCHICAL LOCATION Flat
 - show one specific service: HIERARCHICAL LOCATION Flat ROOM \"Living Room\" DEVICE Thermostat SERVICE \"Thermostat GUI\"
 - show all service that run on devices with the name 'Thermostat': HIERARCHICAL DEVICE Thermostat"""
        arguments = _parse(arg)
        if len(arguments) % 2 == 1:
            print("wrong number of arguments ({})".format(len(arguments)))
            return
        elif len(arguments) == 0:
            m = self._hierarchical_view.pformat(details=ViewDetails.FULL)
        else:
            filters = {"LOCATION": "", "ROOM": "", "DEVICE": "", "SERVICE": ""}
            pos = 0
            while pos < len(arguments):
                first = arguments[pos].upper()
                second = arguments[pos+1]
                if first in filters:
                    filters[first] = second
                else:
                    print("don't know a parameter/filter named '{}'".format(first))
                    return
                pos += 2
            m = self._hierarchical_view.pformat(details=ViewDetails.FULL, filters=filters)
        more(m)

    def do_agentstats(self, arg):
        """agentstats gid gid [all|general|properties|ping|runtime|config|request|logger]
        show information on one specific monitored service: AGENTSTATS GID 1 PROPERTIES"""

        args = _parse(arg)
        if len(args) != 3:
            print("wrong number of arguments: {}\n".format(args))
        elif str(args[0]).lower() != "gid":
            print("first argument ({}) must be 'gid'\n".format(str(args[0]).lower()))
        elif str(args[2]).upper() not in StatType.get_members():
            print("third argument ({}) must be one of {}\n".format(str(args[2]).lower(), StatType.get_members()))
        else:
            try:
                stat_type = StatType.get_enum(str(args[2]))
                gid = self._check_gid(args[1])
                self._print_stats(gid, stat_type)
            except (ValueError, KeyError) as e:
                print("{}\n".format(e))

    def _print_stats(self, gid, type):
        print("stats {} for gid {}:\n".format(type, gid))

        shadow = self._shadows[gid]
        output = ""

        if type == StatType.GENERAL or type == StatType.ALL:
            output += "general: \n"
            output += " - active_state:\n"
            output += "   - name: {}\n".format(shadow.get_state_id().name)
            since = shadow.states[shadow.get_state_id()].timestamp_on_entry
            output += "   - since: {}\n".format(since)
            try:
                output += "   - duration: {}\n".format(datetime.datetime.now()-since)
            except TypeError:
                pass  # since is of type None
            output += " - machine state states: \n"
            for id, state in shadow.states.items():
                try:
                    duration = state.timestamp_on_exit - state.timestamp_on_entry
                except TypeError:
                    try:
                        duration = datetime.datetime.now() - state.timestamp_on_entry
                    except TypeError:
                        duration = "-"

                output += "   - {}: on_entry {} @{}, on_exit {} @{}, duration {}\n"\
                    .format(id.name, state.counter_on_entry, state.timestamp_on_entry,
                            state.counter_on_exit, state.timestamp_on_exit, duration)
            output += " - message stats: \n"
            for id, counter in shadow.shadow_data.get_counter_dict().items():
                output += "   - {}: {}\n".format(id, counter)
            output += " - topics: \n"
            for id, topic in shadow.activity_topics.items():
                output += "   - {}: {}\n".format(id, topic)
            output += " - timings: \n"
            for id, timing in shadow.timings.items():
                output += "   - {}: {}\n".format(id, timing)

        if type == StatType.PROPERTIES or type == StatType.ALL:
            output += "properties: @{}\n".format(shadow.shadow_data.properties_time)
            output += pprint.pformat(shadow.shadow_data.properties, indent=4)
            output += "\n"

        if type == StatType.PING or type == StatType.ALL:
            output += "ping: #{} @{}\n".format(shadow.shadow_data.ping_counter, shadow.shadow_data.ping_time)
            output += pprint.pformat(shadow.shadow_data.ping, indent=4)
            output += "\n"

        if type == StatType.RUNTIME or type == StatType.ALL:
            output += "runtime: #{} @{}\n".format(shadow.shadow_data.runtime_counter, shadow.shadow_data.runtime_time)
            output += pprint.pformat(shadow.shadow_data.runtime, indent=4)
            output += "\n"

        if type == StatType.CONFIG or type == StatType.ALL:
            output += "config: #{} @{}\n".format(shadow.shadow_data.config_counter, shadow.shadow_data.config_time)
            output += pprint.pformat(shadow.shadow_data.config, indent=4)
            output += "\n"

        if type == StatType.REQUEST or type == StatType.ALL:
            output += "request: #{} @{}\n".format(shadow.shadow_data.request_counter, shadow.shadow_data.request_time)
            output += pprint.pformat(shadow.shadow_data.request, indent=4)
            output += "\n"

        if type == StatType.LOGGER or type == StatType.ALL:
            if len(shadow.shadow_data.logger) > 0:
                output += "logger: #{} @{}\n".format(shadow.shadow_data.logger_counter, shadow.shadow_data.logger_time)
                output += pprint.pformat(shadow.shadow_data.logger[-1], indent=4)
                output += "\n"
            else:
                output += "logger: ''\n"

        if output == "":
            print("UI._print_stats: unknown stat type '{}'\n".format(type))
        else:
            more(output)

    def do_agentlog(self, arg):
        """agentlog gid gid - view all received log-entries of this service: AGENTLOG GID 1"""

        args = _parse(arg)
        if len(args) != 2:
            print("wrong number of arguments: {}\n".format(args))
        elif str(args[0]).lower() != "gid":
            print("first argument ({}) must be 'gid'\n".format(str(args[0]).lower()))
        else:
            gid = self._check_gid(args[1])
            shadow = self._shadows[gid]
            print("show log for gid: {}\n".format(gid))

            output = "received: {}, stored: {}\n".format(shadow.shadow_data.logger_counter,
                                                         len(shadow.shadow_data.logger))
            counter = shadow.shadow_data.logger_counter
            for l in shadow.shadow_data.logger:
                output += "{}: {}\n".format(counter, pprint.pformat(l, indent=4))
                counter -= 1
            if counter > 0:
                output += "-- skipping {} removed log-entries".format(counter)
            more(output)

    def do_heartbeatstats(self, arg):
        """heartbeatstats - stats on the heartbeat signal of the monitoring agent: HEARTBEATSTATS"""
        output = "heartbeat: \n"
        output += " - counter: {}\n".format(self._heartbeat.counter)
        output += " - last timestamp: {}\n".format(self._heartbeat.last_timestamp)
        output += " - interval: {} s\n".format(self._heartbeat.interval)
        output += " - topic: {}\n".format(self._heartbeat.topic)
        more(output)

    def do_onboardingstats(self, arg):
        """onboardingstats - stats on the overall onboarding process: ONBOARDINGSTATS"""
        output = "onboarding: \n"
        output += " - counter: {}\n".format(self._onboarding.counter)
        output += " - gid_list: {}\n".format(self._onboarding.gid_list)
        output += " - enforcement: {}\n".format(self._onboarding.enforcement.name)
        output += " - protocol_version: {}\n".format(self._onboarding.protocol_version)
        output += " - topic_onboarding_request: {}\n".format(self._onboarding.topic_onboarding_request)
        output += " - last_timestamp: {}\n".format(self._onboarding.last_timestamp)
        output += " - last_message: \n"
        output += pprint.pformat(self._onboarding.last_message, indent=4)
        more(output)

    def do_config(self, arg):
        """config - show the current config: CONFIG"""
        output = pprint.pformat(self._config, indent=2)
        more(output)

    def do_a(self, arg):
        # """shortcut for 'stats gid 1 all'"""
        self._print_stats("1", StatType.ALL)

    def do_g(self, arg):
        # """shortcut for 'stats gid 1 general'"""
        self._print_stats("1", StatType.GENERAL)

    def do_e(self, arg):
        # """shortcut for 'exit'"""
        return True

    def do_q(self, arg):
        # """shortcut for 'exit'"""
        return True

    def do_h(self, arg):
        # """shortcut for 'hierarchical'"""
        self.do_hierarchical(arg)

    def do_l(self, arg):
        # """shortcut for 'list'"""
        self.do_list(arg)

    def do_o(self, arg):
        # """ shortcut for 'onboardingstats'"""
        self.do_onboardingstats(arg)
