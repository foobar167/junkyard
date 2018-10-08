import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.start_preview()
    # Infinite loop to capture images
    camera.capture_sequence('image{counter:03d}',  format='png', use_video_port=True)
    camera.stop_preview()
