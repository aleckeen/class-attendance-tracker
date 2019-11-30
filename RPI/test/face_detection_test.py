# Author:
# auri@sol <omerfarukcavus@outlook.com>

import cv2
from picamera import PiCamera

from vision.implementations import capture_frame_picamera, detect_faces_opencv, save_frame, detect_faces_ageitgey

test_no = '2'
data_folder = f'../data/face_detection_test/{test_no}'

camera = PiCamera()
camera.resolution = (2560, 1920)
camera.start_preview()

frames = []
for i in range(5):
    frame = capture_frame_picamera(camera)
    frame = cv2.flip(frame, 0)
    print(str(i))
    save_frame(frame, f"{data_folder}/{i}.jpg")
    frames.append(frame.copy())

for i in range(len(frames)):
    frame = frames[i]
    faces_opencv = detect_faces_opencv(frame.copy())
    print(f"There are {len(faces_opencv)} face(s) OpenCV")
    for j in range(len(faces_opencv)):
        save_frame(faces_opencv[j], f"{data_folder}/{i}_{j}_opencv.jpg")

    faces_ageitgey = detect_faces_ageitgey(frame.copy())
    print(f"There are {len(faces_ageitgey)} face(s) Ageitgey")
    for j in range(len(faces_ageitgey)):
        save_frame(faces_ageitgey[j], f"{data_folder}/{i}_{j}_ageitgey.jpg")

    print()
