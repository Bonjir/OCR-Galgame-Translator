# OCR-Galgame-Translator



#### 自动识别图片中的文字？

#### 想啃生肉但懒得配置VNR？

这是一个基于OCR的Galgame翻译器小工具，可以通过框选指定区域自动翻译区域内的日文。

---

### 环境：

使用tkinter搭建窗口框架，百度的ocrAPI进行文字识别，以及腾讯的机器翻译API

后面的两个API都是**免费**的（每天限用次数很充足）

百度的ocrAPI申请参考：[百度ocr服务自动实现文字识别、图片识别功能](https://blog.csdn.net/unbuntu_luo/article/details/143216199) 

腾讯的机器翻译API申请参考：[免费翻译API及使用指南——百度、腾讯](https://blog.csdn.net/xiaoxian666/article/details/139954647)

python=3.10.10

---

### 相较于[原项目](https://github.com/jizhihaoSAMA/OCR-GALGAME-SystemTray)的更新点：

- 原项目处于半开源状态，代码并不和release一同更新，代码已经被抛弃很久了；并且原项目的代码有很多bug无法直接运行，在本项目中进行了修正
- 修正了无法进行OCR、Galgame模式框选区域的问题
- 原项目使用爬虫爬取百度翻译，反应速度慢而且经常出错，更改成了腾讯的翻译API接口

---

### 更新计划：

- 框选区域界面优化
- 基于pyqt对源代码进行重构（原代码的码风让人难以忍受）
- 主窗口界面优化

---

### 食用方法：

参考上面的两个链接注册API key，然后在./config/文件夹下中找到api-config.json，将里面的相应内容替换掉即可
