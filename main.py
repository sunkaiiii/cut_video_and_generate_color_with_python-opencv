import cut_video
import sys
import os
if __name__ == "__main__":
    try:
        args = sys.argv[1]
        if len(sys.argv) == 3:
            mode = int(sys.argv[2])
    except:
        print("请传入一个文件或路径")
        exit(-1)
    # args="D:\文件与资料\视频\以前做过的"
    if os.path.isdir(args):
        cut_video.read_dir_video(args, generate_color=True, mode=mode)
    else:
        cut_video.read_video(args, generate_color=True,mode=mode)
