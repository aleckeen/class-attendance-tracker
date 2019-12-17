import concurrent.futures.process
import os
from enum import Enum

import cv2
import face_recognition
import numpy as np
from PIL import Image
from io import BytesIO
from picamera import PiCamera
from typing import List, Tuple, Optional, Union, Iterator

# Settings
HAARCASCADES = '/usr/share/opencv/haarcascades'
RESOLUTION_PICAMERA = (2560, 1920)
RESOLUTION_OPENCV = (1920, 1080)

# OpenCV
face_cascade = cv2.CascadeClassifier(f'{HAARCASCADES}/haarcascade_frontalface_default.xml')


def capture_frame_picamera(camera: PiCamera) -> np.ndarray:
    frame = np.empty((camera.resolution[1] * camera.resolution[0] * 3,), dtype=np.uint8)
    camera.capture(frame, 'bgr')
    frame = frame.reshape((camera.resolution[1], camera.resolution[0], 3))
    return frame


def capture_frame_opencv(camera) -> np.ndarray:
    _, frame = camera.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame


def write_frame(frame: np.ndarray, buffer: BytesIO, ext: str):
    _, _buf = cv2.imencode(ext, frame)
    buffer.write(_buf)


def save_frame(frame: np.ndarray, path: str):
    ext = os.path.splitext(path)[-1]
    buffer = BytesIO()
    write_frame(frame, buffer, ext)
    f = open(path, "wb")
    f.write(buffer.getvalue())
    f.close()
    buffer.close()


def open_frame_path(path: str) -> np.ndarray:
    frame = cv2.imread(path)
    return frame


def open_frame_bytes(buffer: bytes) -> np.ndarray:
    with BytesIO(buffer) as b:
        b.seek(0)
        frame = Image.open(b)
        frame = np.array(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame


# Takes in a image in OpenCV format(BGR). Returns a list of images in OpenCV format.
# Uses OpenCV to process.
def detect_faces_opencv(frame: np.ndarray) -> List[np.ndarray]:
    rois: List[np.ndarray] = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for x, y, w, h in faces:
        roi = frame[y:y + h, x:x + w]
        rois.append(roi)
    return rois


# Uses the face_recognition library to process.
def detect_faces_ageitgey(frame: np.ndarray) -> List[np.ndarray]:
    rois: List[np.ndarray] = []
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_locations = face_recognition.face_locations(gray)
    for face_location in face_locations:
        top, right, bottom, left = face_location
        face = frame[top:bottom, left:right]
        rois.append(face)
    return rois


def face_encoding(face: np.ndarray) -> Optional[np.ndarray]:
    encoding = face_recognition.face_encodings(face)
    if len(encoding) == 0:
        return None
    return encoding[0]


def recognize_face(face: np.ndarray, encodings: List[np.ndarray], ids: np.ndarray) -> Union[None, str, int]:
    if len(encodings) == 0:
        return None
    encoding = face_encoding(face)
    if encoding is None:
        return None
    matches = face_recognition.compare_faces(encodings, encoding)
    face_id = -1
    face_distances = face_recognition.face_distance(encodings, encoding)
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        face_id = ids[best_match_index]
    return face_id


class CaptureEngineError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EncoderLabelError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EncoderEncodeError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Frame:
    frame: np.ndarray

    class Color(Enum):
        BGR2RGB = cv2.COLOR_BGR2RGB
        RGB2BGR = cv2.COLOR_RGB2BGR
        BGR2GRAY = cv2.COLOR_BGR2GRAY
        RGB2GRAY = cv2.COLOR_RGB2GRAY

    def __init__(self, frame: np.ndarray):
        self.frame = frame

    @staticmethod
    def open_path(path: str) -> 'Frame':
        frame = open_frame_path(path)
        frame = Frame(frame)
        return frame

    @staticmethod
    def open_bytes(buffer: bytes) -> 'Frame':
        frame = open_frame_bytes(buffer)
        frame = Frame(frame)
        return frame

    def flip(self, h: bool = False, v: bool = False):
        if h:
            self.frame = cv2.flip(self.frame, 1)
        if v:
            self.frame = cv2.flip(self.frame, 0)

    def save(self, path: str):
        save_frame(self.frame, path)

    def write(self, buffer: BytesIO, ext: str = '.jpg'):
        write_frame(self.frame, buffer, ext)

    def color(self, mode: Color):
        self.frame = cv2.cvtColor(self.frame, mode)

    def copy(self) -> 'Frame':
        return Frame(self.frame.copy())


class CameraFeed:
    camera = None

    def __init__(self, camera):
        self.camera = camera

    @staticmethod
    def create_picamera(resolution: Tuple[int, int] = RESOLUTION_PICAMERA):
        camera = PiCamera()
        camera.resolution = resolution
        camera.start_preview()
        engine = CameraFeed(camera=camera)

        engine._capture_engine = lambda: capture_frame_picamera(camera=camera)
        engine.__del__ = lambda self: self.camera.close()

        return engine

    @staticmethod
    def create_opencv(resolution: Tuple[int, int] = RESOLUTION_OPENCV):
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        engine = CameraFeed(camera=camera)

        engine._capture_engine = lambda: capture_frame_opencv(camera=camera)
        engine.__del__ = lambda self: self.camera.release()

        return engine

    # noinspection PyTypeChecker
    @staticmethod
    def _capture_engine() -> np.ndarray:
        print("Capture engine hasn't been initialized correctly")
        print("Please make sure you used create functions to initialize the camera")
        raise CaptureEngineError("CameraFeed object wasn't initiated correctly")

    def capture(self) -> Frame:
        frame = self._capture_engine()
        frame = Frame(frame=frame)
        return frame

    def __del__(self):
        pass


class FaceDetector:
    @staticmethod
    def ageitgey(frame: Frame) -> List[Frame]:
        faces = detect_faces_ageitgey(frame=frame.frame)
        faces = [Frame(face) for face in faces]
        return faces

    @staticmethod
    def opencv(frame: Frame) -> List[Frame]:
        faces = detect_faces_opencv(frame=frame.frame)
        faces = [Frame(face) for face in faces]
        return faces


class FaceRecognizer:
    encodings: List[np.ndarray] = []
    ids: List[str] = []

    def __init__(self, faces: Iterator[Tuple[Frame, str]]):
        for frame, id_ in faces:
            encoding = face_encoding(frame.frame)
            if encoding is None:
                print(f"An error occurred during the encoding of the face labeled {id_}")
                print("Please make sure the image is proper")
                # raise EncoderEncodeError(f"Failed to recognize face labeled {id_}")
            else:
                self.encodings.append(encoding)
                self.ids.append(id_)

    def recognize_one(self, face: Frame) -> Tuple[Union[None, str, int], Frame]:
        label = recognize_face(face.frame, self.encodings, np.array(self.ids))
        return label, face

    def recognize_many(self, faces: List[Frame]) -> Iterator[Tuple[Union[None, str, int], Frame]]:
        res = []
        for face in faces:
            label = self.recognize_one(face)
            res.append(label)
        return iter(res)

    def recognize_threaded(self, faces: List[Frame]) -> Iterator[Tuple[Union[None, str, int], Frame]]:
        with concurrent.futures.process.ProcessPoolExecutor() as executor:
            labels = [executor.submit(self.recognize_one, face) for face in faces]
            res = []
            for label in concurrent.futures.as_completed(labels):
                res.append(label.result())
            return iter(res)
