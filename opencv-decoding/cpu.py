import cv2
import time

cap = cv2.VideoCapture(
    "/home/mehroj/Coding/hardware-decoding/video/input.mp4"
)

if not cap.isOpened():
    print("Ошибка при открытии видео!")
    exit()

video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
video_fps = cap.get(cv2.CAP_PROP_FPS)
video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
video_codec_num = int(cap.get(cv2.CAP_PROP_FOURCC))
video_codec = "".join([chr((video_codec_num >> 8 * i) & 0xFF) for i in range(4)])

t1 = time.time()

key_frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    has_key_frame = cap.get(cv2.CAP_PROP_LRF_HAS_KEY_FRAME)
    if has_key_frame:
        key_frame_count += 1


t2 = time.time()
print(f"Размер видео ({video_width}, {video_height})")
print(f"Количество кадров: {video_frames}")
print(f"Количество ключевых кадров: {key_frame_count}")
print(f"FPS: {video_fps}")
print(f"Тип кодека видео: {video_codec}")
print(f"Длительность видео: ~{(video_frames / video_fps) / 60:.2f} минут")
duration_ms = (t2 - t1) * 1000
print(f"Занятное время: {duration_ms:.2f} Millisec")