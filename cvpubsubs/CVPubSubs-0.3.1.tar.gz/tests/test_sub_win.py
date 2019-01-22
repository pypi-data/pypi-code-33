import threading
import unittest as ut

import pubsub
import numpy as np

import cvpubsubs.webcam_pub as w
from cvpubsubs.listen_default import listen_default
from cvpubsubs.window_sub import SubscriberWindows

if False:
    import numpy as np


def print_keys_thread():
    sub_key = pubsub.subscribe("CVKeyStroke")
    sub_cmd = pubsub.subscribe("CVWinCmd")
    msg_cmd = ''
    while msg_cmd != 'quit':
        key_chr = listen_default(sub_key, timeout=.1)  # type: np.ndarray
        if key_chr is not None:
            print("key pressed: " + str(key_chr))
        msg_cmd = listen_default(sub_cmd, block=False, empty='')
    pubsub.publish("CVWinCmd", 'quit')


def start_print_keys_thread():  # type: (...) -> threading.Thread
    t = threading.Thread(target=print_keys_thread, args=())
    t.start()
    return t


class TestSubWin(ut.TestCase):

    def test_sub(self):
        w.VideoHandlerThread().display()

    def test_image(self):
        img = np.random.uniform(0, 1, (300, 300, 3))
        w.VideoHandlerThread(video_source=img).display()

    def test_sub_with_args(self):
        video_thread = w.VideoHandlerThread(video_source=0,
                                            callbacks=w.display_callbacks,
                                            request_size=(800, 600),
                                            high_speed=False,
                                            fps_limit=8
                                            )

        video_thread.display()

    def test_sub_with_callback(self):
        def redden_frame_print_spam(frame, cam_id):
            frame[:, :, 0] = 0
            frame[:, :, 2] = 0

        w.VideoHandlerThread(callbacks=[redden_frame_print_spam] + w.display_callbacks).display()

    def test_multi_cams_one_source(self):
        def cam_handler(frame, cam_id):
            SubscriberWindows.set_global_frame_dict(cam_id, frame, frame)

        t = w.VideoHandlerThread(0, [cam_handler],
                                 request_size=(1280, 720),
                                 high_speed=True,
                                 fps_limit=240
                                 )

        t.start()

        SubscriberWindows(window_names=['cammy', 'cammy2'],
                          video_sources=[str(0)]
                          ).loop()

        t.join()

    def test_multi_cams_multi_source(self):
        t1 = w.VideoHandlerThread(0, request_size=(1920, 1080))
        t2 = w.VideoHandlerThread(1, request_size=(1920, 1080))

        t1.start()
        t2.start()

        SubscriberWindows(window_names=['cammy', 'cammy2'],
                          video_sources=[0, 1]
                          ).loop()

        t1.join()
        t1.join()
