import time
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

def gst_frame_reader(video_path,hardware):
    if hardware == "cuda":
        pipeline_str = f"filesrc location={video_path} ! qtdemux ! h264parse ! nvh264dec ! appsink name=sink"
    elif hardware == "intel":
        pipeline_str = f"filesrc location={video_path} ! qtdemux ! h264parse ! vaapih264dec ! appsink name=sink"
    else:
        pipeline_str = f"filesrc location={video_path} ! qtdemux ! h264parse ! avdec_h264 ! appsink name=sink"    

    pipeline = Gst.parse_launch(pipeline_str)

    appsink = pipeline.get_by_name("sink")
    appsink.set_property("emit-signals", True)
    appsink.set_property("sync", False)
    appsink.set_property("max-buffers", 1)
    appsink.set_property("drop", False)

    pipeline.set_state(Gst.State.PAUSED)
    pipeline.get_state(Gst.CLOCK_TIME_NONE)

    _, duration = pipeline.query_duration(Gst.Format.TIME)
    duration_sec = duration / Gst.SECOND


    pipeline.set_state(Gst.State.PLAYING)
    frame_count=0
    t1 = time.time()
    try:
        while True:
            sample = appsink.emit("try-pull-sample", Gst.SECOND*1)
            if not sample:
                break
            frame_count+=1
            buffer = sample.get_buffer()
            caps = sample.get_caps()
            result, map_info = buffer.map(Gst.MapFlags.READ)
            if result:
                buffer.unmap(map_info)
            else:
                print("Failed to map buffer")

    finally:
        t2 = time.time()
        process_time = t2 - t1
        print(f"Process_time: {(process_time * 1000):.1f}")
        fps = frame_count / process_time if process_time > 0 else 0
        print(f"FPS: {fps:.1f}")
        speed = duration_sec / process_time if process_time > 0 else 0
        print(f"Speed: {speed:.1f}x")
        structure = caps.get_structure(0)
        width = structure.get_value("width")
        height = structure.get_value("height")
        fmt = structure.get_value("format")
        print(f"({width},{height}), format: {fmt}")
        pipeline.set_state(Gst.State.NULL)
        print(f"Frame_Count: {frame_count}")


def main():
    video_path = "/home/mehroj/Coding/hardware-decoding/video/input.mp4"
    print("CUDA decoding")
    gst_frame_reader(video_path,"cuda")

    print("\nINTEL decoding")
    gst_frame_reader(video_path,"intel")

    print("\nCPU decoding")
    gst_frame_reader(video_path,"cpu")


if __name__ == "__main__":
    main()