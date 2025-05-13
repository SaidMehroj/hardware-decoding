#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <memory>
#include <string>
#include <vpl/mfxvideo.h>
#include <va/va.h>
#include <va/va_drm.h>
#include <fcntl.h>
#include <unistd.h>
#include <cstring>

struct DecoderContext {
    mfxSession session;
    mfxBitstream bitstream;
    std::vector<mfxFrameSurface1*> surfaces;
    mfxVideoParam videoParams;
    int fd_va_display;
    VADisplay va_display;
    
    DecoderContext() : session(nullptr), fd_va_display(-1), va_display(nullptr) {
        memset(&bitstream, 0, sizeof(bitstream));
        memset(&videoParams, 0, sizeof(videoParams));
    }
    
    ~DecoderContext() {
        for (auto& surface : surfaces) {
            if (surface) {
                delete[] surface->Data.Y;
                delete surface;
            }
        }
        
        if (bitstream.Data)
            delete[] bitstream.Data;
            
        if (session)
            MFXClose(session);
            
        if (va_display)
            vaTerminate(va_display);
            
        if (fd_va_display >= 0)
            close(fd_va_display);
    }
};

mfxStatus InitVADisplay(DecoderContext& ctx) {    
    ctx.fd_va_display = open("/dev/dri/renderD128", O_RDWR);
    if (ctx.fd_va_display < 0) {
        std::cout<<"Не удалось открыть /dev/dri/renderD128. Проверьте права доступа."<<std::endl;
        return MFX_ERR_DEVICE_FAILED;
    }
    
    ctx.va_display = vaGetDisplayDRM(ctx.fd_va_display);
    if (!ctx.va_display) {
        std::cout<<"Не удалось получить VA Display"<< std::endl;
        return MFX_ERR_DEVICE_FAILED;
    }
    
    int major, minor;
    VAStatus va_status = vaInitialize(ctx.va_display, &major, &minor);
    if (VA_STATUS_SUCCESS != va_status) {
        std::cout<<"Не удалось инициализировать VA-API: " << va_status<< std::endl;
        return MFX_ERR_DEVICE_FAILED;
    }
    
    return MFX_ERR_NONE;
}

mfxStatus CreateDecoderSession(DecoderContext& ctx) {
    mfxStatus sts = MFX_ERR_NONE;
    
    mfxVersion version = {0, 1};

    mfxIMPL impl = MFX_IMPL_HARDWARE | MFX_IMPL_VIA_VAAPI;
    
    sts = MFXInit(impl, &version, &ctx.session);
    
    if (sts != MFX_ERR_NONE) {
        std::cout<<"Не удалось инициализировать сессию, пробую другую реализацию"<< std::endl;
        impl = MFX_IMPL_HARDWARE;
        sts = MFXInit(impl, &version, &ctx.session);
    }
             
    return MFX_ERR_NONE;
}

mfxStatus InitDecoder(DecoderContext& ctx, const std::string& inputFile, mfxU32 codecId) {
    mfxStatus sts = MFX_ERR_NONE;
    
    sts = InitVADisplay(ctx);
    
    sts = CreateDecoderSession(ctx);
    
    sts = MFXVideoCORE_SetHandle(ctx.session, MFX_HANDLE_VA_DISPLAY, ctx.va_display);
    
    ctx.bitstream.MaxLength = 16 * 1024 * 1024;
    ctx.bitstream.Data = new mfxU8[ctx.bitstream.MaxLength];
    ctx.bitstream.DataOffset = 0;
    ctx.bitstream.DataLength = 0;
    
    
    std::ifstream inputFileStream(inputFile, std::ios::binary);
    if (!inputFileStream.is_open()) {
        std::cout<<"Не удалось открыть входной файл"<< std::endl;
        return MFX_ERR_NOT_FOUND;
    }
    
    inputFileStream.read(reinterpret_cast<char*>(ctx.bitstream.Data), ctx.bitstream.MaxLength);
    ctx.bitstream.DataLength = static_cast<mfxU32>(inputFileStream.gcount());
    inputFileStream.close();
    
    memset(&ctx.videoParams, 0, sizeof(ctx.videoParams));
    ctx.videoParams.mfx.CodecId = codecId;
    ctx.videoParams.IOPattern = MFX_IOPATTERN_OUT_SYSTEM_MEMORY;
    
    sts = MFXVideoDECODE_DecodeHeader(ctx.session, &ctx.bitstream, &ctx.videoParams);
    
    ctx.videoParams.mfx.FrameInfo.FourCC = MFX_FOURCC_NV12;
    ctx.videoParams.mfx.FrameInfo.ChromaFormat = MFX_CHROMAFORMAT_YUV420;
    
    sts = MFXVideoDECODE_Init(ctx.session, &ctx.videoParams);
    
    mfxFrameInfo& info = ctx.videoParams.mfx.FrameInfo;
    mfxU16 width = (info.CropW > 0) ? info.CropW : info.Width;
    mfxU16 height = (info.CropH > 0) ? info.CropH : info.Height;
    
    mfxU16 numSurfaces = 16;
    for (int i = 0; i < numSurfaces; i++) {
        mfxFrameSurface1* surface = new mfxFrameSurface1;
        memset(surface, 0, sizeof(mfxFrameSurface1));
        
        surface->Info = info;
        
        mfxU16 pitch = width;
        mfxU32 bufferSize = pitch * height * 3 / 2;
        surface->Data.Y = new mfxU8[bufferSize];
        surface->Data.UV = surface->Data.Y + pitch * height;
        surface->Data.Pitch = pitch;
        
        ctx.surfaces.push_back(surface);
    }
    
    return MFX_ERR_NONE;
}

mfxStatus DecodeVideo(DecoderContext& ctx, const std::string& inputFile) {
    mfxStatus sts = MFX_ERR_NONE;
    
    struct DecodingStats {
        int totalFrames;
        std::chrono::microseconds totalDecodingTime;
        
        DecodingStats() : totalFrames(0), 
                         totalDecodingTime(0) {}
    } stats;
    
    std::ifstream inputFileStream(inputFile, std::ios::binary);
    if (!inputFileStream.is_open()) {
        std::cout<<"Не удалось открыть входной файл"<<std::endl;
        return MFX_ERR_NOT_FOUND;
    }
    
    ctx.bitstream.DataOffset = 0;
    ctx.bitstream.DataLength = 0;
    
    inputFileStream.read(reinterpret_cast<char*>(ctx.bitstream.Data), ctx.bitstream.MaxLength);
    ctx.bitstream.DataLength = static_cast<mfxU32>(inputFileStream.gcount());
    
    mfxSyncPoint syncPoint;
    mfxFrameSurface1* workSurface = nullptr;
    
    while (true) {
        if (ctx.bitstream.DataLength == 0) {
            std::cout<<"Конец файла достигнут"<< std::endl;
            break;
        }

        int surfaceIndex = -1;
        for (size_t i = 0; i < ctx.surfaces.size(); i++) {
            if (ctx.surfaces[i]->Data.Locked == 0) {
                surfaceIndex = static_cast<int>(i);
                break;
            }
        }
        
        if (surfaceIndex == -1) {
            std::cout<<"Ожидание освобождения поверхностей..."<< std::endl;
            continue;
        }
        
        workSurface = ctx.surfaces[surfaceIndex];
        
        auto frameStartTime = std::chrono::high_resolution_clock::now();
        
        sts = MFXVideoDECODE_DecodeFrameAsync(ctx.session, &ctx.bitstream, 
                                             workSurface, &workSurface, &syncPoint);
        
        if (sts == MFX_ERR_MORE_DATA) {
            if (ctx.bitstream.DataOffset > 0) {
                mfxU32 remainingSize = ctx.bitstream.DataLength;
                memmove(ctx.bitstream.Data, ctx.bitstream.Data + ctx.bitstream.DataOffset, remainingSize);
                ctx.bitstream.DataOffset = 0;
                ctx.bitstream.DataLength = remainingSize;
            }
            
            mfxU32 availableSize = ctx.bitstream.MaxLength - ctx.bitstream.DataLength;
            
            inputFileStream.read(reinterpret_cast<char*>(ctx.bitstream.Data + ctx.bitstream.DataLength), availableSize);
            ctx.bitstream.DataLength += static_cast<mfxU32>(inputFileStream.gcount());
            
            if (inputFileStream.gcount() == 0 && ctx.bitstream.DataLength == 0) {
                std::cout<<"Конец файла и нет данных для обработки"<< std::endl;
                break;
            }
            
            continue;
        } else if (sts == MFX_ERR_MORE_SURFACE) {
            std::cout<<"Требуется другая поверхность"<< std::endl;
            continue;
        } else if (sts < 0) {
            std::cout<<"Ошибка декодирования: " << sts<< std::endl;
            if (sts != MFX_ERR_MORE_DATA)
                break;
        }
        
        if (syncPoint) {
            sts = MFXVideoCORE_SyncOperation(ctx.session, syncPoint, 1000);
            if (sts < 0) {
                std::cout<<"Ошибка синхронизации: " << sts<< std::endl;
                break;
            }
            
            auto frameEndTime = std::chrono::high_resolution_clock::now();
            auto frameTime = std::chrono::duration_cast<std::chrono::microseconds>(
                frameEndTime - frameStartTime);
            
            stats.totalFrames++;
            stats.totalDecodingTime += frameTime;
            
            mfxFrameInfo& info = workSurface->Info;
            mfxU16 width = (info.CropW > 0) ? info.CropW : info.Width;
            mfxU16 height = (info.CropH > 0) ? info.CropH : info.Height;            
        }
    }
    inputFileStream.close();
    std::cout<<"Всего декодировано кадров: " << stats.totalFrames<< std::endl;
    std::cout<<"Общее время декодирования: " << stats.totalDecodingTime.count() / 1000000.0 << " с"<< std::endl;
    std::cout<<"Количество кадров в секунду"<<stats.totalFrames/(stats.totalDecodingTime.count()/ 1000000.0)<<std::endl;
    
    return MFX_ERR_NONE;
}

mfxStatus DecodeVideoFile(const std::string& inputFile, mfxU32 codecId) {
    DecoderContext ctx;
    mfxStatus sts;
    
    sts = InitDecoder(ctx, inputFile, codecId);
    if (sts != MFX_ERR_NONE) {
        std::cout<<"Ошибка инициализации декодера: " << sts<< std::endl;
        return sts;
    }
    
    sts = DecodeVideo(ctx, inputFile);
    if (sts != MFX_ERR_NONE) {
        std::cout<<"Ошибка декодирования видео: " << sts<< std::endl;
        return sts;
    }
    
    return MFX_ERR_NONE;
}

int main() {
    std::string inputFile = "/home/mehroj/Coding/hardware-decoding/video/output.h264";
    
    DecodeVideoFile(inputFile, MFX_CODEC_AVC);
    
    return 0;
}