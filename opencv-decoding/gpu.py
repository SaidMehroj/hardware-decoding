import cv2
import time

fname = "/home/mehroj/Coding/hardware-decoding/video/input.mp4"

d_reader = cv2.cudacodec.createVideoReader(fname)

t1 = time.time()

while True:
    success, d_frame = d_reader.nextFrame()
    if not success:
        break

t2 = time.time()

duration_ms = (t2 - t1) * 1000
print(f"Time taken: {duration_ms:.2f} Millisec")
