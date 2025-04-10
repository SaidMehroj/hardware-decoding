import subprocess
import time
import os
import re

def decode(video_path, only_keyframes=False, color_format=None):
    t1 = time.time()
    
    cmd = [
        'ffmpeg',
        '-hwaccel', 'cuda',              
        '-c:v', 'h264_cuvid'
    ]
    
    if only_keyframes:
        cmd.extend(['-skip_frame', 'nokey'])
        
    cmd.extend(['-i', video_path])
    
    if color_format:
        cmd.extend(['-pix_fmt', color_format])
    
    cmd.extend(['-f', 'null', '-'])
    
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    stdout, stderr = process.communicate()
    
    t2 = time.time()
    
    duration_ms = (t2 - t1) * 1000
    
    stderr_output = stderr.decode('utf-8', errors='ignore')
    
    frame_count = 0
    fps = 0
    speed = ""

    progress_lines = []
    for line in stderr_output.split('\n'):
        if "frame=" in line and "fps=" in line:
            progress_lines.append(line)

    if progress_lines:
        last_line = progress_lines[-1]
        all_frames = re.findall(r'frame=\s*(\d+)', last_line)
        all_fps = re.findall(r'fps=([\d.]+)', last_line)
        all_speeds = re.findall(r'speed=\s*([\d.]+)x', last_line)

        frame_count = int(all_frames[-1]) if all_frames else None
        fps = float(all_fps[-1]) if all_fps else None
        speed = float(all_speeds[-1]) if all_speeds else None                               
    
    return {
        'duration_ms': duration_ms,
        'frame_count': frame_count,
        'fps': fps,
        'speed': speed
    }

def count_keyframes(video_path):
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-select_streams', 'v:0',
        '-show_entries', 'frame=pict_type',
        '-of', 'csv=p=0',
        video_path
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    frame_types = stdout.decode('utf-8').split('\n')
    key_frames = frame_types.count('I')
    
    return key_frames

def get_video_info(video_path):
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    import json
    video_info = json.loads(stdout.decode('utf-8'))
    
    video_stream = None
    for stream in video_info.get('streams', []):
        if stream.get('codec_type') == 'video':
            video_stream = stream
            break
    
    return {
        'format': video_info.get('format', {}),
        'video_stream': video_stream
    }

def main():
    video_path = "/home/mehroj/Coding/hardware-decoding/video/input.mp4"
    
    if not os.path.exists(video_path):
        print(f"Ошибка: файл {video_path} не найден.")
        return
    
    info = get_video_info(video_path)
    if info['video_stream']:
        print("\nИнформация о видео:")
        print(f"Кодек: {info['video_stream'].get('codec_name')}")
        print(f"Разрешение: {info['video_stream'].get('width')}x{info['video_stream'].get('height')}")
        print(f"Цветовое пространство: {info['video_stream'].get('pix_fmt')}")
        print(f"Общая продолжительность: {info['format'].get('duration')} сек")
    
    key_frames = count_keyframes(video_path)
    print(f"\nКоличество ключевых кадров (I-frames): {key_frames}")
    
    print("\nОбычное декодирование:")
    result = decode(video_path)
    print(f"Время декодирования: {result['duration_ms']:.2f} мс")
    print(f"Декодировано кадров: {result['frame_count']}")
    print(f"Средний FPS: {result['fps']}")
    print(f"Скорость: {result['speed']}")
    
    print("\nДекодирование только ключевых кадров:")
    result_key = decode(video_path, only_keyframes=True)
    print(f"Время декодирования: {result_key['duration_ms']:.2f} мс")
    print(f"Декодировано кадров: {result_key['frame_count']}")
    print(f"Средний FPS: {result_key['fps']}")
    print(f"Скорость: {result_key['speed']}")
    
    print("\nДекодирование с цветовым форматом yuv420p:")
    result_color = decode(video_path, color_format="yuv420p")
    print(f"Время декодирования: {result_color['duration_ms']:.2f} мс")
    print(f"Декодировано кадров: {result_color['frame_count']}")
    print(f"Средний FPS: {result_color['fps']}")
    print(f"Скорость: {result_color['speed']}")

if __name__ == "__main__":
    main()


"""
Информация о видео:
Кодек: h264
Разрешение: 640x360
Цветовое пространство: yuv420p
Общая продолжительность: 316.047000 сек

Количество ключевых кадров (I-frames): 120

Обычное декодирование:
Время декодирования: 7171.66 мс
Декодировано кадров: 9470
Средний FPS: 1377.0
Скорость: 46.0

Декодирование только ключевых кадров:
Время декодирования: 7500.27 мс
Декодировано кадров: 9470
Средний FPS: 1337.0
Скорость: 44.6

Декодирование с цветовым форматом yuv420p:
Время декодирования: 13387.79 мс
Декодировано кадров: 9470
Средний FPS: 724.0
Скорость: 24.2
"""    