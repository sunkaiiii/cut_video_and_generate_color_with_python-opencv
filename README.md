
# cut_video_and_generate_color_with_python-opencv
自动识别电影剪辑、分析剪辑主题颜色
___
以前做过的一个小项目功能 <br>
目前已加入Mac版本的ffmpeg文件，最近对原来的不标准的路径命名作了修改，程序现在可以在Windows、Mac上运行。Linux预计应该也会加上。

这个程序通过使用OpenCV+FFmpeg将一段视频的剪辑自动切割，并分析每个剪辑的Dominant Color。

切割剪辑的方法主要是通过压缩图像分辨率并二色化，通过对比像素变化的数量判断前后两帧是否为同一剪辑段，并通过FFmpeg将切割的视频保存。

颜色识别使用简单的聚类算法，通过多次迭代，聚类出10（默认）个主体颜色。
___
#### 使用方法

 ```python main.py [split_file_name]  [options]  [generate_color]```

#### split_file_name:要切割的视频/路径的绝对路径 <br>
#### options:不同的option会影响ffmpeg的参数
 0、剪裁精准，速度也较为理想，当片段长度较长（>1分钟)时内存占用会很高 <br>
 -1、快速剪辑模式，速度最快，部分视频文件会因为关键帧问题导致切割尾部不准 <br>
 -2、压缩规格化之后的快速模式，对视频进行一次压缩，在使用快速剪辑模式进行裁剪，速度较为理想，剪裁精准，会占用一部分硬盘空间作为临时文件  <br>
 1、不会造成大量内存占用，速度较为理想，但部分视频因为关键帧在片头会有画面定格出现 <br>
 2、速度最慢（2小时视频约需要8-12小时剪裁），但剪裁精准，资源占用少 <br>
 3、默认值，提取视频音轨，使用OpenCV进行帧提取写入视频文件，与截取对应时间音轨合并为视频，速度较快，占用一定内存和临时空间，但精准度极高 <br>
 #### generate_color: <br>
 1、分析颜色 <br>
 0、不分析颜色 <br>
   

![](https://sunkaiiii.github.io/docs/images/cut_video1.png)![](https://sunkaiiii.github.io/docs/images/cut_video2.jpg)![](https://sunkaiiii.github.io/docs/images/cut_video3.jpg)![](https://sunkaiiii.github.io/docs/images/cut_video4.jpg) 



