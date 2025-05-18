# 🚀 Установка и сборка OpenCV 4.9.0 с поддержкой CUDA, cuDNN, VA-API и GStreamer

Данная инструкция предназначена для пользователей Linux, которые хотят собрать OpenCV 4.9.0 с поддержкой аппаратного ускорения и дополнительными модулями из `opencv_contrib`.

## 📦 Предварительные требования

Перед началом убедитесь, что у вас установлены следующие зависимости:

```bash
sudo apt update && sudo apt install -y \
  build-essential cmake git pkg-config \
  libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev \
  libv4l-dev libxvidcore-dev libx264-dev libjpeg-dev libpng-dev libtiff-dev \
  gfortran openexr libatlas-base-dev python3-dev python3-numpy \
  libtbb2 libtbb-dev libdc1394-22-dev libopenexr-dev \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  libva-dev libgtkglext1-dev qtbase5-dev
```

Также убедитесь, что установлены:

- CUDA Toolkit 12.2
- cuDNN (совместимая версия с CUDA)
- GStreamer (для поддержки видеоинтеграции)
- VA-API и Media SDK (Intel)

---

## 📥 Клонирование исходников

```bash
# Клонируем основное репо OpenCV
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout 4.9.0

# Клонируем дополнительные модули
cd ..
git clone https://github.com/opencv/opencv_contrib.git
cd opencv_contrib
git checkout 4.9.0
```

---

## 🏗️ Сборка OpenCV с поддержкой CUDA, cuDNN и других технологий

```bash
cd ../opencv
mkdir build
cd build
```

Теперь запускаем `cmake` с необходимыми флагами:

```bash
cmake \
  -D CMAKE_BUILD_TYPE=RELEASE \                # Режим сборки: RELEASE включает оптимизации
  -D CMAKE_INSTALL_PREFIX=/usr/local \         # Путь установки после make install
  -D INSTALL_C_EXAMPLES=ON \                   # Установить примеры на C++
  -D INSTALL_PYTHON_EXAMPLES=ON \              # Установить примеры на Python
  -D WITH_TBB=ON \                             # Включить поддержку Intel TBB (многопоточность)
  -D WITH_CUDA=ON \                            # Включить поддержку NVIDIA CUDA
  -D CUDA_ARCH_BIN=8.9 \                       # Целевая архитектура GPU (8.9 = RTX 4060)
  -D BUILD_opencv_cudacodec=ON \               # Собирать модуль для аппаратного декодирования видео на CUDA
  -D ENABLE_FAST_MATH=ON \                     # Использовать быстрые математические функции
  -D NVCUVID_FAST_MATH=ON \                    # (Опция CUDA) включить быстрые вычисления для NVCUVID
  -D CUDA_FAST_MATH=ON \                       # Включить быстрые математические функции CUDA
  -D WITH_CUBLAS=ON \                          # Использовать библиотеку CUBLAS (линейная алгебра от NVIDIA)
  -D WITH_VA=ON \                              # Включить поддержку VA-API (аппаратное ускорение на Intel GPU)
  -D WITH_MFX=ON \                             # Поддержка Intel Media SDK (libmfx)
  -D WITH_GTK=ON \                             # Использовать GTK для GUI (например, в imshow)
  -D BUILD_opencv_java=OFF \                   # Не собирать Java-bindings
  -D BUILD_ZLIB=ON \                           # Собирать встроенную поддержку Zlib
  -D BUILD_TIFF=ON \                           # Собирать встроенную поддержку TIFF
  -D WITH_NVCUVID=ON \                         # Включить поддержку NVIDIA CUVID
  -D WITH_FFMPEG=ON \                          # Включить поддержку FFMPEG (чтение/запись видеофайлов)
  -D CUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda-12.2 \  # Путь к установленному CUDA Toolkit
  -D WITH_1394=ON \                            # Поддержка IEEE1394 (FireWire камер)
  -D CUDNN_INCLUDE_DIR=/usr/local/cuda/include \   # Путь к заголовкам cuDNN
  -D CUDNN_LIBRARY=/usr/local/cuda/lib64/libcudnn.so.8.9.5 \  # Путь к библиотеке cuDNN
  -D OPENCV_GENERATE_PKGCONFIG=ON \            # Сгенерировать pkg-config файл
  -D OPENCV_PC_FILE_NAME=opencv4.pc \          # Имя pkg-config файла
  -D OPENCV_ENABLE_NONFREE=ON \                # Включить не-свободные модули (например, SIFT, SURF)
  -D WITH_GSTREAMER=ON \                       # Включить поддержку GStreamer
  -D WITH_V4L=ON \                              # Поддержка Video4Linux (камеры)
  -D WITH_QT=OFF \                              # Не использовать Qt (если используется GTK)
  -D WITH_CUDNN=ON \                            # Включить поддержку cuDNN в DNN модуле
  -D OPENCV_DNN_CUDA=ON \                       # Ускорение DNN (глубоких нейросетей) с CUDA
  -D WITH_OPENGL=ON \                           # Включить поддержку OpenGL (для отображения)
  -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \  # Путь к дополнительным модулям из opencv_contrib
  -D BUILD_EXAMPLES=ON ..                       # Собирать примеры из исходников
```

> 💡 **Примечание:** Проверьте корректность путей до `CUDA`, `cuDNN` и `opencv_contrib`. Путь `CUDA_ARCH_BIN=8.9` соответствует архитектуре RTX 4060.

---

## ⚙️ Сборка и установка

```bash
make -j$(nproc)    # Используем все доступные ядра процессора
sudo make install  # Устанавливаем OpenCV в систему
sudo ldconfig      # Обновляем кэш динамических библиотек
```

---

## ✅ Проверка установки

Проверьте установленную версию OpenCV:

```bash
pkg-config --modversion opencv4
```

Также можно проверить поддержку CUDA:

```bash
python3 -c "import cv2; print(cv2.getBuildInformation())"
```

---

## 📌 Завершение

Вы успешно собрали и установили OpenCV 4.9.0 с поддержкой:

- CUDA и cuDNN (ускорение на GPU)
- GStreamer (мультимедиа стриминг)
- VA-API / Intel Media SDK (аппаратное ускорение на Intel GPU)
- Дополнительные модули из `opencv_contrib`

---
