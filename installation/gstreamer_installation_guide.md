# 🎥 Установка и сборка GStreamer с поддержкой NVENC/NVDEC и VAAPI

Данное руководство описывает, как собрать `gst-plugins-bad` с поддержкой `nvcodec` (CUDA/NVENC) и `vaapi` на Linux.

---

## 📦 Шаг 1: Установка зависимостей

```bash
sudo apt install \
  build-essential meson ninja-build \
  libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
  libx11-dev libxext-dev \
  libva-x11-2 \
  gstreamer1.0-tools gstreamer1.0-gl gstreamer1.0-libav
```

Эти пакеты необходимы для сборки и использования GStreamer с графическими и мультимедийными возможностями.

---

## 🔽 Шаг 2: Клонирование исходников `gst-plugins-bad`

```bash
git clone https://gitlab.freedesktop.org/gstreamer/gst-plugins-bad.git -b 1.20.3
cd gst-plugins-bad
```

Загружается версия `1.20.3` плагинов GStreamer, которая содержит поддержку NVDEC/NVENC.

---

## ⚙️ Шаг 3: Конфигурация сборки с Meson

```bash
meson setup build \
  --prefix=/usr \
  -Dnvcodec=enabled \
  -Dc_args="-I/usr/local/cuda/include" \
  -Dc_link_args="-L/usr/local/cuda/lib64"
```

**Комментарии к параметрам:**
- `--prefix=/usr`: установка будет выполнена в системный путь.
- `-Dnvcodec=enabled`: включение поддержки кодеков NVIDIA (NVDEC/NVENC).
- `-Dc_args`: передача флага для компиляции с заголовками CUDA.
- `-Dc_link_args`: передача флага для линковки с библиотеками CUDA.

---

## 🛠️ Шаг 4: Сборка и установка

```bash
ninja -C build
sudo ninja -C build install
```

---

## ✅ Шаг 5: Проверка наличия плагинов

```bash
gst-inspect-1.0 nvcodec
gst-inspect-1.0 nvh264dec
gst-inspect-1.0 vaapi
```

Эти команды должны показать информацию о соответствующих плагинах, если они были успешно установлены.

---

## 📝 Примечания

- Убедитесь, что CUDA Toolkit установлен и доступен по пути `/usr/local/cuda`.
- Для работы с `vaapi` также должен быть установлен драйвер Intel (например, `intel-media-va-driver`).
- Для успешного использования `nvh264dec`, необходимы заголовки `nv-codec-headers` и поддержка CUDA на уровне драйвера NVIDIA.

---
