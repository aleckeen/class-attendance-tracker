# Author:
# auri@sol <omerfarukcavus@outlook.com>

from vision.implementations import CameraFeed

test_no = '5'
data_folder = f'../data/camera_feed_test/{test_no}'
iterations = 5

camera_opencv = CameraFeed.create_opencv()
for i in range(iterations):
    frame = camera_opencv.capture()
    frame.flip(h=True, v=True)
    print(f"OpenCV {i}")
    frame.save(f"{data_folder}/{i}_opencv.png")
del camera_opencv

camera_picamera = CameraFeed.create_picamera()
for i in range(iterations):
    frame = camera_picamera.capture()
    frame.flip(h=True, v=True)
    print(f"PiCamera {i}")
    frame.save(f"{data_folder}/{i}_picamera.png")
del camera_picamera
