import os
import sys
from time import sleep


class UserErrorReporting(object):
    _DESCRIPTION = "description"
    _VALUE = "value"
    _EVENT_NAME = "user run error"

    def __init__(self, dot_jumper):
        self._error_type_list = ["unimplemented_instruction", "unimplemented_section", "jemu_error", "user_error"]

        self._web_api = None
        self._analytics = None
        self._fw_file_link = None
        self._log_file_link = None
        self._jemu_cmd = None
        self._sdk_cmd = 'jumper ' + ' '.join(sys.argv[1:])
        self._filename = None
        self._log_file_path = dot_jumper + '/log.txt'

    def set_jemu_connection(self, jemu_connection, local_jemu):
        if not local_jemu:
            jemu_connection.register(self.receive_packet)

    def set_analytics(self, analytics):
        self._analytics = analytics

    def set_web_api(self, web_api):
        self._web_api = web_api

    def set_file_download_link(self, file_link):
        self._fw_file_link = file_link

    def set_log_file_download_link(self, file_link):
        self._log_file_link = file_link

    def set_filename(self, filename):
        self._filename = filename

    def set_jemu_cmd(self, jemu_cmd):
        self._jemu_cmd = ' '.join(jemu_cmd)

    def _wait_for_log_file_link(self):
        while self._log_file_link is None:
            sleep(0.1)

    def _wait_for_filename(self):
        while self._filename is None:
            sleep(0.1)

    def receive_packet(self, jemu_packet):
        if not self._analytics:
            return

        jemu_packet_type = jemu_packet[self._DESCRIPTION]
        if any(jemu_packet_type in error_type for error_type in self._error_type_list):
            self._wait_for_filename()
            self._upload_log_file()
            self._wait_for_log_file_link()
            self._send_event(jemu_packet)

    def _send_event(self, jemu_packet):
        to_send = {'event': self._EVENT_NAME, 'labels': {
            'message': jemu_packet[self._VALUE],
            'fw_file_link': self._fw_file_link,
            'log_file_link': self._log_file_link,
            'filename': self._filename,
            'jemu_cmd': self._jemu_cmd,
            'sdk_cmd': self._sdk_cmd,
            'error_type': jemu_packet[self._DESCRIPTION],
            'running_from_cloud': 'RUNNING_FROM_CLOUD' in os.environ
        }}
        try:
            self._analytics.add_event(to_send)
        except:
            print("error sending error event")

    def _upload_log_file(self):
        if os.name == 'nt':
            return
        self._web_api.upload_log_file(self._log_file_path, self._filename + "_log.txt", self)
