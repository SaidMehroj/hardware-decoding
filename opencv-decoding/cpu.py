import cv2
import time

cap = cv2.VideoCapture("/home/mehroj/Coding/hardware-decoding/video/input.mp4")

t1 = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

t2 = time.time()

duration_ms = (t2 - t1) * 1000
print(f"Time taken: {duration_ms:.2f} Millisec")
