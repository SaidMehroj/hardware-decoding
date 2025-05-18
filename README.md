# Аппаратное декодирование сжатого видео 🚀

Проект разработан в рамках выпускной квалификационной работы (ВКР) в Таджикском филиале МГУ им. М. В. Ломоносова.  
**Научный руководитель**: Шокуров Антон Вячеславович ([ti.math.msu.su](http://ti.math.msu.su/), [машинноезрение.рф](http://машинноезрение.рф)).

Работа посвящена исследованию и разработке системы аппаратного декодирования сжатого видео с использованием специализированных аппаратных решений для оптимизации производительности. Проект демонстрирует эффективное декодирование видеопотоков с акцентом на снижение нагрузки на процессор и ускорение обработки.

## 📖 Описание

Проект реализует и сравнивает подходы к аппаратному декодированию сжатого видео с использованием современных технологий и библиотек. Он включает примеры декодирования с применением GPU (NVIDIA, Intel) и CPU, а также интеграцию мультимедийных фреймворков.

**Применение**:  
- 📺 Разработка высокопроизводительных приложений для стриминга, видеонаблюдения и видеоконференций.  
- 🔍 Исследование производительности аппаратного декодирования на различных платформах.  
- 🖼️ Интеграция в проекты компьютерного зрения для эффективной обработки видеопотоков.  
- 📚 Декодированные изображения можно подавать на вход нейронным сетям.

## 🛠️ Стек технологий

- **Языки**: Python 🐍, C++ 💻  
- **Библиотеки и SDK**:  
  - NVIDIA Video Codec SDK  
  - Intel Media SDK  
  - FFmpeg  
  - OpenCV  
  - GStreamer

## ⚙️ Установка и использование

### Установка
Инструкции по настройке окружения находятся в папке [installation/](installation/):  
- [`cuda_installation_guide.md`](installation/cuda_installation_guide.md) — установка NVIDIA CUDA и Video Codec SDK.  
- [`ffmpeg_installation_guide.md`](installation/ffmpeg_installation_guide.md) — установка FFmpeg с поддержкой аппаратного декодирования.  
- [`gstreamer_installation_guide.md`](installation/gstreamer_installation_guide.md) — установка GStreamer и плагинов.  
- [`intel_media_sdk_installation_guide.md`](installation/intel_media_sdk_installation_guide.md) — установка Intel Media SDK.  
- [`opencv_installation_guide.md`](installation/opencv_installation_guide.md) — установка OpenCV с поддержкой GPU и CPU.  

Следуйте этим руководствам для корректной установки зависимостей.

### Использование
Проект включает готовые функции для декодирования видео:  
- [`gstreamer/decode.py`](gstreamer/decode.py) — декодирование с GStreamer (Python).  
- [`nvcc/main.cpp`](nvcc/main.cpp) — декодирование с NVIDIA Video Codec SDK (C++).  
- [`intel/main.cpp`](intel/main.cpp) — декодирование с Intel Media SDK (C++).  
- [`ffmpeg-decoding/decode.py`](ffmpeg-decoding/decode.py) — декодирование с FFmpeg (Python).  
- [`opencv-decoding/gpu_nvidia.py`](opencv-decoding/gpu_nvidia.py) — декодирование с OpenCV на GPU NVIDIA (Python).  
- [`opencv-decoding/cpu.py`](opencv-decoding/cpu.py) — декодирование с OpenCV на CPU (Python).  
- [`opencv-decoding/gpu_intel.py`](opencv-decoding/gpu_intel.py) — декодирование с OpenCV на GPU Intel (Python).  

Для запуска скриптов следуйте инструкциям в соответствующих файлах и убедитесь, что все зависимости установлены.