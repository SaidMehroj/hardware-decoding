cmake_minimum_required(VERSION 3.10)
project(NVDecFrameDecoder)

set(CMAKE_CXX_STANDARD 14)

include_directories(
    /usr/local/cuda/include
    /home/mehroj/Downloads/Video_Codec_SDK_11.1.5/Interface
)

link_directories(
    /usr/local/cuda/lib64
)

add_executable(nvdec_decoder main.cpp)

target_link_libraries(nvdec_decoder
    cuda
    cudart
    nvcuvid
)
