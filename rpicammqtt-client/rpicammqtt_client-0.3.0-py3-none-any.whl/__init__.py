import json
import logging
import time
import yaml
from pkg_resources import resource_string

_LOGGER = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.ERROR,
)


class RpiCamMqttClient:
    """MQTT client for rpicam."""
    STATUSES = ('halted', 'image', 'md_ready', 'md_video',
                'ready', 'timelapse', 'tl_md_ready', 'video')
    INACTIVE_STATUSES = ('halted', 'Unknown', None)
    ACTIVE_STATUSES = ('image', 'md_ready', 'md_video',
                       'ready', 'timelapse', 'tl_md_ready', 'video')
    RECORDING_STATUSES = ('image', 'md_video', 'timelapse', 'video')
    MOTION_STATUSES = ('md_ready', 'md_video', 'tl_md_ready')
    EXPOSURE_MODES = (
        "off",
        "auto",
        "night",
        "nightpreview",
        "backlight",
        "spotlight",
        "sports",
        "snow",
        "beach",
        "verylong",
        "fixedfps",
        "antishake",
        "fireworks"
    )
    WB_MODES = (
        "off",
        "auto",
        "sun",
        "cloudy",
        "shade",
        "tungsten",
        "fluorescent",
        "incandescent",
        "flash",
        "horizon"
    )
    METERING_MODES = (
        "average",
        "spot",
        "backlit",
        "matrix"
    )
    EFFECTS = (
        "none",
        "negative",
        "solarise",
        "posterize",
        "whiteboard",
        "blackboard",
        "sketch",
        "denoise",
        "emboss",
        "oilpaint",
        "hatch",
        "gpen",
        "pastel",
        "watercolour",
        "film",
        "blur",
        "saturation",
        "colourswap",
        "washedout",
        "posterise ",
        "colourpoint",
        "colourbalance",
        "cartoon"
    )
    topics = {}
    default_topics = {
            # Topic where camera commands are sent
            "cmd": "rpicam/{}",
            # Status of the camera
            "status": "rpicam/{}/status",
            # Topic where pan/tilt commands are sent
            "pantilt": "rpicam/{}/pt",
            # Pan/tilt views made available by the camera
            "ptviews": "rpicam/{}/pt/views"
        }
    topic_names = list(default_topics.keys())

    def __init__(self, pub_callback, sub_callback,
                 camera_name, qos=1, retain=True):
        # Should accept topic, payload, qos, retain.
        self._pub_callback = pub_callback
        # Should accept topic, function callback for receive and qos.
        self._sub_callback = sub_callback
        self.camera = camera_name
        self.define_topics(self.default_topics)
        self.qos = qos
        self._retain = retain  # flag to publish with retain

        self.rpi_commands = yaml.load(
            resource_string(
                __name__,
                "data/rpicam_commands.yaml"
            ).decode('utf-8')
        )

        self.rpi_info = {'status': None, 'ptviews': None}
        self._subscribe_rpicam()
        # Delay to allow the subscription to complete
        time.sleep(0.5)

    def get_cmd_list(self):
        """Returns the list of commands"""
        return [c['Cmd'] for c in self.rpi_commands]

    def get_cmd_info(self, cmd):
        """Returns command params and description"""
        for c in self.rpi_commands:
            if c['Cmd'] == cmd:
                return c['Parameters'], c['Description']

    def run_command(self, full_command):
        """Run formatted command string"""
        self.send(self.topics['cmd'], full_command, self.qos)

    def define_topics(self, custom_topics):
        """Redefine topics
        Override the predefined topics with custom ones.
        All topics are expected to contain the camera name, which
        is added by this method."""
        for tname in self.topic_names:
            if custom_topics[tname] is not None:
                self.topics[tname] = custom_topics[tname].format(self.camera)

    def _subscribe_rpicam(self):
        """Handle rpicam subscriptions

         Subscribe to status and ptviews topics."""
        topic_ids = ['status', 'ptviews']

        for id in list(self.rpi_info.keys()):
            topic = self.topics[id]
            try:
                _LOGGER.debug('Subscribing to: %s, qos: %s', topic, self.qos)
                self._sub_callback(topic, self.recv, self.qos)
            except Exception as exception:  # pylint: disable=broad-except
                _LOGGER.exception(
                    'Subscribe to %s failed: %s', topic, exception)

    def recv(self, topic, payload, qos):
        """Receive a MQTT message.

        Call this method when a message is received from the MQTT broker.
        """
        data = str(payload)
        if data is not None:
            if topic == self.topics['status']:
                self.rpi_info['status'] = data \
                    if data in self.STATUSES else None
            elif topic == self.topics['ptviews']:
                self.rpi_info['ptviews'] = json.loads(data)
        _LOGGER.debug('Receiving %s', data)

    def send(self, topic, message, qos):
        """Send message to the MQTT broker."""
        if not message:
            return
        try:
            _LOGGER.debug('Publishing %s', message.strip())
            self._pub_callback(topic, message, qos, self._retain)
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.exception('Publish to %s failed: %s', topic, exception)

    def get_status(self):
        """Provide the status string"""
        return self.rpi_info['status']

    def get_ptviews(self):
        """Returns the list of pantilt views, if any"""
        return self.rpi_info['ptviews']

    def is_active(self):
        """Tells if the camera is on or off"""
        return bool(self.rpi_info['status'] in self.ACTIVE_STATUSES)

    def is_ptview_available(self):
        """Tells if the camera supports pantilt views"""
        available = False
        if self.rpi_info['ptviews']:
            available = True
        return available

    def is_recording(self):
        """Tells if the camera is recording"""
        return bool(self.rpi_info['status'] in self.RECORDING_STATUSES)

    def is_detecting_motion(self):
        """Tells if the camera is detecting motion"""
        return bool(self.rpi_info['status'] in self.MOTION_STATUSES)

    def set_camera_status(self, active=False):
        """Enable/disable camera"""
        cmd = "ru 0"
        if active:
            cmd = "ru 1"
        self.run_command(cmd)

    def set_motion_detection_status(self, active=False):
        """Enable/disable motion detection"""
        cmd = "md 0"
        if active:
            cmd = "md 1"
        self.run_command(cmd)

    def start_video(self, duration=None):
        """Start recording a video

        If duration in seconds is specified,
        it doesn't need a call to stop_video"""
        cmd = 'ca 1'
        if duration:
            cmd = "{} {}".format(cmd, duration)
        self.run_command(cmd)

    def stop_video(self, duration=None):
        """Stop camera recording"""
        if self.is_recording():
            cmd = 'ca 0'
            self.run_command(cmd)

    def take_picture(self):
        """Take a picture"""
        cmd = 'im 1'
        self.run_command(cmd)

    def set_exposure_mode(self, mode=None):
        """Set exposure mode"""
        if mode and mode in self.EXPOSURE_MODES:
            cmd = "em {}".format(mode)
            self.run_command(cmd)

    def set_wb_mode(self, mode=None):
        """Set white balance mode"""
        if mode and mode in self.WB_MODES:
            cmd = "wb {}".format(mode)
            self.run_command(cmd)

    def set_metering_mode(self, mode=None):
        """Set metering mode"""
        if mode and mode in self.METERING_MODES:
            cmd = "mm {}".format(mode)
            self.run_command(cmd)

    def set_image_effect(self, filter=None):
        """Set image effect"""
        if filter and filter in self.EFFECTS:
            cmd = "ie {}".format(filter)
            self.run_command(cmd)

    def set_pantilt(self, view=None, pan=None, tilt=None):
        """Publish a pantilt command."""
        cmd = {'view': view if view in self.rpi_info['ptviews'] else None,
               'pan': pan,
               'tilt': tilt
               }
        self.send(self.topics['pantilt'], json.dumps(cmd), self.qos)


def main():
    pass


if __name__ == "__main__":
    main()
