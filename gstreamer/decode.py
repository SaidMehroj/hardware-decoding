import subprocess
import time
import os
import re
import gi
import sys
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Инициализация GStreamer
Gst.init(None)

def get_video_metadata(video_path):
    cmd = ['gst-discoverer-1.0', '-v', video_path]
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = process.communicate()
        return stdout.decode('utf-8')
    except Exception as e:
        print(f"Ошибка при получении информации о видео: {e}")
        return ""

def parse_video_info(output):
    codec_match = re.search(r'video/x-([a-zA-Z0-9]+)', output)
    color_match = re.search(r'format: ([a-zA-Z0-9]+)', output)
    duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', output)

    codec_name = codec_match.group(1) if codec_match else "unknown"
    pix_fmt = color_match.group(1) if color_match else "unknown"

    if duration_match:
        h, m, s = int(duration_match.group(1)), int(duration_match.group(2)), float(duration_match.group(3))
        duration_sec = h * 3600 + m * 60 + s
    else:
        duration_sec = 0

    return {
        'codec_name': codec_name,
        'pix_fmt': pix_fmt,
        'duration': duration_sec
    }

def decode(video_path):
    t1 = time.time()
    
    pipeline_str = f"""
        filesrc location="{video_path}" !
        qtdemux !
        h264parse !
        nvh264dec !
        cudaconvert !
        fakesink name=sink sync=false
    """

    print(f"Pipeline: {pipeline_str.strip()}")
    
    try:
        pipeline = Gst.parse_launch(pipeline_str)
    except GLib.Error as e:
        print(f"Ошибка создания pipeline: {e}")
        return {'duration_ms': 0, 'frame_count': 0, 'fps': 0, 'speed': 0}
    
    sink = pipeline.get_by_name("sink")
    frame_count = [0]

    def on_handoff(sink, buffer, pad, data):
        data[0] += 1
        
    sink.set_property("signal-handoffs", True)
    sink.connect("handoff", on_handoff, frame_count)
    
    pipeline.set_state(Gst.State.PLAYING)
    bus = pipeline.get_bus()

    while True:
        msg = bus.timed_pop_filtered(100 * Gst.MSECOND, Gst.MessageType.ERROR | Gst.MessageType.EOS)
        if msg:
            if msg.type == Gst.MessageType.ERROR:
                err, _ = msg.parse_error()
                print(f"Ошибка воспроизведения: {err.message}")
                break
            elif msg.type == Gst.MessageType.EOS:
                break

    pipeline.set_state(Gst.State.NULL)
    
    t2 = time.time()
    process_time = t2 - t1

    metadata = get_video_metadata(video_path)
    info = parse_video_info(metadata)
    video_duration = info['duration']

    fps = frame_count[0] / process_time if process_time > 0 else 0
    speed = video_duration / process_time if process_time > 0 else 0

    return {
        'duration_ms': process_time * 1000,
        'frame_count': frame_count[0],
        'fps': fps,
        'speed': speed
    }

def decode_with_vaapi(video_path):
    t1 = time.time()

    pipeline_str = f"""
        filesrc location="{video_path}" !
        qtdemux !
        h264parse !
        vaapih264dec !
        video/x-raw !
        fakesink name=sink sync=false
    """

    print(f"Pipeline (VAAPI): {pipeline_str.strip()}")

    try:
        pipeline = Gst.parse_launch(pipeline_str)
    except GLib.Error as e:
        print(f"Ошибка создания pipeline (vaapih264dec): {e}")
        return {'duration_ms': 0, 'frame_count': 0, 'fps': 0, 'speed': 0}

    sink = pipeline.get_by_name("sink")
    frame_count = [0]

    def on_handoff(sink, buffer, pad, data):
        data[0] += 1

    sink.set_property("signal-handoffs", True)
    sink.connect("handoff", on_handoff, frame_count)

    pipeline.set_state(Gst.State.PLAYING)
    bus = pipeline.get_bus()

    while True:
        msg = bus.timed_pop_filtered(100 * Gst.MSECOND, Gst.MessageType.ERROR | Gst.MessageType.EOS)
        if msg:
            if msg.type == Gst.MessageType.ERROR:
                err, _ = msg.parse_error()
                print(f"Ошибка воспроизведения: {err.message}")
                break
            elif msg.type == Gst.MessageType.EOS:
                break

    pipeline.set_state(Gst.State.NULL)

    t2 = time.time()
    process_time = t2 - t1

    metadata = get_video_metadata(video_path)
    info = parse_video_info(metadata)
    video_duration = info['duration']

    fps = frame_count[0] / process_time if process_time > 0 else 0
    speed = video_duration / process_time if process_time > 0 else 0

    return {
        'duration_ms': process_time * 1000,
        'frame_count': frame_count[0],
        'fps': fps,
        'speed': speed
    }

def decode_with_avdec(video_path):
    t1 = time.time()

    pipeline_str = f"""
        filesrc location="{video_path}" !
        qtdemux !
        h264parse !
        avdec_h264 !
        fakesink name=sink sync=false
    """

    print(f"Pipeline (avdec_h264): {pipeline_str.strip()}")

    try:
        pipeline = Gst.parse_launch(pipeline_str)
    except GLib.Error as e:
        print(f"Ошибка создания pipeline (avdec_h264): {e}")
        return {'duration_ms': 0, 'frame_count': 0, 'fps': 0, 'speed': 0}

    sink = pipeline.get_by_name("sink")
    frame_count = [0]

    def on_handoff(sink, buffer, pad, data):
        data[0] += 1

    sink.set_property("signal-handoffs", True)
    sink.connect("handoff", on_handoff, frame_count)

    pipeline.set_state(Gst.State.PLAYING)
    bus = pipeline.get_bus()

    while True:
        msg = bus.timed_pop_filtered(100 * Gst.MSECOND, Gst.MessageType.ERROR | Gst.MessageType.EOS)
        if msg:
            if msg.type == Gst.MessageType.ERROR:
                err, _ = msg.parse_error()
                print(f"Ошибка воспроизведения: {err.message}")
                break
            elif msg.type == Gst.MessageType.EOS:
                break

    pipeline.set_state(Gst.State.NULL)

    t2 = time.time()
    process_time = t2 - t1

    metadata = get_video_metadata(video_path)
    info = parse_video_info(metadata)
    video_duration = info['duration']

    fps = frame_count[0] / process_time if process_time > 0 else 0
    speed = video_duration / process_time if process_time > 0 else 0

    return {
        'duration_ms': process_time * 1000,
        'frame_count': frame_count[0],
        'fps': fps,
        'speed': speed
    }


def main():
    video_path = "/home/mehroj/Coding/hardware-decoding/video/input.mp4"
    
    if not os.path.exists(video_path):
        print(f"Ошибка: файл {video_path} не найден.")
        return

    metadata = get_video_metadata(video_path)
    info = parse_video_info(metadata)

    print("\nИнформация о видео:")
    print(f"Кодек: {info['codec_name']}")
    print(f"Цветовое пространство: {info['pix_fmt']}")
    print(f"Продолжительность: {info['duration']} сек")

    print("\nДекодирование:")
    result = decode(video_path)
    print(f"Время декодирования: {result['duration_ms']:.2f} мс")
    print(f"Декодировано кадров: {result['frame_count']}")
    print(f"Средний FPS: {result['fps']:.1f}")
    print(f"Скорость: {result['speed']:.1f}x")

    print("\nVAAPI-декодирование:")
    vaapi_result = decode_with_vaapi(video_path)
    print(f"Время: {vaapi_result['duration_ms']:.2f} мс, FPS: {vaapi_result['fps']:.1f}, Скорость: {vaapi_result['speed']:.1f}x")

    print("\nПрограммное декодирование (avdec_h264):")
    avdec_result = decode_with_avdec(video_path)
    print(f"Время: {avdec_result['duration_ms']:.2f} мс, FPS: {avdec_result['fps']:.1f}, Скорость: {avdec_result['speed']:.1f}x")


if __name__ == "__main__":
    main()



"""
Информация о видео:
Кодек: h264
Цветовое пространство: ISO
Продолжительность: 316.047 сек

Декодирование:
Pipeline: filesrc location="/home/mehroj/Coding/hardware-decoding/video/input.mp4" !
        qtdemux !
        h264parse !
        nvh264dec !
        cudaconvert !
        fakesink name=sink sync=false
Время декодирования: 2354.40 мс
Декодировано кадров: 9470
Средний FPS: 4022.3
Скорость: 134.2x

VAAPI-декодирование:
Pipeline (VAAPI): filesrc location="/home/mehroj/Coding/hardware-decoding/video/input.mp4" !
        qtdemux !
        h264parse !
        vaapih264dec !
        video/x-raw !
        fakesink name=sink sync=false
DRM_IOCTL_I915_GEM_APERTURE failed: Invalid argument
Assuming 131072kB available aperture size.
May lead to reduced performance or incorrect rendering.
get chip id failed: -1 [22]
param: 4, val: 0
Время: 6630.94 мс, FPS: 1428.2, Скорость: 47.7x

Программное декодирование (avdec_h264):
Pipeline (avdec_h264): filesrc location="/home/mehroj/Coding/hardware-decoding/video/input.mp4" !
        qtdemux !
        h264parse !
        avdec_h264 !
        fakesink name=sink sync=false
Время: 19210.75 мс, FPS: 493.0, Скорость: 16.5x
"""