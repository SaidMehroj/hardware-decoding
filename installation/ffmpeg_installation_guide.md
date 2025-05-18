# 🚀 Руководство по сборке FFmpeg 4.4 с поддержкой CUDA, libx264, libx265 и других кодеков

Данное руководство описывает пошаговую установку FFmpeg 4.4 с поддержкой GPU-ускорения (CUDA/NVENC/NPP), а также необходимых кодеков и библиотек для полноценной работы мультимедийных приложений.

---

## 🔧 Шаг 1: Установка заголовков NVIDIA для кодеков

```bash
git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git
cd nv-codec-headers
sudo make install
cd -
```

Заголовки `nv-codec-headers` необходимы для поддержки NVIDIA NVENC/NVDEC в FFmpeg.

---

## 📦 Шаг 2: Создание рабочей директории и загрузка исходников FFmpeg

```bash
mkdir -p ~/ffmpeg_build && cd ~/ffmpeg_build
wget https://ffmpeg.org/releases/ffmpeg-4.4.tar.gz
tar xzf ffmpeg-4.4.tar.gz
cd ffmpeg-4.4
```

---

## 🧱 Шаг 3: Установка зависимостей

```bash
sudo apt-get install build-essential yasm cmake libtool \
    libc6 libc6-dev unzip wget libnuma1 libnuma-dev
```

Эти пакеты необходимы для компиляции FFmpeg и поддержки дополнительных библиотек.

---

## ⚙️ Шаг 4: Конфигурация сборки

```bash
./configure \
  --prefix=/usr \                                  # Путь установки
  --extra-version=0ubuntu0.22.04.1 \               # Суффикс версии для системы
  --toolchain=hardened \                           # Усиленная компиляция
  --libdir=/usr/lib/x86_64-linux-gnu \             # Расположение библиотек
  --incdir=/usr/include/x86_64-linux-gnu \         # Расположение заголовков
  --arch=amd64 \                                   # Архитектура системы
  --enable-gpl \                                   # Разрешить GPL-библиотеки (например, x264)
  --enable-ladspa \                                # Аудио плагины LADSPA
  --enable-libaom \                                # Поддержка кодека AV1 (AOM)
  --enable-libdav1d \                              # Поддержка декодера AV1 (dav1d)
  --enable-libfontconfig \                         # Работа с шрифтами
  --enable-libfreetype \                           # Рендеринг текста
  --enable-libopenjpeg \                           # JPEG 2000
  --enable-libpulse \                              # PulseAudio
  --enable-libsnappy \                             # Быстрое сжатие Snappy
  --enable-libssh \                                # Поддержка SSH
  --enable-libvpx \                                # VP8/VP9 кодеки
  --enable-libwebp \                               # Поддержка WebP
  --enable-libx265 \                               # HEVC (H.265)
  --enable-libxvid \                               # MPEG-4 ASP
  --enable-libzimg \                               # Цветовые преобразования
  --enable-omx \                                   # OpenMAX (ARM)
  --enable-opencl \                                # Поддержка OpenCL
  --enable-opengl \                                # Поддержка OpenGL
  --enable-sdl2 \                                  # Использование SDL2
  --enable-librsvg \                               # Отображение SVG
  --enable-libmfx \                                # Intel Media SDK (GPU-ускорение)
  --extra-cflags=-I/usr/include \                  # Доп. заголовки
  --enable-libdrm \                                # Direct Rendering Manager (GPU)
  --enable-libx264 \                               # H.264 кодек (x264)
  --enable-nonfree \                               # Несвободные библиотеки (x264/x265)
  --enable-cuda-nvcc \                             # Сборка с CUDA NVCC
  --enable-libnpp \                                # NVIDIA Performance Primitives
  --nvccflags="-gencode arch=compute_89,code=sm_89" \  # Архитектура RTX 4060
  --extra-cflags=-I/usr/local/cuda/include \       # CUDA заголовки
  --extra-ldflags=-L/usr/local/cuda/lib64 \        # CUDA библиотеки
  --disable-static \                               # Только динамические библиотеки
  --disable-x86asm \                               # Отключение ASM (при необходимости)
  --enable-shared                                  # Динамические библиотеки
```

---

## 🛠️ Шаг 5: Компиляция и установка

```bash
make -j$(nproc)
sudo make install
```

---

## ✅ Проверка

Проверьте версию установленного FFmpeg:

```bash
ffmpeg -hwaccels
```

Вы должны увидеть поддержку `cuda`, `nvenc`, `nvdec`, и другие аппаратные ускорения.

---

## 📌 Примечание

- Убедитесь, что `CUDA` установлен по пути `/usr/local/cuda`.
- Значение `compute_89` и `sm_89` указывается для GPU архитектуры Ada Lovelace (например, RTX 4060).
- Если у вас другой GPU, используйте соответствующую архитектуру (см. [NVIDIA CUDA GPUs](https://developer.nvidia.com/cuda-gpus)).

---
