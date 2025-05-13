import cv2
import time

fname = "/home/mehroj/Coding/hardware-decoding/video/input.mp4"

# Для установления параметров вручную
# customparams = cv2.cudacodec.VideoReaderInitParams()
# d_reader = cv2.cudacodec.createVideoReader(fname,params=customparams)

d_reader = cv2.cudacodec.createVideoReader(fname)

# Установка цветового формата, пример
# d_reader.set(cv2.cudacodec.ColorFormat_NV_NV12)
# Поддерживаемые форматы: 'ColorFormat_BGR', 'ColorFormat_BGRA', 'ColorFormat_GRAY', 
# 'ColorFormat_NV_AYUV', 'ColorFormat_NV_IYUV', 'ColorFormat_NV_NV12', 'ColorFormat_NV_YUV444', 
# 'ColorFormat_NV_YV12', 'ColorFormat_PROP_NOT_SUPPORTED', 'ColorFormat_RGB', 'ColorFormat_RGBA', 'ColorFormat_UNDEFINED'


# Характеристики
_,video_width = d_reader.get(cv2.CAP_PROP_FRAME_WIDTH)
_,video_height = d_reader.get(cv2.CAP_PROP_FRAME_HEIGHT)
_,video_fps = d_reader.get(cv2.CAP_PROP_FPS)
_,video_frames = d_reader.get(cv2.CAP_PROP_FRAME_COUNT)
_,video_codec_num = d_reader.get(cv2.CAP_PROP_FOURCC)
video_codec = "".join([chr((int(video_codec_num) >> 8 * i) & 0xFF) for i in range(4)])

t1 = time.time()

key_frame_count = 0

while True:
    success, d_frame = d_reader.nextFrame()
    if not success:
        break
    
    has_key_frame,_ = d_reader.get(cv2.CAP_PROP_LRF_HAS_KEY_FRAME)

    if has_key_frame:
        key_frame_count += 1      

t2 = time.time()

print(f"Размер видео ({video_width},{video_height})")
print(f"Количество кадров: {video_frames}")
print(f"Количество ключевых кадров: {key_frame_count}")
print(f"FPS: {video_frames/(t2 - t1):.2f}")
print(f"Тип кодека видео: {video_codec}")
print(f"Длительность видео: ~{(video_frames/video_fps)/60:.2f}")
duration_ms = (t2 - t1) * 1000
print(f"Занятное время: {duration_ms:.2f} Millisec")