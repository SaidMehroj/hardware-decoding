import subprocess
import time
import os
import re

def decode(video_path):
    t1 = time.time()
    
    cmd = [
        'ffmpeg',
        '-hwaccel', 'vaapi',              
        '-c:v', 'h264',            
        '-i', video_path,              
        '-f', 'null',                   
        '-'                 
    ]
    
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
    video_time=""
    speed=""
    
    for line in stderr_output.split('\n'):
        if "frame=" in line and "fps=" in line:
            match = re.search(r'fps=(\d+)', line)
            if match:
                fps = match.group(1)
            match = re.search(r'frame= (\d+)', line)
            if match:
                frame_count = match.group(1)
            match = re.search(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})', line)
            if match:
                video_time = match.group(1)
            match = re.search(r'speed=(\d+\.\d+)', line)
            if match:
                speed = match.group(1)                                                
    
    return {
        'duration_ms': duration_ms,
        'frame_count': frame_count,
        'fps': fps,
        'video_time': video_time,
        'speed': speed
    }

def main():
    video_path = "/home/mehroj/Coding/hardware-decoding/video/input.mp4"
    
    if not os.path.exists(video_path):
        print(f"Ошибка: файл {video_path} не найден.")
        return
    
    result = decode(video_path)
    
    print("\nИтоговые результаты:")
    print(f"Время декодирования: {result['duration_ms']:.2f} мс")
    print(f"Декодировано кадров: {result['frame_count']}")
    print(f"Средний FPS: {result['fps']}")
    print(f"Продолжительность видео: {result['video_time']}")
    print(f"Скорость: {result['speed']}")

if __name__ == "__main__":
    main()

"""
Итоговые результаты:
Время декодирования: 6891.64 мс
Декодировано кадров: 9470
Средний FPS: 1409
Продолжительность видео: 00:05:15.98
Скорость: 34.4
"""    