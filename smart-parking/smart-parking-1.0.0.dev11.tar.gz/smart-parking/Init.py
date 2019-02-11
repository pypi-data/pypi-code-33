from Configuration.config import Configuration
from Camera.camera import Camera
from Parking.monitor import Parking
from Log.log import Logger
from Log.logLevel import LogLevel


class Init():
    if __name__ == "__main__":
        configuration = Configuration()
        camera = Camera(configuration)
        monitor = Parking(configuration)
        while True:
            try:
                frame = camera.readStreaming()
                frame = monitor.parking(frame, camera.video_cur_pos, camera.video_cur_frame)
                camera.showFrame(frame)
            except (KeyboardInterrupt):
                configuration.logger.log(LogLevel.INFO,"Exiting apllication!!")
                if camera.video_capture.isOpened():
                    configuration.logger.log(LogLevel.INFO,"Release camera streaming.")
                    camera.video_capture.release()