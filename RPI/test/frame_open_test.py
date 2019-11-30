# Author:
# auri@sol <omerfarukcavus@outlook.com>

from vision.implementations import CameraFeed, Frame

test_no = '1'
data_folder = f'../data/frame_open_test/{test_no}'

camera = CameraFeed.create_picamera()
frame = camera.capture()
frame.flip(h=True, v=True)
frame.save(f'{data_folder}/saved.jpg')

frame = Frame.open_path(f'{data_folder}/saved.jpg')
frame.save(f"{data_folder}/read_then_saved.jpg")
