import json
import logging
import time

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
    default_topics = {
            # Topic where camera commands are sent
            "cmd": "rpicam/{}".format(camera_name),
            # Status of the camera
            "status": "rpicam/{}/status".format(camera_name),
            # Topic where pan/tilt commands are sent
            "pantilt": "rpicam/{}/pt".format(camera_name),
            # Pan/tilt views made available by the camera
            "ptviews": "rpicam/{}/pt/views".format(camera_name)
        }
    topic_names = default_topics.keys()

    def __init__(self, pub_callback, sub_callback,
                 camera_name, qos=1, retain=True):
        # Should accept topic, payload, qos, retain.
        self._pub_callback = pub_callback
        # Should accept topic, function callback for receive and qos.
        self._sub_callback = sub_callback
        self.camera = camera_name
        self.topics = self.default_topics
        self.qos = qos
        self._retain = retain  # flag to publish with retain

        self.rpi_info = { 'status': None, 'ptviews': None }
        self._subscribe_rpicam()
        # Delay to allow the subscription to complete
        time.sleep(0.5)

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

        for id in self.rpi_info.keys():
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
        self.send(self.topics['cmd'], cmd, self.qos)

    def set_motion_detection_status(self, active=False):
        """Enable/disable motion detection"""
        cmd = "md 0"
        if active:
            cmd = "md 1"
        self.send(self.topics['cmd'], cmd, self.qos)

    def start_video(self, duration=None):
        """Start recording a video

        If duration in seconds is specified,
        it doesn't need a call to stop_video"""
        cmd = 'ca 1'
        if duration:
            cmd = "{} {}".format(cmd, duration)
        self.send(self.topics['cmd'], cmd, self.qos)

    def stop_video(self, duration=None):
        """Stop camera recording"""
        if self.is_recording():
            cmd = 'ca 0'
            self.send(self.topics['cmd'], cmd, self.qos)

    def take_picture(self):
        """Take a picture"""
        cmd = 'im 1'
        self.send(self.topics['cmd'], cmd, self.qos)

    def set_exposure_mode(self, mode=None):
        """Set exposure mode"""
        if mode and mode in self.EXPOSURE_MODES:
            cmd = "em {}".format(mode)
            self.send(self.topics['cmd'], cmd, self.qos)

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
