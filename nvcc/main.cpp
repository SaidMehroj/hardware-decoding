#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <mutex>
#include <queue>
#include <condition_variable>

#include <cuda.h>
#include "nvcuvid.h"
#include "cuviddec.h"

#define CUDA_CHECK(call) \
    do { \
        CUresult result = call; \
        if (result != CUDA_SUCCESS) { \
            const char* errName; \
            cuGetErrorName(result, &errName); \
            std::cerr << "CUDA error " << errName << " at " << __FILE__ << ":" << __LINE__ << std::endl; \
            exit(1); \
        } \
    } while (0)

struct VideoDecoder {
    CUcontext cuContext = nullptr;
    
    CUvideodecoder decoder = nullptr;
    CUvideoparser parser = nullptr;
    
    int frameCount = 0;
    int width = 0;
    int height = 0;
    
    std::mutex mutex;
    std::condition_variable condition;
    std::queue<int> frameQueue;
    bool endOfDecode = false;
};

static int CUDAAPI HandleVideoSequence(void* userData, CUVIDEOFORMAT* format) {
    VideoDecoder* decoder = static_cast<VideoDecoder*>(userData);
    
    decoder->width = format->coded_width;
    decoder->height = format->coded_height;
    
    CUVIDDECODECREATEINFO decodeInfo = {};
    decodeInfo.CodecType = format->codec;
    decodeInfo.ChromaFormat = format->chroma_format;
    decodeInfo.ulWidth = format->coded_width;
    decodeInfo.ulHeight = format->coded_height;
    decodeInfo.ulNumDecodeSurfaces = format->min_num_decode_surfaces;
    
    decodeInfo.OutputFormat = cudaVideoSurfaceFormat_NV12;
    decodeInfo.DeinterlaceMode = cudaVideoDeinterlaceMode_Weave;
    
    decodeInfo.ulTargetWidth = format->coded_width;
    decodeInfo.ulTargetHeight = format->coded_height;
    
    if (decoder->decoder) {
        CUDA_CHECK(cuvidDestroyDecoder(decoder->decoder));
    }
    
    CUDA_CHECK(cuvidCreateDecoder(&decoder->decoder, &decodeInfo));
    
    return format->min_num_decode_surfaces;
}

static int CUDAAPI HandlePictureDecode(void* userData, CUVIDPICPARAMS* picParams) {
    VideoDecoder* decoder = static_cast<VideoDecoder*>(userData);
    
    CUDA_CHECK(cuvidDecodePicture(decoder->decoder, picParams));
    
    return 1;
}

static int CUDAAPI HandlePictureDisplay(void* userData, CUVIDPARSERDISPINFO* dispInfo) {
    VideoDecoder* decoder = static_cast<VideoDecoder*>(userData);
    
    decoder->frameCount++;
    
    {
        std::lock_guard<std::mutex> lock(decoder->mutex);
        decoder->frameQueue.push(dispInfo->picture_index);
    }
    
    decoder->condition.notify_one();
    
    return 1;
}

int main() {
    const char* videoFilePath = "/home/mehroj/Coding/hardware-decoding/video/output.h264";
    VideoDecoder decoder;
    
    CUDA_CHECK(cuInit(0));
    
    CUdevice cuDevice;
    CUDA_CHECK(cuDeviceGet(&cuDevice, 0));
    
    char deviceName[128];
    CUDA_CHECK(cuDeviceGetName(deviceName, sizeof(deviceName), cuDevice));
    std::cout << "Используется GPU: " << deviceName << std::endl;
    
    CUDA_CHECK(cuCtxCreate(&decoder.cuContext, 0, cuDevice));
    
    CUVIDDECODECAPS decodeCaps = {};
    decodeCaps.eCodecType = cudaVideoCodec_H264;
    decodeCaps.eChromaFormat = cudaVideoChromaFormat_420;
    decodeCaps.nBitDepthMinus8 = 0;
    
    CUDA_CHECK(cuvidGetDecoderCaps(&decodeCaps));
    
    if (!decodeCaps.bIsSupported) {
        std::cerr << "Декодирование H.264 не поддерживается на этом GPU" << std::endl;
        return -1;
    }
    
    std::cout << "Максимальное разрешение: " << decodeCaps.nMaxWidth << "x" << decodeCaps.nMaxHeight << std::endl;
    
    CUVIDPARSERPARAMS parserParams = {};
    parserParams.CodecType = cudaVideoCodec_H264;
    parserParams.ulMaxNumDecodeSurfaces = 20;
    parserParams.ulMaxDisplayDelay = 1;
    parserParams.pUserData = &decoder;
    parserParams.pfnSequenceCallback = HandleVideoSequence;
    parserParams.pfnDecodePicture = HandlePictureDecode;
    parserParams.pfnDisplayPicture = HandlePictureDisplay;
    
    CUDA_CHECK(cuvidCreateVideoParser(&decoder.parser, &parserParams));
    
    std::ifstream videoFile(videoFilePath, std::ios::binary);
    if (!videoFile) {
        std::cerr << "Не удалось открыть файл: " << videoFilePath << std::endl;
        return -1;
    }
    
    videoFile.seekg(0, std::ios::end);
    size_t fileSize = videoFile.tellg();
    videoFile.seekg(0, std::ios::beg);
    
    constexpr size_t bufferSize = 1024 * 1024;
    std::vector<uint8_t> buffer(bufferSize);
    
    std::thread processingThread([&decoder]() {
        while (true) {
            int pictureIndex = -1;
            
            {
                std::unique_lock<std::mutex> lock(decoder.mutex);
                decoder.condition.wait(lock, [&decoder]() {
                    return !decoder.frameQueue.empty() || decoder.endOfDecode;
                });
                
                if (decoder.frameQueue.empty() && decoder.endOfDecode) {
                    break; 
                }
                
                pictureIndex = decoder.frameQueue.front();
                decoder.frameQueue.pop();
            }

        }
    });
    
    auto startTime = std::chrono::high_resolution_clock::now();
    
    CUVIDSOURCEDATAPACKET packet = {};
    size_t bytesRead = 0;
    
    while (videoFile) {
        videoFile.read(reinterpret_cast<char*>(buffer.data()), buffer.size());
        size_t bytesReadThisTime = videoFile.gcount();
        
        if (bytesReadThisTime == 0) {
            break;
        }
        
        bytesRead += bytesReadThisTime;
        
        packet.payload = buffer.data();
        packet.payload_size = static_cast<unsigned long>(bytesReadThisTime);
        packet.flags = 0;
        
        CUDA_CHECK(cuvidParseVideoData(decoder.parser, &packet));
    }
    
    packet.payload = nullptr;
    packet.payload_size = 0;
    packet.flags = CUVID_PKT_ENDOFSTREAM;
    
    CUDA_CHECK(cuvidParseVideoData(decoder.parser, &packet));
    
    {
        std::lock_guard<std::mutex> lock(decoder.mutex);
        decoder.endOfDecode = true;
    }
    decoder.condition.notify_one();
    
    processingThread.join();
    
    auto endTime = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime);
    
    std::cout << "Декодировано кадров: " << decoder.frameCount << std::endl;
    std::cout << "Размер видео: " << decoder.width << "x" << decoder.height << std::endl;
    std::cout << "Время декодирования: " << duration.count() << " мс" << std::endl;
    
    if (duration.count() > 0) {
        double fps = static_cast<double>(decoder.frameCount) * 1000.0 / duration.count();
        std::cout << "Производительность декодирования: " << fps << " кадров/с" << std::endl;
    }
    
    if (decoder.parser) {
        CUDA_CHECK(cuvidDestroyVideoParser(decoder.parser));
    }
    
    if (decoder.decoder) {
        CUDA_CHECK(cuvidDestroyDecoder(decoder.decoder));
    }
    
    CUDA_CHECK(cuCtxDestroy(decoder.cuContext));
    
    return 0;
}