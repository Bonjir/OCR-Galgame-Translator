
'''
调用方式：

def shot(self):
    self.hide()
    self.screenlabel = ScreenLabel()
    self.screenlabel.showFullScreen()
    self.screenlabel.signal_shot.connect(self.shot_callback)

def shot_callback(self, selected_rect):
    """截图完成回调函数"""
    self.label.close()
    del self.label  # del前必须先close
    print(f'截图完成:区域{selected_rect}')
    if not self.isMinimized():
        self.show()  # 截图完成显示窗口
    
'''

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class Bbox(object):
    def __init__(self):
        self._x1, self._y1 = 0, 0
        self._x2, self._y2 = 0, 0

    @property
    def point1(self):
        return self._x1, self._y1

    @point1.setter
    def point1(self, position: tuple):
        self._x1 = position[0]
        self._y1 = position[1]

    @property
    def point2(self):
        return self._x2, self._y2

    @point2.setter
    def point2(self, position: tuple):
        self._empty = False
        self._x2 = position[0]
        self._y2 = position[1]

    @property
    def bbox(self):
        if self._x1 < self._x2:
            x_min, x_max = self._x1, self._x2
        else:
            x_min, x_max = self._x2, self._x1

        if self._y1 < self._y2:
            y_min, y_max = self._y1, self._y2
        else:
            y_min, y_max = self._y2, self._y1
        return (x_min, y_min, x_max - x_min, y_max - y_min)

    def __str__(self):
        return str(self.bbox)


class ScreenLabel(QLabel):
    signal_shot = pyqtSignal(QRect)
    signal_interrupt = pyqtSignal()

    def __init__(self):
        super().__init__()
        height = QApplication.desktop().screenGeometry().height()
        width = QApplication.desktop().screenGeometry().width()
        self._press_flag = False
        self._bbox = Bbox()
        self._pen = QPen(Qt.GlobalColor.white, 2, Qt.DashLine)
        self._painter = QPainter()
        self._bbox = Bbox()
        self._pixmap = QPixmap(width, height)
        self._pixmap.fill(QColor(255, 255, 255))
        self.setPixmap(self._pixmap)
        self.setWindowOpacity(0.4)

        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 设置背景颜色为透明

        QShortcut(QKeySequence("esc"), self, self.interrupt) # 创建了一个快捷键事件，当按下 Esc 键时关闭窗口。

        self.setWindowFlag(Qt.Tool)  # 不然exec_执行退出后整个程序退出

        # palette = QPalette()
        # palette.
        # self.setPalette()

    def _draw_bbox(self):
        pixmap = self._pixmap.copy()
        self._painter.begin(pixmap)
        self._painter.setPen(self._pen)  # 设置pen必须在begin后
        rect = QRect(*self._bbox.bbox)
        self._painter.fillRect(rect, Qt.GlobalColor.black)  # 区域不透明
        self._painter.drawRect(rect)  # 绘制虚线框
        self._painter.end()
        self.setPixmap(pixmap)
        self.update()
        self.showFullScreen()


    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            # print("鼠标左键：", [QMouseEvent.x(), QMouseEvent.y()])
            self._press_flag = True
            self._bbox.point1 = [QMouseEvent.x(), QMouseEvent.y()]

    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton and self._press_flag:
            # print("鼠标释放：", [QMouseEvent.x(), QMouseEvent.y()])
            self._bbox.point2 = [QMouseEvent.x(), QMouseEvent.y()]
            self._press_flag = False
            self.signal_shot.emit(QRect(*self._bbox.bbox))

    def mouseMoveEvent(self, QMouseEvent):
        if self._press_flag:
            # print("鼠标移动：", [QMouseEvent.x(), QMouseEvent.y()])
            self._bbox.point2 = [QMouseEvent.x(), QMouseEvent.y()]
            self._draw_bbox()

    def interrupt(self):
        self.signal_interrupt.emit()
        self.close()