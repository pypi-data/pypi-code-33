from queue import Empty
from multiprocessing import Event, Value

from stytra.utilities import FrameProcess
from arrayqueues.shared_arrays import TimestampedArrayQueue


class TrackingProcess(FrameProcess):
    """A class which handles taking frames from the camera and processing them,
     as well as dispatching a subset for display

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(
        self,
        in_frame_queue,
        finished_signal: Event = None,
        pipeline=None,
        processing_parameter_queue=None,
        output_queue=None,
        processing_counter: Value = None,
        gui_framerate=30,
        gui_dispatcher=False,
        **kwargs
    ):
        """
        :param in_frame_queue: queue dispatching frames from camera
        :param finished_signal: signal for the end of the acquisition
        :param processing_parameter_queue: queue for function&parameters
        :param gui_framerate: framerate of the display GUI
        """
        super().__init__(name="tracking", **kwargs)

        self.frame_queue = in_frame_queue
        self.gui_queue = TimestampedArrayQueue()  # GUI queue for displaying the image
        self.output_queue = output_queue  # queue for processing output (e.g., pos)
        self.processing_parameter_queue = processing_parameter_queue
        self.processing_counter = processing_counter

        self.finished_signal = finished_signal
        self.gui_framerate = gui_framerate
        self.gui_dispatcher = gui_dispatcher
        self.pipeline_cls = pipeline
        self.pipeline = None

        self.i = 0

    def process_internal(self, frame):
        """Apply processing function to current frame with
        self.processing_parameters as additional inputs.

        Parameters
        ----------
        frame :
            frame to be processed;

        Returns
        -------
        type
            processed output

        """

    def retrieve_params(self):
        while True:
            try:
                param_dict = self.processing_parameter_queue.get(timeout=0.0001)
                self.pipeline.deserialize_params(param_dict)
            except Empty:
                break

    def run(self):
        """Loop where the tracking function runs."""

        self.pipeline = self.pipeline_cls()
        self.pipeline.setup()

        while not self.finished_signal.is_set():

            # Gets the processing parameters from their queue
            self.retrieve_params()

            # Gets frame from its queue, if the input is too fast, drop frames
            # and process the latest, if it is too slow continue:
            try:
                time, frame_idx, frame = self.frame_queue.get(timeout=0.001)
            except Empty:
                continue

            # If a processing function is specified, apply it:

            messages, output = self.pipeline.run(frame)

            for msg in messages:
                self.message_queue.put(msg)

            self.output_queue.put(time, output)

            # calculate the frame rate
            self.update_framerate()

            # put current frame into the GUI queue
            self.send_to_gui(time, self.pipeline.diagnostic_image
            if self.pipeline.diagnostic_image is not None else frame)

        return

    def send_to_gui(self, frametime, frame):
        """ Sends the current frame to the GUI queue at the appropriate framerate"""
        if self.framerate_rec.current_framerate:
            every_x = max(int(self.framerate_rec.current_framerate / self.gui_framerate), 1)
        else:
            every_x = 1
        if self.i == 0:
            self.gui_queue.put(frame, timestamp=frametime)
        self.i = (self.i + 1) % every_x
