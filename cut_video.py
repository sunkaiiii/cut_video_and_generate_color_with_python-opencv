# coding=utf-8
import cv2
import compare_frame as compare
import subprocess
import os
import pandas as pd
import collections
import generate_color as gc
import platform

"""
 -------------cut_video-------------
功能：传入一个视频文件、路径，对视频进行切割，并保存在制定文件夹中
切割的视频会自动建立文件夹进行分类存储并保存剪裁文件信息表格以供分析
"""

cut_filenames = []
startFrames = []
stopFrames = []
startTimes = []
stopTimes = []
durations = []

middle_file_path = os.path.join(os.getcwd(), "middle_file")
cut_file_path = os.path.join(os.getcwd(), "cut")

ffmpegName = ""
if platform.system() == "Windows":
    ffmpegName = "ffmpeg.exe"
elif platform.system() == "Linux":
    a = 1
else:
    ffmpegName = "ffmpeg"
ffmpegPath = os.path.join(os.getcwd(), ffmpegName)


def frame_to_time(frame, rate):
    """
    将传入的帧转为记录时间的list
    :param frame: 传入的帧位置
    :param rate: 要剪裁视频的帧率
    :return: 返回值arr为转换好的list
    """
    arr = [0, 0, 0, 0]
    arr[3] = int(frame % rate)  # 计算毫秒（帧单位）
    frame = int(frame / rate)
    frame = frame * rate
    if frame / rate >= 60:
        arr[2] = int(frame / rate) % 60  # 计算秒
        frame = int(frame / 60)
        if (frame / rate > 60):
            arr[1] = int(frame / rate) % 60  # 计算分钟
            frame = int(frame / rate)
            arr[0] = int(frame / 60)  # 计算小时
        else:
            arr[1] = int(frame / rate)
    else:
        arr[2] = int(frame / rate)
    # print(arr)
    return arr


def write_log(startFrame, stopFrame, rate, filepath, filename, cut_filename):
    """
    将剪裁过程中生成的信息写入txt
    :param startFrame: 起始帧位置
    :param stopFrame: 结束帧位置
    :param rate: 帧率
    :param filepath: 路径地址
    :param filename: 剪裁文件的文件名
    :param cut_filename: 剪裁好的文件的文件名
    """
    fp = open(os.path.join(filepath, filename + "_剪裁信息.txt"), 'a')
    startTimeList = frame_to_time(startFrame, rate)
    stopTimeList = frame_to_time(stopFrame, rate)
    durationList = frame_to_time(stopFrame - startFrame, rate)
    startTime = str(startTimeList[0]) + ':' + str(startTimeList[1]) + ':' + str(startTimeList[2]) + ',' + str(
        startTimeList[3])
    stopTime = str(stopTimeList[0]) + ':' + str(stopTimeList[1]) + ':' + str(stopTimeList[2]) + ',' + str(
        stopTimeList[3])
    durationTime = str(durationList[0]) + ':' + str(durationList[1]) + ':' + str(durationList[2]) + ',' + str(
        durationList[3])
    cut_info = str(
        cut_filename + '\t' + str(startFrame) + '\t' + str(
            stopFrame) + '\t' + startTime + '\t' + stopTime + '\t' + durationTime + '\n')
    fp.write(cut_info)
    fp.close()
    cut_filenames.append(cut_filename)
    startFrames.append(startFrame)
    stopFrames.append(stopFrame)
    startTimes.append(startTime)
    stopTimes.append(stopTime)
    durations.append(durationTime)


def write_log_to_excel(name):
    """
    将剪裁的结果写入到cut对应文件夹中的excel文件
    """
    a = collections.OrderedDict()  # 使用顺序字典构建数据框，保证输出到excel时候数据顺序一致
    a['文件名'] = cut_filenames
    a['开始帧'] = startFrames
    a['结束帧'] = stopFrames
    a['开始时间'] = startTimes
    a['结束时间'] = stopTimes
    a['持续时间'] = durations
    df = pd.DataFrame(a, index=range(0, len(cut_filenames)))
    df.to_excel(os.path.join(cut_file_path, name, name + ".xlsx"), sheet_name='剪裁信息')


def save_video(frames, frameToStart, frameToStop, rate, saveNums, filename, size):
    """
    使用opencv的VideoWrite来保存视频,并使用ffmpeg合并音频视频，只可保存为avi格式
    需下载OpenH264(openh264-1.6.0-win64)并配置环境变量
    需下载ffmpeg
    :param frames: 记录的剪裁区间段的所有帧的内容
    :param frameToStart: 帧开始位置
    :param frameToStop: 帧结束位置
    :param rate: 视频的帧率
    :param saveNums: 当前已保存的片段数量
    :param filename: 保存的文件名
    :param size: 保存文件的分辨率
    :return: 视频保存成功，返回True，失败返回False
    """
    if (frameToStop < frameToStart):
        print('结束帧小于开始帧，错误退出')
        return False
    writer = cv2.VideoWriter()
    name = os.path.splitext(filename)[0]  # 去除文件扩展名
    name = os.path.basename(name)  # 去除文件路径，只保留文件名
    audio_full_filename = os.path.join(middle_file_path, name, name) + ".mp3"  # 临时文件夹的声音文件路径
    filename = os.path.basename(filename)  # 去除文件路径，保留文件名
    filename_no_count = os.path.splitext(filename)[0]
    filepath = os.path.join(middle_file_path, filename_no_count)  # 路径指定视频中间文件的路径为middle_file文件夹下原视频文件名
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    filename = filename_no_count + '_' + str(saveNums) + '.avi'  # 路径指定为cut文件夹下原视频文件名+剪裁序列序号
    print(filename)
    writer.open(os.path.join(filepath, filename), int(1145656920), rate, size, True)  # 参数2为avi格式的forucc，使用别的格式会导致转换出错
    for frame in frames:
        writer.write(frame)

    # 使用ffmpeg剪切对应时间段的音频
    subprocess.call([os.path.join(os.getcwd(), ffmpegName), "-y", "-vn", "-ss", str(frameToStart / rate), "-t",
                     str((frameToStop - frameToStart) / rate),
                     "-i", audio_full_filename, "-acodec", "copy", os.path.join(filepath, filename) + ".mp3"])
    if not os.path.exists(cut_file_path):
        os.mkdir(cut_file_path)
    savePath = os.path.join(cut_file_path, filename_no_count)
    if not os.path.exists(savePath):
        os.mkdir(savePath)
    # 使用ffmpeg合并音频与视频，保存在cut文件夹中
    subprocess.call([os.path.join(os.getcwd(), ffmpegName), "-y", "-i", os.path.join(filepath, filename), "-i",
                     os.path.join(filepath, filename) + ".mp3", "-vcodec", "copy", "-acodec", "copy",
                     os.path.join(savePath, filename)])
    write_log(frameToStart, frameToStop, rate, savePath, filename_no_count, filename)
    return True


def save_video_with_ffmpeg(filename, startFrame=0, stopFrame=1, rate=24, saveNumber=0, mode=0, kbps=4096, name=""):
    """
        使用ffmpeg截取视频，支持更多视频格式且速度依旧很快，有多种参数可调
    :param filename: 视频文件的路径
    :param startFrame: 视频开始帧的位置
    :param stopFrame: 视频结束帧的位置
    :param rate: 视频帧率
    :param saveNumber: 当前已保存的片段数量
    :param mode: 不同的mode对应不同的ffmpeg设置参数，具体请参阅ffmpeg官方文档 https://ffmpeg.org/ffmpeg.html
    :param kbps:压缩码率
    :return: 视频保存成功，返回True，失败返回False
    """
    cut_file_name = filename
    if (stopFrame < startFrame):
        print('结束帧小于开始帧，错误退出')
        return False

    filepath = os.path.join(cut_file_path, name)  # 路径指定为cut文件夹下原视频文件名
    filename = os.path.basename(filename)  # 去除文件路径，保留文件名
    if not os.path.exists(cut_file_path):
        os.mkdir(cut_file_path)
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    '''
    使用subprocess执行ffmpeg，需要下载ffmpeg相应套件
    -ss表示截取视频的开始时间
    -t表示从开始时间往后的持续时间
    acodec、vcodec的copy表示对原视频、音频不转码直接截取
    或者使用-vcodec等参数对其机型转码
    具体参考官方文档
    '''
    save_filename = os.path.splitext(filename)[0] + '_' + str(saveNumber) + os.path.splitext(filename)[
        1]  # 将文件名转换为原文件名+计数序号+扩展名
    print("cut_filename: ", os.path.join(filepath, save_filename))
    if mode == 0:
        subprocess.call([ffmpegPath, "-y", "-ss", str(startFrame / rate), "-t", str((stopFrame - startFrame) / rate)
                            , "-i", cut_file_name, "-c:v"
                            , "libx264", "-preset", "superfast", "-b:v"
                            , str(kbps) + "k", "-maxrate", str(kbps / 2) + "k", "-bufsize", str(kbps) + "k", "-c:a",
                         "copy", os.path.join(filepath, save_filename)])
    elif mode == -1 or mode == -2:
        startFrame += round(rate / 12 * 2)
        stopFrame -= round(rate / 12 * 4)
        subprocess.call([ffmpegPath, "-y", "-ss", str(startFrame / rate), "-t", str((stopFrame - startFrame) / rate)
                            , "-accurate_seek", "-i", cut_file_name, "-codec", "copy", "-avoid_negative_ts", "1",
                         os.path.join(filepath, save_filename)])

    elif mode == 1:
        subprocess.call([ffmpegPath,"-y","-ss",str(startFrame / rate),"-accurate_seek","-i",cut_file_name
                         ,"-t",str((stopFrame - startFrame) / rate),"-c:a","copy","-vcodec"
                         ,"mpeg4","-b:v",str(kbps)+"k","-r",str(rate),os.path.join(filepath,save_filename)])
    elif mode == 2:
        subprocess.call([ffmpegPath,"-y","-i",cut_file_name,"-ss",str(startFrame / rate)
                         ,"-t",str((stopFrame - startFrame) / rate),"-c:a","copy","-vcodec"
                         ,"mpeg4","-b:v",str(kbps)+"k","-r",str(rate),os.path.join(filepath,save_filename)])


    write_log(startFrame, stopFrame, rate, filepath, filename, save_filename)

    return True


def compress_video(filename, compression_type='mpeg4', kpbs=4096, gop=2):
    """
    mode=-2时默认调用的方法，压缩视频，并调整关键帧
    :param filename: 文件名
    :param compression_type: 压缩编码
    :param kpbs: 压缩码率
    :param gop: 关键帧
    :return: 压缩完成后返回压缩后的文件的路径
    """
    capture = cv2.VideoCapture(filename)
    rate = capture.get(cv2.CAP_PROP_FPS)
    totalFrameNumber = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    middle_file = os.path.join(middle_file_path,os.path.basename(filename)+".mp4")
    subprocess.call([ffmpegPath,"-y","-i",filename,"-ss","0","-t",str(totalFrameNumber / rate)
                     ,"-c:a","copy","-vcodec",compression_type,"-b:v",str(kpbs)+"k"
                     ,"-r",str(rate),"-keyint_min",str(gop),"-g",str(gop),middle_file])
    return True, middle_file


def merge_video(filenames):
    """
    传入要合并的视频文件的list
    :param filenames: 视频文件的路径list
    :return: 输出合并的视频
    """
    args = ""
    all_name = ""
    for filename in filenames:
        if not os.path.exists(os.getcwd() + "\\middle_file"):
            os.mkdir(os.getcwd() + '\\middle_file')
        if not os.path.exists(os.getcwd() + "\\middle_file\\merge"):
            os.mkdir(os.getcwd() + "\\middle_file\\merge")
        print(filename)
        name = filename.split('\\')[len(filename.split('\\')) - 1]
        all_name += os.path.splitext(name)[0] + '_'
        name = os.path.splitext(name)[0]
        middle_dir = '\middle_file\\merge\\'
        subprocess.call(
            os.getcwd() + '\\ffmpeg.exe -y -i ' + filename + ' -vcodec copy -acodec copy -vbsf h264_mp4toannexb ' + os.getcwd() + middle_dir + name + '.ts')
        args += os.getcwd() + middle_dir + name + '.ts' + '|'
    args = args[:-1]
    all_name = all_name[:-1]
    dir = filenames[0].strip(filenames[0].split("\\")[len(filenames[0].split('\\')) - 1])
    # print(dir)
    subprocess.call(
        os.getcwd() + '\\ffmpeg.exe -y -i \"concat:' + args + '\" -c copy -absf aac_adtstoasc ' + dir + all_name + '_merge.mp4')
    import shutil
    if os.path.exists(os.getcwd() + "\middle_file"):
        shutil.rmtree(os.getcwd() + '\middle_file')
    # print(args)


def compress_video_to_audio(filename):
    """
    mode=3时先调用的方法，将视频中的音频分离出来
    :param filename: 文件名
    """
    name, ext = os.path.splitext(filename)
    name = os.path.basename(name)
    middle_file = os.path.join(middle_file_path, name, name) + ".mp3"
    subprocess.call(
        [os.path.join(os.getcwd(), ffmpegName), "-y", "-i", filename, "-vn", "-ar", "44100", "-ac", "2", "-ab", "192k",
         "-f", "mp3", middle_file])


def cut_video(filename, mode=3, boundary=19):
    """
    对视频场景进行剪裁
    :param filename: 传入文件路径
    :param mode:传入不同的模式参数会使用不同的剪裁处理方法
    :param boundary:剪裁敏感度，此值越低，剪裁越敏感
    0、剪裁精准，速度也较为理想，当片段长度较长（>1分钟)时内存占用会很高，8G以上内存推荐使用此模式
    -1、快速剪辑模式，速度最快，部分视频文件会因为关键帧问题导致切割尾部不准
    -2、压缩规格化之后的快速模式，对视频进行一次压缩，在使用快速剪辑模式进行裁剪，速度较为理想，剪裁精准，会占用一部分硬盘空间作为临时文件
    1、不会造成大量内存占用，速度较为理想，但部分视频因为关键帧在片头会有画面定格出现
    2、速度最慢（2小时视频约需要8-12小时剪裁），但剪裁精准，资源占用少
    3、默认值，提取视频音轨，使用OpenCV进行帧提取写入视频文件，与截取对应时间音轨合并为视频，速度较快，占用一定内存和临时空间，但精准度极高
    :return: 剪裁完成后返回True，否则返回False
    """
    print("剪裁:" + filename)
    name = os.path.splitext(filename)[0]  # 去除文件扩展名
    name = os.path.basename(name)  # 去除文件路径，只保留文件名
    print(name)
    print(os.path.join(middle_file_path, name))
    if mode == -2:
        if not os.path.exists(middle_file_path):
            os.mkdir(middle_file_path)
        success, filename = compress_video(filename)
        if not success:
            print('转码出现错误')
            return
    elif mode == 3:
        if not os.path.exists(middle_file_path):
            os.mkdir(middle_file_path)
        if not os.path.exists(os.path.join(middle_file_path, name)):
            os.mkdir(os.path.join(middle_file_path, name))
        compress_video_to_audio(filename)

    if not os.path.exists(os.getcwd() + "\\cut"):
        os.mkdir(os.getcwd() + "\\cut")

    capture = cv2.VideoCapture(filename)
    if capture.isOpened():
        width = capture.get(int(cv2.CAP_PROP_FRAME_WIDTH))
        height = capture.get(int(cv2.CAP_PROP_FRAME_HEIGHT))
        size = (int(width), int(height))
        totalFrameNumber = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        print('视频一共', str(int(totalFrameNumber)) + '帧')
        frameToStart = 1
        capture.set(cv2.CAP_PROP_POS_FRAMES, frameToStart)
        frameToStop = totalFrameNumber
        if (frameToStop < frameToStart):
            print("结束帧小于开始帧，程序错误，即将退出！")
        else:
            print("结束帧为：第" + str(int(frameToStop)) + "帧")
        rate = capture.get(cv2.CAP_PROP_FPS)
        print("帧率为:" + str(rate))
        # delay = 1000 / rate;
        # forucc = capture.get(cv2.CAP_PROP_FOURCC)
        # print(forucc)
        currentFrame = frameToStart
        saveNums = 0
        success, frame = capture.read()
        frames = []
        cut_filenames.clear()
        startFrames.clear()
        stopFrames.clear()
        startTimes.clear()
        stopTimes.clear()
        durations.clear()
        while success:
            if mode == 3:
                frames.append(frame)  # 只有在mode=3时才进行frame存储，节省时间、空间
            currentImg = frame
            success, frame = capture.read()
            if not success:
                if currentFrame < totalFrameNumber:
                    currentFrame += 1
                    success = True
                    continue
            lastImg = frame
            isSimilar = compare.classify_pHash(currentImg, lastImg, boundary)
            # print(isSimilar)
            currentFrame += 1
            if not isSimilar:
                if (currentFrame - frameToStart > int(rate)):
                    print('发现剪辑')
                    if mode == 3:
                        saveFlag = save_video(frames, frameToStart, currentFrame, rate, saveNums, filename, size)
                        frames = []  # 清空列表缓存，进行下一次截取
                    else:
                        saveFlag = save_video_with_ffmpeg(filename, frameToStart, currentFrame, rate, saveNums, mode,
                                                          name=name)

                    if saveFlag:
                        print('第' + str(saveNums) + '段视频保存成功')
                        saveNums += 1
                        frameToStart = currentFrame
                    else:
                        print('第' + str(saveNums) + '段视频保存失败')
                        break
                else:
                    print('小于1秒的剪辑')
        write_log_to_excel(name)  # 剪裁结束，存入表格
        capture.release()

        """
        临时文件清理
        """
        if mode == -2:
            os.remove(filename)
        elif mode == 3:
            import shutil
            shutil.rmtree(os.path.join(middle_file_path, name))

    else:
        print('打开视频失败')
    return os.path.join(os.getcwd(), "cut", name)


def read_dir_video(path, mode=3, num=9999, generate_color=False):
    """
    如果要批量切割视频，应调用此方法
    :param path: 路径名
    :param mode:选择裁剪视频的模式
    :param num:选择切割目录下视频的数量，当num<0的时候，切割目录下所有视频
    """
    if not os.path.isdir(path):  # 当传入的是文件的时候，对文件进行分析
        cut_video(path)
        return
    list = os.listdir(path)
    count = 0
    for file in list:
        if num >= 0:
            if count == num:
                break
        file = os.path.join(path, file)
        # print(file)
        if not os.path.isdir(file):
            print(file)
            cut_path = cut_video(filename=file, mode=mode)
            generate_video_info(cut_path, generate_color)
        count += 1


def read_video(filename, mode=3, generate_color=False):
    cut_path = cut_video(filename, mode)
    generate_video_info(cut_path, generate_color)


def generate_video_info(cut_path, generate_color=False):
    if generate_color == True:
        gc.generate_cut_video_color(cut_path)

# cut_video('E:\V60511-173651.mp4',mode=0)

# names=[]
# dir="e:\\1"
# for file in os.listdir("E:\\1"):
#     names.append(dir+"\\"+file)
# merge_video(names)
