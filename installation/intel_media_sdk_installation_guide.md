# 📦 Установка Intel Media SDK (libmfx) и oneVPL + настройка среды

Это руководство включает установку:

- Intel Media SDK (библиотека аппаратного ускорения `libmfx`)
- OneVPL (современная реализация Intel Video Processing Library)
- Драйверов VA-API
- Переменных окружения

---

## 🔄 Шаг 1: Обновление системы и установка зависимостей

```bash
sudo apt update
sudo apt install -y cmake build-essential pkg-config libva-dev libdrm-dev
```

---

## 💻 Шаг 2: Установка драйвера Intel VAAPI (проприетарного)
```bash
sudo apt install -y intel-media-va-driver-non-free
```
Этот драйвер позволяет использовать Intel GPU для аппаратного ускорения видео через VAAPI.

## 📥 Шаг 3: Клонирование и сборка Intel Media SDK
```bash
git clone https://github.com/Intel-Media-SDK/MediaSDK.git
cd MediaSDK
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```
После установки libmfx будет доступна в /opt/intel/mediasdk.

## 📥 Шаг 4: Установка oneVPL
```bash
git clone https://github.com/oneapi-src/oneVPL.git
cd oneVPL
mkdir build && cd build
cmake ..
make -j$(nproc)
sudo make install
```
OneVPL — это продолжение Intel Media SDK, поддерживающее современные архитектуры (Xe, ARC и др.). Его можно использовать совместно с VAAPI и другими библиотеками.

## 🔍 Шаг 5: Проверка доступности VAAPI
```bash
sudo apt install vainfo
vainfo
```
Команда vainfo выводит список доступных аппаратных ускорений (VAAPI устройств и кодеков).

## 📁 Шаг 6: Проверка наличия pkg-config файлов
```bash
ls /opt/intel/mediasdk/lib/pkgconfig/
```
Ожидаемые файлы:

```bash
libmfxhw64.pc

libmfx.pc

mfx.pc
```
## ⚙️ Шаг 7: Настройка переменной окружения PKG_CONFIG_PATH
Добавьте путь к .pc-файлам в .bashrc:

```bash
vim ~/.bashrc
Добавьте строку:
```
```bash
export PKG_CONFIG_PATH=/opt/intel/mediasdk/lib/pkgconfig/
```
Примените изменения:

```bash
source ~/.bashrc
```

## ✅ Готово!
Теперь и pkg-config, и сборочные системы (CMake, Meson и др.) смогут находить библиотеки:
```bash
libmfx (Intel Media SDK)

oneVPL
```
Обе библиотеки пригодятся при сборке и запуске мультимедийных приложений с аппаратным ускорением (GStreamer, FFmpeg, OpenCV и др.).