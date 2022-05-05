### pdf2txt.py使用说明

1. 环境：里面导包虽然用到的是pdfminer，但是不能直接pip install pdfminer，得到的版本不对；直接安装pdfplumber，就可以解决了——`pip install pdfplumber`。

2. >demo：`python pdf2txt.py  -o 123.txt  -O ./jpg_files   sample.pdf `      // 其它参数看代码里
   >
   >- 想针对扫描版的pdf：建议就不要给-o 123.txt了，就直接只保存图片就好了
   >
   >- 如果不是扫描版的pdf，可以把dpf文档文字整个快速的写进`123.txt`；然后把里面的图片放进`jpg_files`文件夹，
   >  这里面，较好的情况是生成的.jpg格式，部分不那么好的图会生成.bmp格式；还有部分位置知道是图，但提取不出来，得到的就是.img格式(图片查看器无法打开,程序也无法打开，做丢弃处理吧)
   >
   >Ps：针对扫面版的pdf，得到的123.txt是一段乱码，sizeof也不大，基本上整个内容都是以图片的形式放进了jpg_files,
   >一样，好的图格式大抵都是.jpg,然后很多基本都是.bmp