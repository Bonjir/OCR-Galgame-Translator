
import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json

from ui.mainwindow import Ui_MainWindow # type: ignore
from ui.ocrdialog import Ui_Dialog # type: ignore
from screenshot import ScreenLabel
from ocr import Ocr_Handler
from translator import Translate_Handler
from customwidgets import *

API_CONFIG_FILE_PATH = "./config/api-config.json"
SETTINGS_FILE_PATH = "./config/settings.json"

class Main(DraggableMixin, QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__(clipped=False)
        self.adjustSize()
        self.setupUi(self)
        self.setWindowTitle('Galgame-Translator')
        self.setWindowIcon(QIcon('./icon/cut.png'))
        self.screen = QApplication.primaryScreen()
        # 托盘行为
        self.action_quit = QAction("Quit", self, triggered = self.close)
        self.action_show = QAction('Show', self, triggered = self.show)
        self.menu_tray = QMenu(self)
        self.menu_tray.addAction(self.action_quit)
        # 设置最小化托盘
        self.tray = QSystemTrayIcon(QIcon('./icon/screenshot.png'), self)
        self.tray.activated.connect(self.ocr_pushed) # 设置托盘点击事件处理函数
        self.tray.setContextMenu(self.menu_tray)
        self.tray.show()
        # 快捷键
        QShortcut(QKeySequence('F1'), self, self.ocr_pushed)
        # 信号与槽
        self.pushButton_ocr.clicked.connect(self.ocr_pushed)
        self.pushButton_gal.clicked.connect(self.galgame_pushed)
        self.pushButton_exit.clicked.connect(self.close)
    
    def ocr_pushed(self):
        self.hide()
        self.ocr_dialog = OCRDialog()
        self.ocr_dialog.shot()
        # self.ocr_dialog.exec_()
        self.ocr_dialog.signal_close.connect(self.ocr_finished)
    
    def galgame_pushed(self):
        self.hide()
        self.ocr_dialog = OCRDialog(True)
        self.ocr_dialog.shot()
        # self.ocr_dialog.exec_()
        self.ocr_dialog.signal_close.connect(self.ocr_finished)
    
    def ocr_finished(self):
        if not self.isMinimized():
            self.show()  # 截图完成显示窗口


class OCRDialog(DraggableMixin, QDialog, Ui_Dialog):
    # 创建关闭信号
    signal_close = pyqtSignal() # 结束事件无参数
    def __init__(self, galgame_mode = False):
        super().__init__(clipped=False)
        self.adjustSize()
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Tool)  # 不然exec_执行退出后整个程序退出
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)  # 没有窗口栏
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)  # 置顶 
        self.galgame_mode = galgame_mode
        # 信号与槽
        self.pushButton_continue.clicked.connect(self.shot)
        self.pushButton_close.clicked.connect(self.close)
        # 快捷键
        QShortcut(QKeySequence('Esc'), self, self.close)
        # OCR模块
        self.ocr_handler = Ocr_Handler()
        self.ocr_handler.signal_started.connect(self.ocr_handler_started_callback)
        self.ocr_handler.signal_finished.connect(self.ocr_handler_finished_callback)
        self.translate_handler = Translate_Handler()
        # 计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.grab_and_handle_screenshot)
        # load config
        with open(SETTINGS_FILE_PATH,"r+") as f:
            settings = json.load(f)
        self.grab_interval = int(settings['grab_interval'])
        self.timer.setInterval(self.grab_interval)
        
    def shot(self):
        # QMessageBox.information(self, '!', 'should be a screenshot here', QMessageBox.StandardButton.Ok)
        self.hide()
        self.timer.stop()
        self.screenlabel = ScreenLabel()
        self.screenlabel.showFullScreen()
        self.screenlabel.signal_shot.connect(self.shot_callback)
        self.screenlabel.signal_interrupt.connect(self.close)
        
    def shot_callback(self, selected_rect):
        """截图完成回调函数"""
        self.screenlabel.close()
        del self.screenlabel  # del前必须先close
        
        print(f'截图完成:区域{selected_rect}')
        self.selected_rect = selected_rect
        self.grab_and_handle_screenshot()
        if self.galgame_mode == True:
            # 启动定时器
            self.timer.start()
            
    def grab_and_handle_screenshot(self):
        '''对指定区域截图并进行处理'''
        # grab
        pixmap = QApplication.primaryScreen().grabWindow(0).copy(self.selected_rect)
        
        # show pixmap
        self.label_shot.setPixmap(pixmap)
        self.adjustSize()
        if not self.isMinimized():
            self.show()  # 截图完成显示窗口
            
        def make_pixmap_bytes_like(pixmap): # 图片格式处理
            buffer = QBuffer() # 创建一个 QBuffer 对象来保存字节数据
            buffer.open(QIODevice.WriteOnly)
            pixmap.save(buffer, "PNG") # 将 QImage 写入 QBuffer 对象，格式为 PNG（你可以根据需要选择其他格式）
            byte_data = buffer.data() # 获取字节流数据
            return bytes(byte_data) # byte_data 是一个 QByteArray 类型，你可以将它转换为 Python 的 bytes 类型
            
        image = make_pixmap_bytes_like(pixmap)
        if self.ocr_handler.isRunning() == False:
            self.ocr_handler.select_image(image)
            self.ocr_text = self.ocr_handler.start()
    
    def ocr_handler_started_callback(self):
        # self.edit_ocr.setText('[...]')
        pass
    
    def ocr_handler_finished_callback(self, text):
        if text == self.ocr_text:
            # 文字没变
            return
        self.ocr_text = text
        self.edit_ocr.setText(self.ocr_text)
        # start translate
        self.edit_translate.setText('[...]')
        translate_text = self.translate_handler.translate(self.ocr_text)
        self.edit_translate.setText(translate_text)
    
    def closeEvent(self, event):
        self.timer.stop()
        self.ocr_text = ''
        self.signal_close.emit()
        event.accept()

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    screen_height = QApplication.desktop().screenGeometry().height()
    screen_width = QApplication.desktop().screenGeometry().width()
    sys.exit(app.exec_())
    