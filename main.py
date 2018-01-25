import cut_video
import sys
import os

if __name__ == "__main__":
    mode = 3
    generate_color = True
    try:
        args = sys.argv[1]
        if len(sys.argv) == 3:
            mode = int(sys.argv[2])
        if len(sys.argv) == 4:
            mode=int(sys.argv[2])
            if int(sys.argv[3]) == 0:
                generate_color = False
    except:
        print("请传入一个文件或路径")
        exit(-1)
    # args="D:\文件与资料\视频\以前做过的"
    if os.path.isdir(args):
        cut_video.read_dir_video(args, generate_color=generate_color, mode=mode)
    else:
        cut_video.read_video(args, generate_color=generate_color, mode=mode)
