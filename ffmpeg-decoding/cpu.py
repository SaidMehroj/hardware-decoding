import subprocess
import time
import os
import re

def decode(video_path):
    t1 = time.time()
    
    cmd = [
        'ffmpeg',
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
    print(f"Скорость: {result['speed']}")

if __name__ == "__main__":
    main()


"""
Итоговые результаты:
Время декодирования: 18387.01 мс
Декодировано кадров: 9470
Средний FPS: 520
Скорость: 17.3
"""    