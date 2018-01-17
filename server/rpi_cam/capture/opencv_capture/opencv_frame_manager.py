import cv2

from rpi_cam.capture.frame_manager import FrameManager
from rpi_cam.capture.tools import crop_to_ratio


class OpenCVFrameManager(FrameManager):
    def start(self):
        super().start()
        self.camera = cv2.VideoCapture(0)
        self.image_resolution = (self.camera.get(3), self.camera.get(4))

    def get_image(self):
        if self.camera is None:
            self.start()

        ret, frame = self.camera.read()
        if ret:
            return frame
        else:
            return None

    def get_preview(self):
        frame = self.get_image()
        cropped = crop_to_ratio(frame, self.preview_resolution[0] / self.preview_resolution[1])
        if frame is not None:
            thumb = cv2.resize(cropped, self.preview_resolution, interpolation=cv2.INTER_CUBIC)
            return thumb
        else:
            return None

    def report_state(self):
        state = super().report_state()

        state['data']['driver'] = 'OpenCV'

        return state

    def write_img(self, filename, img):
        cv2.imwrite(filename, img)

    def stop(self):
        super().stop()
        self.camera.release()
        self.camera = None
        self.image_resolution = None
        cv2.destroyAllWindows()
