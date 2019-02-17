
import os
import re
import subprocess
import sys
import time

from abc import ABC
from colibris import settings
from colibris import schemas

from testmyesp import attributes
from testmyesp.instructions import BaseInstruction, register_instruction, InstructionException


class WiFiInstructionException(InstructionException):
    pass


class HostAPDException(WiFiInstructionException):
    pass


class DNSMasqException(WiFiInstructionException):
    pass


class WPASupplicantException(WiFiInstructionException):
    pass


class DHClientException(WiFiInstructionException):
    pass


class IPConfigException(WiFiInstructionException):
    pass


class WiFiInstruction(BaseInstruction, ABC):
    REG_COUNTRY = 'GB'

    HOSTAPD_CONF_TEMPLATE = (
        'ssid={ssid}\n'
        'wpa_passphrase={psk}\n'
        'wpa=2\n'
        'wpa_key_mgmt=WPA-PSK\n'
        'interface={interface}\n'
        'channel=1\n'
        'driver=nl80211\n'
        'hw_mode=g\n'
        'ieee80211n=1\n'
        'ieee80211ac=1\n'
    )

    DNSMASQ_CONF_TEMPLATE = (
        'interface={interface}\n'
        'dhcp-range={start_ip},{stop_ip},24h\n'
        'dhcp-leasefile=/tmp/dnsmasq.leases\n'
    )

    WPA_SUPPLICANT_CONF_TEMPLATE = (
        'country={country}\n'
        'ctrl_interface=/var/run/wpa_supplicant\n'
        '\n'
        'network={{\n'
        '    scan_ssid=1\n'
        '    ssid="{ssid}"\n'
        '    psk="{psk}"\n'
        '}}\n'
    )

    DHCLIENT_CONF_TEMPLATE = (
        'send host-name = gethostname();\n'
        'request subnet-mask, broadcast-address;\n'
    )

    HOSTAPD_CONF_FILE = '/tmp/hostapd.conf'
    HOSTAPD_LOG_FILE = '/tmp/hostapd.log'

    DNSMASQ_CONF_FILE = '/tmp/dnsmasq.conf'
    DNSMASQ_LOG_FILE = '/tmp/dnsmasq.log'

    WPA_SUPPLICANT_CONF_FILE = '/tmp/wpa_supplicant.conf'
    WPA_SUPPLICANT_LOG_FILE = '/tmp/wpa_supplicant.log'

    DHCLIENT_CONF_FILE = '/tmp/dhclient.conf'
    DHCLIENT_LOG_FILE = '/tmp/dhclient.log'

    PROCESS_SETTLE_TIME = 2
    PROCESS_TERM_TIMEOUT = 2
    DEFAULT_TIMEOUT = 15

    def __init__(self, ssid=None, psk=None, timeout=None,
                 host_ip_address=None, device_ip_address=None,
                 start_ip_address=None, stop_ip_address=None):

        self.ssid = ssid
        self.psk = psk
        self.timeout = timeout or self.DEFAULT_TIMEOUT

        self.host_ip_address = host_ip_address
        self.device_ip_address = device_ip_address

        self.start_ip_address = start_ip_address
        self.stop_ip_address = stop_ip_address

        self.remaining_timeout = self.timeout

        if self.device_ip_address:
            attributes.set(attributes.DEVICE_IP_ADDRESS, self.device_ip_address)

        # some arping variants have a -C N option to stop after receiving that number of replies;
        # others have a -f option to stop after receiving the first reply
        self._arping_has_c_option = self._guess_arping_has_c_option()

        super().__init__()

    @property
    def dev_null(self):
        return open(os.devnull, 'w')

    @staticmethod
    def print_log_file(log_file):
        log_file.seek(0)
        for line in log_file:
            sys.stderr.write('    {}'.format(line))

    def _guess_arping_has_c_option(self):
        try:
            subprocess.check_call('arping 2>&1 | grep \-C', shell=True, stdout=self.dev_null, stderr=subprocess.STDOUT)
            return True

        except subprocess.CalledProcessError:
            return False

    def start_hostapd(self):
        self.logger.debug('starting hostapd with ssid "%s" and psk "%s"', self.ssid, self.psk)

        log_file = open(self.HOSTAPD_LOG_FILE, 'w+')

        with open(self.HOSTAPD_CONF_FILE, 'w') as conf_file:
            conf = self.HOSTAPD_CONF_TEMPLATE.format(ssid=self.ssid, psk=self.psk,
                                                     interface=settings.WIFI_INTERFACE)
            conf_file.write(conf)

        subprocess.Popen(['hostapd', conf_file.name], stdout=log_file, stderr=subprocess.STDOUT)

        # allow for the process to settle
        time.sleep(self.PROCESS_SETTLE_TIME)
        self.remaining_timeout -= self.PROCESS_SETTLE_TIME

        if not self.is_hostapd_running():
            msg = 'could not start hostapd'
            self.logger.error(msg)
            self.print_log_file(log_file)

            raise HostAPDException(msg)

    def stop_hostapd(self):
        self.logger.debug('stopping hostapd')
        os.system('killall hostapd >/dev/null 2>&1')

        # allow for the process to gracefully exit
        time.sleep(self.PROCESS_TERM_TIMEOUT)
        if self.is_hostapd_running():
            self.logger.warning('killing hostapd with fire')
            os.system('killall -9 hostapd >/dev/null 2>&1')

    def is_hostapd_running(self):
        try:
            subprocess.check_call('ps aux | grep hostapd | grep -v grep',
                                  shell=True, stdout=self.dev_null, stderr=subprocess.STDOUT)

            return True

        except subprocess.CalledProcessError:
            return False

    def start_dnsmasq(self, wait_device_connect=False):
        self.logger.debug('starting dnsmasq')

        # start with empty leases file
        try:
            os.remove('/tmp/dnsmasq.leases')

        except OSError:
            pass

        start_ip = self.start_ip_address or settings.START_IP
        stop_ip = self.stop_ip_address or settings.STOP_IP

        log_file = open(self.DNSMASQ_LOG_FILE, 'w+')

        with open(self.DNSMASQ_CONF_FILE, 'w') as conf_file:
            conf = self.DNSMASQ_CONF_TEMPLATE.format(interface=settings.WIFI_INTERFACE,
                                                     start_ip=start_ip,
                                                     stop_ip=stop_ip)
            conf_file.write(conf)

        subprocess.Popen(['dnsmasq', '-d', '-C', conf_file.name], stdout=log_file, stderr=subprocess.STDOUT)

        # allow for the process to settle
        time.sleep(self.PROCESS_SETTLE_TIME)
        self.remaining_timeout -= self.PROCESS_SETTLE_TIME

        if not self.is_dnsmasq_running():
            msg = 'could not start dnsmasq'
            self.logger.error(msg)
            self.print_log_file(log_file)

            raise DNSMasqException(msg)

        if not wait_device_connect:
            return

        while self.remaining_timeout > 0:
            if self.is_dnsmasq_device_connected():
                self.logger.debug('device connected')
                break

            time.sleep(1)
            self.remaining_timeout -= 1

        else:
            msg = 'timeout waiting for device to connect'
            self.logger.error(msg)
            self.stop_dnsmasq()

            raise DNSMasqException(msg)

    def stop_dnsmasq(self):
        self.logger.debug('stopping dnsmasq')
        os.system('killall dnsmasq >/dev/null 2>&1')

        # allow for the process to gracefully exit
        time.sleep(self.PROCESS_TERM_TIMEOUT)
        if self.is_dnsmasq_running():
            self.logger.warning('killing dnsmasq with fire')
            os.system('killall -9 dnsmasq >/dev/null 2>&1')

    def is_dnsmasq_running(self):
        try:
            subprocess.check_call('ps aux | grep dnsmasq | grep -v grep',
                                  shell=True, stdout=self.dev_null, stderr=subprocess.STDOUT)

            return True

        except subprocess.CalledProcessError:
            return False

    def is_dnsmasq_device_connected(self):
        with open('/tmp/dnsmasq.leases') as f:
            for line in f:
                m = re.match(r'^\d+ ([a-f0-9:]{17}) ([0-9.]{7,15}) ([a-zA-Z0-9_-]+)', line)
                if not m:
                    continue

                mac_address = m.group(1)
                ip_address = m.group(2)

                self.logger.debug('captured device IP address: %s', ip_address)
                self.logger.debug('captured device MAC address: %s', mac_address)

                attributes.set(attributes.DEVICE_IP_ADDRESS, ip_address)
                attributes.set(attributes.DEVICE_MAC_ADDRESS, mac_address)

                return True

        return False

    def start_wpa_supplicant(self):
        self.logger.debug('starting wpa_supplicant')

        try:
            subprocess.check_call('iw reg set {}'.format(self.REG_COUNTRY),
                                  shell=True, stdout=self.dev_null, stderr=subprocess.STDOUT)

            self.logger.debug('regulatory domain country set to %s', self.REG_COUNTRY)

        except subprocess.CalledProcessError:
            raise WPASupplicantException('could not set regulatory domain country')

        log_file = open(self.WPA_SUPPLICANT_LOG_FILE, 'w+')

        with open(self.WPA_SUPPLICANT_CONF_FILE, 'w') as conf_file:
            cmd = ['wpa_supplicant', '-D', 'nl80211', '-i', settings.WIFI_INTERFACE, '-c', conf_file.name]

            conf = self.WPA_SUPPLICANT_CONF_TEMPLATE.format(ssid=self.ssid, psk=self.psk, country=self.REG_COUNTRY)
            conf_file.write(conf)

        subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)

        # allow for the process to settle
        time.sleep(self.PROCESS_SETTLE_TIME)
        self.remaining_timeout -= self.PROCESS_SETTLE_TIME
        if not self.is_wpa_supplicant_running():
            msg = 'could not start wpa_supplicant'
            self.logger.error(msg)
            self.print_log_file(log_file)

            raise WPASupplicantException(msg)

        # wait for connection
        while self.remaining_timeout > 0:
            if self.is_wpa_supplicant_connected():
                break

            time.sleep(1)
            self.remaining_timeout -= 1

        else:
            self.stop_wpa_supplicant()
            raise WPASupplicantException('could not connect to wifi')

    def stop_wpa_supplicant(self):
        self.logger.debug('stopping wpa_supplicant')
        os.system('killall wpa_supplicant >/dev/null 2>&1')

        # allow for the process to gracefully exit
        time.sleep(self.PROCESS_TERM_TIMEOUT)
        if self.is_wpa_supplicant_running():
            self.logger.warning('killing wpa_supplicant with fire')
            os.system('killall -9 wpa_supplicant >/dev/null 2>&1')

    def is_wpa_supplicant_running(self):
        try:
            subprocess.check_call('ps aux | grep wpa_supplicant | grep -v grep',
                                  shell=True, stdout=self.dev_null, stderr=subprocess.STDOUT)

            return True

        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def is_wpa_supplicant_connected():
        cmd = ['wpa_cli', '-i', settings.WIFI_INTERFACE, 'status']

        try:
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            return result.index(b'COMPLETED') >= 0

        except ValueError:
            return False

        except subprocess.CalledProcessError:
            return False

    def start_dhclient(self):
        self.logger.debug('starting dhclient')

        log_file = open(self.DHCLIENT_LOG_FILE, 'w+')

        with open(self.DHCLIENT_CONF_FILE, 'w') as conf_file:
            conf = self.DHCLIENT_CONF_TEMPLATE
            conf_file.write(conf)

        cmd = ['dhclient', '-v', '-cf', conf_file.name, '-d', settings.WIFI_INTERFACE]
        subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)

        # allow for the process to settle
        time.sleep(self.PROCESS_SETTLE_TIME)
        self.remaining_timeout -= self.PROCESS_SETTLE_TIME
        if not self.is_dhclient_running():
            msg = 'could not start dhclient'
            self.logger.error(msg)
            self.print_log_file(log_file)
            raise DHClientException(msg)

        while self.remaining_timeout > 0:
            if self.is_interface_configured():
                break

            time.sleep(1)
            self.remaining_timeout -= 1

        else:
            msg = 'could not obtain IP address via DHCP'
            self.logger.error(msg)
            self.print_log_file(log_file)
            self.stop_dhclient()

            raise DHClientException(msg)

        # capture IP address of the device
        log_file.seek(0)
        log_text = log_file.read()
        m = re.search(r'from ([\d.]{7,15})', log_text)
        if m:
            ip_address = m.group(1)
            self.logger.debug('captured device IP address: %s', ip_address)
            attributes.set(attributes.DEVICE_IP_ADDRESS, ip_address)

    def stop_dhclient(self):
        self.logger.debug('stopping dhclient')
        os.system('killall dhclient {interface} >/dev/null 2>&1'.format(interface=settings.WIFI_INTERFACE))

        # allow for the process to gracefully exit
        time.sleep(self.PROCESS_TERM_TIMEOUT)
        if self.is_dhclient_running():
            self.logger.warning('killing dhclient with fire')
            os.system('killall -9 dhclient {interface} >/dev/null 2>&1'.format(interface=settings.WIFI_INTERFACE))

    def is_dhclient_running(self):
        cmd = 'ps aux | grep dhclient | grep {interface} | grep -v grep'.format(interface=settings.WIFI_INTERFACE)

        try:
            subprocess.check_call(cmd, shell=True, stdout=self.dev_null, stderr=subprocess.STDOUT)
            return True

        except subprocess.CalledProcessError:
            return False

    def is_interface_configured(self):
        cmd = 'ip addr show dev {interface} | grep inet'.format(interface=settings.WIFI_INTERFACE)

        try:
            subprocess.check_call(cmd, shell=True, stdout=self.dev_null, stderr=subprocess.STDOUT)
            return True

        except subprocess.CalledProcessError:
            return False

    def is_arp_device_connected(self, ip_address):
        cmd = 'arping -I {interface} -c 3 '
        if self._arping_has_c_option:
            cmd += '-C 1 '

        else:
            cmd += '-f '

        cmd += '{ip_address}'
        cmd = cmd.format(interface=settings.WIFI_INTERFACE, ip_address=ip_address)

        try:
            subprocess.check_call(cmd, shell=True, stdout=self.dev_null, stderr=subprocess.STDOUT)

            return True

        except subprocess.CalledProcessError:
            return False

    def set_host_ip(self):
        ip_address = self.host_ip_address or settings.HOST_IP

        self.logger.debug('setting host IP address to %s', ip_address)

        flush_cmd = 'ip addr flush dev {interface}'.format(interface=settings.WIFI_INTERFACE)
        add_cmd = 'ip addr add {addr} dev {interface}'.format(addr=ip_address, interface=settings.WIFI_INTERFACE)

        try:
            subprocess.check_call(flush_cmd, shell=True)
            subprocess.check_call(add_cmd, shell=True)

        except subprocess.CalledProcessError:
            raise IPConfigException('could not set host IP address')

    def flush_arp_cache(self):
        self.logger.debug('flushing ARP cache')

        cmd1 = 'ip link set arp off dev {interface}'
        cmd2 = 'ip link set arp on dev {interface}'
        cmd1 = cmd1.format(interface=settings.WIFI_INTERFACE)
        cmd2 = cmd2.format(interface=settings.WIFI_INTERFACE)

        try:
            subprocess.check_call(cmd1, shell=True)
            subprocess.check_call(cmd2, shell=True)

        except subprocess.CalledProcessError:
            raise IPConfigException('could not flush ARP cache')

    def stop_all(self):
        if self.is_dhclient_running():
            self.stop_dhclient()
        if self.is_wpa_supplicant_running():
            self.stop_wpa_supplicant()
        if self.is_hostapd_running():
            self.stop_hostapd()
        if self.is_dnsmasq_running():
            self.stop_dnsmasq()
        self.flush_arp_cache()

    def tear_down_job(self):
        self.stop_all()


class WiFiInstructionSchema(schemas.Schema):
    ssid = schemas.fields.String(validate=schemas.validate.Length(1, 32))
    psk = schemas.fields.String(validate=schemas.validate.Length(8, 64))
    timeout = schemas.fields.Integer(validate=schemas.validate.Range(1, 60))
    host_ip_address = schemas.fields.String(validate=schemas.validate.Regexp(r'^[0-9/.]{7,18}$'))
    device_ip_address = schemas.fields.String(validate=schemas.validate.Regexp(r'^[0-9.]{7,15}$'))
    start_ip_address = schemas.fields.String(validate=schemas.validate.Regexp(r'^[0-9.]{7,15}$'))
    stop_ip_address = schemas.fields.String(validate=schemas.validate.Regexp(r'^[0-9.]{7,15}$'))


@register_instruction
class WiFiAPStart(WiFiInstruction):
    NAME = 'wifi-ap-start'

    def __init__(self, ssid, psk=None, timeout=None,
                 host_ip_address=None, device_ip_address=None,
                 start_ip_address=None, stop_ip_address=None,
                 wait_device_connect=True):

        self.wait_device_connect = wait_device_connect

        super().__init__(ssid=ssid, psk=psk, timeout=timeout,
                         host_ip_address=host_ip_address, device_ip_address=device_ip_address,
                         start_ip_address=start_ip_address, stop_ip_address=stop_ip_address)

    def execute(self):
        self.stop_all()

        self.start_hostapd()
        self.set_host_ip()

        if self.device_ip_address:
            if self.wait_device_connect:
                while self.remaining_timeout > 0:
                    if self.is_arp_device_connected(self.device_ip_address):
                        self.logger.debug('device connected')
                        break

                    time.sleep(1)
                    self.remaining_timeout -= 1

                else:
                    msg = 'timeout waiting for device to connect'
                    self.logger.error(msg)

                    raise WiFiInstructionException(msg)

        else:
            self.start_dnsmasq(self.wait_device_connect)

    class Schema(WiFiInstructionSchema):
        wait_device_connect = schemas.fields.Boolean()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields['ssid'].required = True


@register_instruction
class WiFiAPStop(WiFiInstruction):
    NAME = 'wifi-ap-stop'

    def __init__(self):
        super().__init__()

    def execute(self):
        self.stop_all()

    Schema = None


@register_instruction
class WiFiAPWaitDeviceConnect(WiFiInstruction):
    NAME = 'wifi-ap-wait-device-connect'

    def __init__(self, timeout=None, device_ip_address=None):
        super().__init__(timeout=timeout, device_ip_address=device_ip_address)

    def execute(self):
        ip_address = self.device_ip_address or attributes.get(attributes.DEVICE_IP_ADDRESS)
        if not ip_address:
            raise WiFiInstructionException('device IP address is unknown')

        while self.remaining_timeout > 0:
            if self.is_arp_device_connected(ip_address):
                self.logger.debug('device connected')
                break

            time.sleep(1)
            self.remaining_timeout -= 1

        else:
            msg = 'timeout waiting for device to connect'
            self.logger.error(msg)

            raise WiFiInstructionException(msg)

    class Schema(WiFiInstructionSchema):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields.pop('ssid')
            self.fields.pop('psk')
            self.fields.pop('host_ip_address')
            self.fields.pop('start_ip_address')
            self.fields.pop('stop_ip_address')


@register_instruction
class WiFiAPWaitDeviceDisconnect(WiFiInstruction):
    NAME = 'wifi-ap-wait-device-disconnect'

    def __init__(self, timeout=None, device_ip_address=None):
        super().__init__(timeout=timeout, device_ip_address=device_ip_address)

    def execute(self):
        ip_address = self.device_ip_address or attributes.get(attributes.DEVICE_IP_ADDRESS)
        if not ip_address:
            raise WiFiInstructionException('device IP address is unknown')

        while self.remaining_timeout > 0:
            if not self.is_arp_device_connected(ip_address):
                self.logger.debug('device disconnected')
                break

            time.sleep(1)
            self.remaining_timeout -= 1

        else:
            msg = 'timeout waiting for device to disconnect'
            self.logger.error(msg)

            raise WiFiInstructionException(msg)

    class Schema(WiFiInstructionSchema):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields.pop('ssid')
            self.fields.pop('psk')
            self.fields.pop('host_ip_address')
            self.fields.pop('start_ip_address')
            self.fields.pop('stop_ip_address')


@register_instruction
class WiFiStationConnect(WiFiInstruction):
    NAME = 'wifi-station-connect'

    def __init__(self, ssid, psk=None, timeout=None, host_ip_address=None):
        super().__init__(ssid=ssid, psk=psk, timeout=timeout, host_ip_address=host_ip_address)

    def execute(self):
        self.stop_all()

        self.start_wpa_supplicant()
        if self.host_ip_address:
            self.set_host_ip()

        else:
            self.start_dhclient()

    class Schema(WiFiInstructionSchema):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields['ssid'].required = True
            self.fields.pop('device_ip_address')
            self.fields.pop('start_ip_address')
            self.fields.pop('stop_ip_address')


@register_instruction
class WiFiStationDisconnect(WiFiInstruction):
    NAME = 'wifi-station-disconnect'

    def __init__(self):
        super().__init__()

    def execute(self):
        self.stop_all()

    Schema = None
