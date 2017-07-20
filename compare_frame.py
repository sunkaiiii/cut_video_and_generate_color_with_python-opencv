#coding=utf-8
import cv2
import numpy as np

"""
 -------------compare_frame-------------
提供了直方图、平均哈希、感知哈希三种方式判断场景
可以根据需要选择不同的方法来判断场景来剪裁视频
"""

def calculate(img1,img2):
    """
    计算直方图的相关性
    :return: 返回值dgree为相关性系数，一般认为>0.7的时候即为相似场景
    """
    hist1 = cv2.calcHist([img1], [0], None, [256], [0.0, 255.0])
    hist2 = cv2.calcHist([img2], [0], None, [256], [0.0, 255.0])
    degree = 0
    for i in range(len(hist1)):
        if hist1[i] != hist2[i]:
            degree = degree + (1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i]))
        else:
            degree = degree + 1
    degree = degree / len(hist1)
    return degree


def classify_hist_with_split(img1,img2):
    """
    将传入的图标通道分离，分别计算三个通道的直方图相关性系数
    :return: 当返回值<0.7（默认值）的时候，认为场景发生了改变
    """
    sub_img1=cv2.split(img1)
    sub_img2=cv2.split(img2)
    sub_data=0
    for im1,im2 in zip(sub_img1,sub_img2):
        sub_data+=calculate(im1,im2)
    sub_data=sub_data/3
    print(sub_data)
    if sub_data>0.7:
        return True
    else:
        return False

def classify_aHash(image1,image2,boundary=19):
    """
    平均哈希算法计算,将图片转为8x8的图片，模糊掉各种微小细节
    判断是否为同一场景
    """
    image1 = cv2.resize(image1,(8,8))
    image2 = cv2.resize(image2,(8,8))
    gray1 = cv2.cvtColor(image1,cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2,cv2.COLOR_BGR2GRAY)
    hash1 = getHash(gray1)
    hash2 = getHash(gray2)
    return Hamming_distance(hash1,hash2,boundary)


def classify_pHash(image1,image2,boundary=19):
    """
    感知哈希法进行计算
    :param boundary:查询界限，界越低，切割越敏感
    """
    try:
        image1 = cv2.resize(image1,(32,32))
        image2 = cv2.resize(image2,(32,32))
    except:
        return False
    gray1 = cv2.cvtColor(image1,cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2,cv2.COLOR_BGR2GRAY)
    # 将灰度图转为浮点型，再进行dct变换
    dct1 = cv2.dct(np.float32(gray1))
    dct2 = cv2.dct(np.float32(gray2))
    # 取左上角的32*32，这些代表图片的最低频率
    # 这个操作等价于c++中利用opencv实现的掩码操作
    # 在python中进行掩码操作，可以直接这样取出图像矩阵的某一部分
    dct1_roi = dct1[0:8,0:8]
    dct2_roi = dct2[0:8,0:8]
    hash1 = getHash(dct1_roi)
    hash2 = getHash(dct2_roi)
    return Hamming_distance(hash1,hash2,boundary)

def getHash(image):
    """
    输入灰度图
    :param image:
    :return: 返回hash
    """
    avreage = np.mean(image)
    hash = []
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i,j] > avreage:
                hash.append(1)
            else:
                hash.append(0)
    return hash

def Hamming_distance(hash1,hash2,boundary):
    """
    计算汉明距离
    计算完的hash利用汉明距离可以清晰的表示有几个像素不一样，
    :param hash1:
    :param hash2:
    :param boundary:搜索界限，超过这个界认为是不一样的图像
    :return: 当大于boundart(默认值19)的时候认为是两个不同的场景
    """
    num = 0
    for index in range(len(hash1)):
        if hash1[index] != hash2[index]:
            num += 1
    if num>boundary:
        return False
    return True