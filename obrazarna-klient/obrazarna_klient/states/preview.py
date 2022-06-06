import time
import uuid
import os
import picamera
import pygame

from PIL import Image

from obrazarna_klient.config import CAMERA_RESOLUTION, CAMERA_FRAMERATE, CAMERA_HFLIP, CAMERA_VFLIP, CACHE_DIR, RECORDING_LENGTH


class Preview:
    flip = False

    def __init__(self, screen, dimensions, pictures, font, picture, accompaniment_id):
        self.accompaniment_id = accompaniment_id
        self.picture = picture
        self.screen = screen

        pygame.display.flip()

        # inicializace kamery
        self.camera = picamera.PiCamera()
        self.camera.resolution = CAMERA_RESOLUTION
        self.camera.framerate = CAMERA_FRAMERATE
        self.camera.hflip = CAMERA_HFLIP
        self.camera.vflip = CAMERA_VFLIP
        self.camera.start_preview()

        # vrstva s overlay obrazkem
        self.o = self.camera.add_overlay(picture.mask[0], size=picture.mask[1])
        self.o.alpha = 255
        self.o.layer = 4
        self.overlays = [picture.mask[0], picture.mask[2]]
        self.black_overlay = Image.new("RGBA", (1280, 720), (0,0,0)).tobytes()
        self.overlays_idx = 1

        # internosti
        self.recording = False
        basename = f'{str(time.time()).replace(".", "_")}_{uuid.uuid4().hex}'
        self.video_path = os.path.join(os.path.expanduser(CACHE_DIR), f'{basename}.h264')
        self.image_path = os.path.join(os.path.expanduser(CACHE_DIR), f'{basename}.jpg')

    def process(self, tick, context):
        if self.recording:
            if tick == self.tick_stop:
                self.camera.stop_recording()
                self.o.update(self.black_overlay)
                self.recording = False
                self.screen.fill((0,0,0))
                self.camera.stop_preview()
                self.screen.fill((0,0,0))
                self.camera.close()
                del self.camera
                return "upload"  # TODO:

            elif (tick - self.tick_start) % (CAMERA_FRAMERATE // 2) == 0:
                self.overlays_idx += 1
                if self.overlays_idx >= len(self.overlays):
                    self.overlays_idx = 0
                self.o.update(self.overlays[self.overlays_idx])
        else:
            if context.get('pressed', False):
                self.recording = True
                self.tick_start = tick
                self.tick_stop = tick + RECORDING_LENGTH
                self.camera.start_recording(self.video_path)
                self.o.update(self.overlays[self.overlays_idx])

    def export(self):
        return {
            'accompaniment_id': self.accompaniment_id,
            'video_path': self.video_path,
            'image_path': self.image_path,
            'picture_id': self.picture.id,
        }
