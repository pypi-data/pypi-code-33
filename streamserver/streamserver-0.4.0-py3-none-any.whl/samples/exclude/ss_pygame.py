#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

__author__ = 'cnheider'


def main():
    import pygame.camera
    import streamserver

    pygame.init()
    pygame.camera.init()

    cameras = pygame.camera.list_cameras()

    if cameras:
        camera = pygame.camera.Camera(cameras[0],(640,480))
        #camera = pygame.camera.Camera('/dev/video0', (640, 480))

        while True:
            try:
                camera.start()
                break
            except Exception as e:
                print(e)
                time.sleep(1)

        with streamserver.StreamServer(JPEG_quality=75, host='localhost', port=5000) as ss:
            while True:
                image = camera.get_image()
                ss.set_frame(image)

                if pygame.key.get_pressed() == ord('q'):
                    break
        camera.stop()


if __name__ == '__main__':
    main()
