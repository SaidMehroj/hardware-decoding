# 📦 Установка CUDA Toolkit 12.2, cuDNN 8.9.5 и Nvidia Video Codec SDK 11.1

Это руководство поможет вам установить и настроить следующие компоненты:

- **CUDA Toolkit 12.2** — набор инструментов для работы с GPU от NVIDIA.
- **cuDNN 8.9.5** — библиотека для ускорения вычислений на GPU с использованием CUDA.
- **Nvidia Video Codec SDK 11.1** — набор библиотек для аппаратного декодирования и кодирования видео с использованием GPU NVIDIA.

---

## 🔄 Шаг 1: Обновление системы и установка зависимостей

Перед установкой CUDA и других компонентов обновите систему и установите необходимые зависимости:

```bash
sudo apt update
sudo apt install -y build-essential pkg-config cmake libtool libc6 libc6-dev unzip wget
```

## 💻 Шаг 2: Установка CUDA Toolkit 12.2 (через `.deb` пакет)

### 🔹 2.1 Загрузка и установка pin-файла

Для контроля приоритетов репозиториев загрузите pin-файл:

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
```

Переместите его в директорию предпочтений apt:

```bash
sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
```

### 🔹 2.2 Загрузка и установка .deb пакета CUDA Toolkit 12.2
Загрузите установочный .deb файл:

```bash
wget https://developer.download.nvidia.com/compute/cuda/12.2.0/local_installers/cuda-repo-ubuntu2204-12-2-local_12.2.0-530.30.02-1_amd64.deb
```
Установите репозиторий:

```bash
sudo dpkg -i cuda-repo-ubuntu2204-12-2-local_12.2.0-530.30.02-1_amd64.deb
```
Скопируйте ключи репозитория:

```bash
sudo cp /var/cuda-repo-ubuntu2204-12-2-local/cuda-*-keyring.gpg /usr/share/keyrings/
```

### 🔹 2.3 Обновление и установка CUDA Toolkit
Обновите индекс пакетов:

```bash
sudo apt update
```
Установите CUDA Toolkit 12.2:

```bash
sudo apt install -y cuda-toolkit-12-2
```
### 🔹 2.4 Настройка переменных окружения
Добавьте в .bashrc пути к CUDA Toolkit:

```bash
echo 'export PATH=/usr/local/cuda-12.2/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.2/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```
### 🔹 2.5 Перезагрузка системы
Чтобы завершить установку, перезагрузите систему:

```bash
sudo reboot
```
### 🔹 2.6 Проверка установки CUDA
После перезагрузки проверьте версию CUDA:

```bash
nvcc --version
```
Ожидаемый результат должен содержать информацию о версии release 12.2.

## 🧠 Шаг 3: Установка cuDNN 8.9.5
### 🔹 3.1 Скачивание cuDNN
Перейдите на сайт NVIDIA cuDNN и скачайте соответствующий архив для версии CUDA 12.2 и cuDNN 8.9.5.

### 🔹 3.2 Установка cuDNN
После скачивания архива распакуйте его и переместите в соответствующие каталоги:

```bash
tar -xzvf cudnn-12.2-linux-x64-v8.9.5.0.tgz
sudo cp cuda/include/cudnn*.h /usr/local/cuda/include
sudo cp cuda/lib64/libcudnn* /usr/local/cuda/lib64
sudo chmod a+r /usr/local/cuda/include/cudnn*.h /usr/local/cuda/lib64/libcudnn*
```
### 🔹 3.3 Проверка установки cuDNN
Для проверки правильности установки выполните команду:

```bash
dpkg -l | grep cudnn
```

## 🎥 Шаг 4: Установка Nvidia Video Codec SDK 11.1

### 🔹 4.1 Скачивание Nvidia Video Codec SDK 11.1

Перейдите на сайт [NVIDIA Video Codec SDK](https://developer.nvidia.com/nvidia-video-codec-sdk) и скачайте архив SDK 11.1.

### 🔹 4.2 Установка SDK

Распакуйте архив и переместите его содержимое в нужную директорию:

```bash
tar -xvzf NVIDIA_Video_Codec_SDK_11.1.0_Linux.tar.gz
sudo mv NVIDIA_Video_Codec_SDK /usr/local/
```

### 🔹 4.3 Перемещение заголовочных файлов в папку CUDA
Для правильной работы с CUDA, переместите заголовочные файлы из SDK в папку CUDA. Это нужно для того, чтобы CUDA смогла найти нужные файлы при компиляции.

```bash
sudo cp /usr/local/NVIDIA_Video_Codec_SDK/include/* /usr/local/cuda/include/
```
### 🔹 4.4 Настройка переменной окружения для Video Codec SDK
Добавьте путь к SDK в .bashrc:

```bash
echo 'export NV_CODEC_SDK=/usr/local/NVIDIA_Video_Codec_SDK' >> ~/.bashrc
source ~/.bashrc
```
### 🔹 4.5 Проверка установки
Для проверки, что SDK установлен корректно, выполните:

```bash
ls $NV_CODEC_SDK
```
Вы должны увидеть список директорий и файлов SDK, включая примеры и библиотеки.
