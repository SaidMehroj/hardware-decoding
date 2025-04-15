import ffmpeg
import numpy as np
import time
import re


def detect_video_format(video_path):
    probe = ffmpeg.probe(video_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    
    if not video_stream:
        raise ValueError("Не удалось найти видеопоток в файле")
    
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    
    pix_fmt = video_stream.get('pix_fmt', 'yuv420p')
    
    if 'avg_frame_rate' in video_stream:
        fps_str = video_stream['avg_frame_rate']
        if '/' in fps_str:
            num, den = map(int, fps_str.split('/'))
            fps = num / den if den != 0 else 0
        else:
            fps = float(fps_str)
    else:
        fps = 0
    
    return {
        'width': width,
        'height': height,
        'pix_fmt': pix_fmt,
        'fps': fps
    }


def decode_yuv420p(video_path,hwaccel_t,decoder_t ,only_keyframes=False):
    info = detect_video_format(video_path)
    width, height = info['width'], info['height']
    
    input_args = {
        'hwaccel': hwaccel_t,
        'c:v': decoder_t
    }
    
    if only_keyframes:
        input_args['skip_frame'] = 'nokey'
    
    output_args = {
        'format': 'rawvideo',
        'pix_fmt': 'yuv420p'
    }
    
    stream = ffmpeg.input(video_path, **input_args)
    stream = ffmpeg.output(stream, 'pipe:', **output_args)
    
    process = ffmpeg.run_async(stream, pipe_stdout=True, pipe_stderr=True)
    
    y_size = width * height
    uv_size = (width // 2) * (height // 2)
    frame_size = y_size + uv_size * 2
    frame_count = 0
    
    try:
        while True:
            in_bytes = process.stdout.read(frame_size)
            if not in_bytes or len(in_bytes) < frame_size:
                break
            
            y_data = in_bytes[:y_size]
            u_data = in_bytes[y_size:y_size + uv_size]
            v_data = in_bytes[y_size + uv_size:]
            
            y_plane = np.frombuffer(y_data, np.uint8).reshape((height, width))
            u_plane = np.frombuffer(u_data, np.uint8).reshape((height // 2, width // 2))
            v_plane = np.frombuffer(v_data, np.uint8).reshape((height // 2, width // 2))
            
            yuv_frame = {
                'y': y_plane,
                'u': u_plane,
                'v': v_plane,
                'format': 'yuv420p'
            }
            
            frame_count += 1
            yield yuv_frame
    
    finally:
        _finish_process(process, frame_count)


def decode_rgb24(video_path,hwaccel_t,decoder_t, only_keyframes=False):
    info = detect_video_format(video_path)
    width, height = info['width'], info['height']
    
    input_args = {
        'hwaccel': hwaccel_t,
        'c:v': decoder_t
    }
    
    if only_keyframes:
        input_args['skip_frame'] = 'nokey'
    
    output_args = {
        'format': 'rawvideo',
        'pix_fmt': 'rgb24'
    }
    
    stream = ffmpeg.input(video_path, **input_args)
    stream = ffmpeg.output(stream, 'pipe:', **output_args)
    
    process = ffmpeg.run_async(stream, pipe_stdout=True, pipe_stderr=True)
    
    bytes_per_pixel = 3
    frame_size = width * height * bytes_per_pixel
    frame_count = 0
    
    try:
        while True:
            in_bytes = process.stdout.read(frame_size)
            if not in_bytes or len(in_bytes) < frame_size:
                break
            
            frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 3])
            
            frame_count += 1
            yield {'data': frame, 'format': 'rgb24'}
    
    finally:
        _finish_process(process, frame_count)


def decode_rgba(video_path,hwaccel_t,decoder_t, only_keyframes=False):
    info = detect_video_format(video_path)
    width, height = info['width'], info['height']
    
    input_args = {
        'hwaccel': hwaccel_t,
        'c:v': decoder_t
    }
    
    if only_keyframes:
        input_args['skip_frame'] = 'nokey'
    
    output_args = {
        'format': 'rawvideo',
        'pix_fmt': 'rgba'
    }
    
    stream = ffmpeg.input(video_path, **input_args)
    stream = ffmpeg.output(stream, 'pipe:', **output_args)
    
    process = ffmpeg.run_async(stream, pipe_stdout=True, pipe_stderr=True)
    
    bytes_per_pixel = 4
    frame_size = width * height * bytes_per_pixel
    frame_count = 0
    
    try:
        while True:
            in_bytes = process.stdout.read(frame_size)
            if not in_bytes or len(in_bytes) < frame_size:
                break
            
            frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width, 4])
            
            frame_count += 1
            yield {'data': frame, 'format': 'rgba'}
    
    finally:
        _finish_process(process, frame_count)


def decode_gray(video_path,hwaccel_t,decoder_t, only_keyframes=False):
    info = detect_video_format(video_path)
    width, height = info['width'], info['height']
    
    input_args = {
        'hwaccel': hwaccel_t,
        'c:v': decoder_t
    }
    
    if only_keyframes:
        input_args['skip_frame'] = 'nokey'
    
    output_args = {
        'format': 'rawvideo',
        'pix_fmt': 'gray'
    }
    
    stream = ffmpeg.input(video_path, **input_args)
    stream = ffmpeg.output(stream, 'pipe:', **output_args)
    
    process = ffmpeg.run_async(stream, pipe_stdout=True, pipe_stderr=True)
    
    bytes_per_pixel = 1
    frame_size = width * height * bytes_per_pixel
    frame_count = 0
    
    try:
        while True:
            in_bytes = process.stdout.read(frame_size)
            if not in_bytes or len(in_bytes) < frame_size:
                break
            
            frame = np.frombuffer(in_bytes, np.uint8).reshape([height, width])
            
            frame_count += 1
            yield {'data': frame, 'format': 'gray'}
    
    finally:
        _finish_process(process, frame_count)


def _finish_process(process, frame_count):
    t_start = time.time()
    
    process.stdout.close()
    stderr = process.stderr.read()
    process.wait()
    
    duration_ms = (time.time() - t_start) * 1000
    
    stderr_output = stderr.decode('utf-8', errors='ignore')
    fps = 0
    speed = None
    
    progress_lines = []
    for line in stderr_output.split('\n'):
        if "frame=" in line and "fps=" in line:
            progress_lines.append(line)
    
    if progress_lines:
        last_line = progress_lines[-1]
        all_fps = re.findall(r'fps=([\d.]+)', last_line)
        all_speeds = re.findall(r'speed=\s*([\d.]+)x', last_line)
        fps = float(all_fps[-1]) if all_fps else None
        speed = float(all_speeds[-1]) if all_speeds else None
    
    print(f"Processed {frame_count} frames in {duration_ms:.2f}ms")
    print(f"FPS: {fps}, Speed: {speed}x")


def decode_video(video_path,hwaccel_t,decoder_t, target_format=None, only_keyframes=False):
    info = detect_video_format(video_path)
    if target_format is None:
        native_format = info['pix_fmt']
        
        if native_format == 'yuv420p':
            return decode_yuv420p(video_path,hwaccel_t,decoder_t, only_keyframes)
        elif native_format in ['rgb24', 'bgr24']:
            return decode_rgb24(video_path,hwaccel_t,decoder_t, only_keyframes)
        elif native_format in ['rgba', 'bgra']:
            return decode_rgba(video_path,hwaccel_t,decoder_t, only_keyframes)
        elif native_format == 'gray':
            return decode_gray(video_path,hwaccel_t,decoder_t, only_keyframes)
        else:
            return decode_rgb24(video_path,hwaccel_t,decoder_t, only_keyframes)
    else:
        if target_format == 'yuv420p':
            return decode_yuv420p(video_path,hwaccel_t,decoder_t, only_keyframes)
        elif target_format == 'rgb24':
            return decode_rgb24(video_path,hwaccel_t,decoder_t, only_keyframes)
        elif target_format == 'rgba':
            return decode_rgba(video_path,hwaccel_t,decoder_t, only_keyframes)
        elif target_format == 'gray':
            return decode_gray(video_path,hwaccel_t,decoder_t, only_keyframes)
        else:
            raise ValueError(f"Неподдерживаемый формат: {target_format}")

def main():
    video_path = "/home/mehroj/Coding/hardware-decoding/video/input.mp4"
    
    format_type = ""

    print("CUDA декодирование")
    for frame in decode_video(video_path,'cuda','h264_cuvid'):
        format_type = frame.get('format')

    print("\nIntel GPU декодирование")
    for frame in decode_video(video_path,'vaapi','h264'):
        format_type = frame.get('format')    

    print("\nCPU декодирование")
    for frame in decode_video(video_path,'none','h264'):
        format_type = frame.get('format') 


    print(f"format_type: {format_type}")


main()    


"""
CUDA декодирование
Processed 9470 frames in 0.08ms
FPS: 3350.0, Speed: 112.0x

Intel GPU декодирование
Processed 9470 frames in 0.06ms
FPS: 2006.0, Speed: 66.9x

CPU декодирование
Processed 9470 frames in 0.05ms
FPS: 2452.0, Speed: 81.8x
format_type: yuv420p
"""