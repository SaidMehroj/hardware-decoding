import time
import os
import re
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstPbutils', '1.0')
from gi.repository import Gst, GLib, GstPbutils

Gst.init(None)

def parse_video_info(video_path):
    default_result = {
        'codec_name': "unknown",
        'pix_fmt': "unknown",
        'duration': 0,
        'width': 0,
        'height': 0,
        'framerate': 0
    }
    
    try:
        if not os.path.exists(video_path):
            print(f"Ошибка3: Файл не найден: {video_path}")
            return default_result
        
        abs_path = os.path.abspath(video_path)
        
        timeout = 5 * Gst.SECOND
        discoverer = GstPbutils.Discoverer.new(timeout)
        file_uri = Gst.filename_to_uri(abs_path)
        
        info = discoverer.discover_uri(file_uri)
        
        codec_name = "unknown"
        pix_fmt = "unknown"
        duration_sec = info.get_duration() / Gst.SECOND
        width = 0
        height = 0
        framerate = 0
        
        video_streams = info.get_video_streams()
        if video_streams:
            video_stream = video_streams[0]
            caps = video_stream.get_caps().to_string()
            
            codec_match = re.search(r'video/x-([a-zA-Z0-9]+)', caps)
            if codec_match:
                codec_name = codec_match.group(1)
            
            format_match = re.search(r'format=\(string\)([a-zA-Z0-9]+)', caps)
            if format_match:
                pix_fmt = format_match.group(1)
            
            width = video_stream.get_width()
            height = video_stream.get_height()
            
            num = video_stream.get_framerate_num()
            denom = video_stream.get_framerate_denom()
            if denom > 0:
                framerate = num / denom
        
        return {
            'codec_name': codec_name,
            'pix_fmt': pix_fmt,
            'duration': duration_sec,
            'width': width,
            'height': height,
            'framerate': framerate
        }
    except GLib.Error as e:
        print(f"GStreamer ошибка: {e.message}")
        return default_result
    except Exception as e:
        print(f"Ошибка при парсинге информации о видео: {e}")
        return default_result

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

    info = parse_video_info(video_path)
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

    info = parse_video_info(video_path)
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

    info = parse_video_info(video_path)
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
        print(f"Ошибка1: файл {video_path} не найден.")
        return

    info = parse_video_info(video_path)

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
Цветовое пространство: avc
Продолжительность: 316.047 сек

Декодирование:
Pipeline: filesrc location="/home/mehroj/Coding/hardware-decoding/video/input.mp4" !
        qtdemux !
        h264parse !
        nvh264dec !
        cudaconvert !
        fakesink name=sink sync=false
Время декодирования: 2387.49 мс
Декодировано кадров: 9470
Средний FPS: 3966.5
Скорость: 132.4x

VAAPI-декодирование:
Pipeline (VAAPI): filesrc location="/home/mehroj/Coding/hardware-decoding/video/input.mp4" !
        qtdemux !
        h264parse !
        vaapih264dec !
        video/x-raw !
        fakesink name=sink sync=false
Время: 6884.27 мс, FPS: 1375.6, Скорость: 45.9x

Программное декодирование (avdec_h264):
Pipeline (avdec_h264): filesrc location="/home/mehroj/Coding/hardware-decoding/video/input.mp4" !
        qtdemux !
        h264parse !
        avdec_h264 !
        fakesink name=sink sync=false
Время: 12401.58 мс, FPS: 763.6, Скорость: 25.5x
"""