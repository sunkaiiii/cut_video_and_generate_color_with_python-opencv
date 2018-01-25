# coding=gbk
import os
import cv2 as cv2
import numpy as np
import colorsys
from PIL import Image
import k_mean_class

"""
 -------------generate_color---------------
功能：传入剪切好的视频的路径，按秒分析每秒视频帧中的主题颜色
并将分析图保存在指定路径当中
"""

video_extensions = [".avi", ".mp4", ".flv", ".mpg", ".mpeg", ".3gp"]
generate_color_path = os.path.join(os.getcwd(), 'cut_main_color')


def handle_main_color(colors, frame, filename, pathname, image_count, num=10):
    """
    将分析好的颜色画在图片中，并调用方法保存图片
    :param colors:分析好的颜色list
    :param frame:分析帧
    :param filename:文件名
    :param pathname:路径名
    :param image_count:分析文件名计数
    :param num:显示颜色的数量
    """
    shape = frame.shape
    width = 800
    ratio = float(shape[0]) / float(shape[1])
    height = width * ratio
    size = (int(width), int(height))
    frame = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    count = 0
    rec_width = width / num
    rec_height = rec_width * 0.75
    width_add = width / 200
    height_add = width / 200
    cv2.rectangle(frame, (0, int(height - rec_height)), (int(width), int(height)), (220, 220, 220), -1)
    for i in colors:
        bgr = (i[2], i[1], i[0])
        # print(bgr)
        cv2.rectangle(frame,
                      (int(rec_width * count + width_add), int(height - rec_height + height_add)),
                      (int(rec_width * (count + 1) - width_add), int(height - height_add)),
                      bgr, -1)
        count += 1
    # cv2.imshow('21',frame)
    # cv2.waitKey(0)
    save_file(pathname, filename, frame, image_count)


def find_main_color(frame, filename, pathname, image_count, max_iterations=10, min_distance=0.5, k=10):
    """
    mode=0时调用的方法，使用聚类k值分析来判断图像主题颜色
    :param frame: 要分析的帧
    :param filename: 文件名
    :param pathname: 目录
    :param image_count: 计数
    :param max_iterations:计算深度，值越高则深度越深，结果越精确，速度越慢
    :param min_distance:相似颜色距离，此值越小，则颜色分离程度越大，
    :param k:聚类初始点数量，同时也代表输出color的list的长度
    """
    k_image = k_mean_class.Kmeans(max_iterations=max_iterations, min_distance=min_distance, k=k)
    image = Image.fromarray(frame, 'RGB')
    try:
        color = k_image.run(image)
    except:
        print(pathname + filename + '分析失败')
        return None
    hsv_color = []
    for i in color:
        hsv_color.append(list(colorsys.rgb_to_hsv(i[0], i[1], i[2])))
    hsv_color = sorted(hsv_color, key=lambda x: x[2], reverse=True)
    # print(hsv_color)
    for i in range(0, len(hsv_color)):
        r, g, b = colorsys.hsv_to_rgb(hsv_color[i][0], hsv_color[i][1], hsv_color[i][2])
        color[i] = (b, g, r)
        # print(color[i])
    handle_main_color(color, frame, filename, pathname, image_count)
    return True


def save_file(pathname, filename, firstframe, image_count):
    """
    将画好的，带有主题颜色色块的图片保存
    :param pathname:路径名
    :param filename:文件名
    :param firstframe:视频帧
    :param image_count:计数
    """
    pathname = os.path.basename(pathname)
    if not os.path.exists(generate_color_path):
        os.mkdir(generate_color_path)
    path = os.path.join(generate_color_path, pathname)
    if not os.path.exists(path):
        os.mkdir(path)
    filename = os.path.basename(filename)
    # cv2.imwrite('cut_main_color\\123\\'+ filename + '_' + str(image_count) + '.jpg', frame)
    cv2.imencode('.jpg', firstframe)[1].tofile(os.path.join(path, filename + '_' + str(image_count) + '.jpg'))
    print(os.path.join(path, filename + '_' + str(image_count) + '.jpg') + '保存成功')


def find_main_color_by_vertical_cut(frame, filename, image_count, pathname, firstframe):
    """
    将横坐标切割为10份，并逐次查找每一份当中的主题颜色
    :param frame: 当前帧
    :param filename: 文件名
    :param image_count: 计数
    """

    # 重新调整图片大小
    shape = frame.shape
    width = 1024
    ratio = float(shape[0]) / float(shape[1])
    height = width * ratio
    size = (int(width), int(height))
    frame = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    firstframe = cv2.resize(firstframe, size, interpolation=cv2.INTER_AREA)
    try:
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    except:
        return None
    image = Image.fromarray(image, 'RGB')
    image = image.convert('RGBA')
    width = image.width
    height = image.height
    for i in range(0, 10):
        # 切割视频的纵向区域选择图像的3/10至7/10的位置，排除一些边缘干扰
        cut_image = image.crop(
            (image.width / 10 * i, image.height / 20 * 6, image.width / 10 * (i + 1), image.height / 20 * 14))
        # cut_image.show()
        max_score = 0
        colors = []
        dominant_color = ()
        for count, (r, g, b, a) in cut_image.getcolors(cut_image.size[0] * cut_image.size[1]):
            if a == 0:
                continue
            # print(r,g,b)
            saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]
            y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)
            y = (y - 16.0) / (235 - 16)
            # print(y)

            # 过滤掉高光和阴影
            if y > 0.95:
                continue
            if y < 0.05:
                continue

            score = (saturation + 0.1) * count
            if score > max_score:
                if (b, g, r) in colors:  # 尽量寻找不一样的颜色
                    continue
                max_score = score
                dominant_color = (b, g, r)

        try:
            colors.append(dominant_color)
            # 在原图上显示色块
            cv2.rectangle(firstframe,
                          (int(width / 10 * i), height - 64),
                          (int(width / 10 * (i + 1)), height),
                          dominant_color,
                          -1)
        except:
            continue
    save_file(pathname, filename, firstframe, image_count)


def read_cut_video(filename, pathname, mode=0, max_iterations=10, min_distance=0.5, k=10):
    """
    读取传入进来的文件帧，并调用相关方法进行分析
    :return:
    """
    # 打开视频文件
    capture = cv2.VideoCapture(filename)
    if not capture.isOpened():
        print('文件打开失败')
        return
    success, frame = capture.read()
    rate_count = 1
    rate = capture.get(cv2.CAP_PROP_FPS)
    print("帧率为:" + str(rate))
    # 使用opencv获取视频帧数返回为infinity,故暂时使用24帧
    # 视频剪裁的默认帧率为24
    if rate > 1000 or rate <= 0:
        rate = 24
    totalFrameNumber = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    generate_frame = []
    for i in range(1, 4):
        generate_frame.append(int(totalFrameNumber / 4 * i))
    image_count = 0  # 保存图片数量计数
    while success:
        # cal_frame_hist(frame)
        success, frame = capture.read()
        # 读取失败,退出循环
        if not success:
            break
        rate_count += 1
        # 在剪裁视频中,当读取到对应切割点的frame时分析颜色
        if rate_count in generate_frame:
            firstframe = frame
            if mode == 0:
                saturation = cv2.convertScaleAbs(frame, cv2.CV_8UC1, 1.2, -20)  # 增加图像对比度，降低一定亮度，使颜色区分明显
                ok = 0
                try:
                    for i in range(0, 3):
                        if find_main_color(saturation, filename, pathname, image_count, max_iterations, min_distance,
                                           k) is True:  ##如果没有找到主要颜色或者程序执行错误,重新进入循环:
                            ok = 1
                            break
                        print('进行第' + str(i + 1) + '次重试')
                    if ok == 0:
                        success, frame = capture.read()
                        rate_count += 1
                        # 读取失败,退出循环
                        if not success:
                            break
                        for i in range(3, 6):
                            if find_main_color(saturation, filename, pathname,
                                               image_count) is True:  ##如果没有找到主要颜色或者程序执行错误,重新进入循环:
                                break
                            print('进行第' + str(i + 1) + '次重试')
                except:
                    return
                finally:
                    image_count += 1
            if mode == 1:
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
                morph_close = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)  # 对图像做闭运算，减少颜色复杂度
                saturation = cv2.convertScaleAbs(morph_close, cv2.CV_8UC1, 1.2, -20)  # 增加图像对比度，降低一定亮度，使颜色区分明显
                find_main_color_by_vertical_cut(saturation, filename, image_count, pathname, firstframe)
                image_count += 1


def generate_cut_video_color(filepath='cut\\', mode=0, max_iterations=10, min_distance=0.5, k=10):
    """
    读取剪裁文件夹下的所有文件，并依次对其进行分析
    :param mode:
    0、对横坐标切割10份，分析每一份中的最主题颜色
    1、对图像整体分析颜色，取前10个主题颜色。
    :return:
    """
    list = os.listdir(filepath)
    for file in list:
        file = os.path.join(filepath, file)
        if not os.path.isdir(file):
            extension = os.path.splitext(file)[1]
            if extension in video_extensions:
                print('读取' + file)
                read_cut_video(file, filepath, mode, max_iterations, min_distance, k)


if __name__ == "__main__":
    generate_cut_video_color('D:\文件与资料\Onedrive\文档\PycharmProjects\internship_working\cut\\开场', mode=0)
    # filelist=os.listdir('E:\picture2')
    # count=0
    # for file in filelist:
    #     frame=cv2.imread('E:\picture2\\'+file)
    #     find_main_color(frame=frame,filename=file,image_count=count,pathname='E:\picture')
    #     count+=1
