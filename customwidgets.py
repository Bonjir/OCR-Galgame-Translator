# affliated to OCR-Galgame-Translator

from PyQt5.QtCore import Qt, QTime, QEasingCurve, \
    QPoint, QSize, QRect, \
    QTimer, QPropertyAnimation
from PyQt5.QtWidgets import QWidget, QDialog, QMainWindow, QPushButton, QLineEdit, QApplication
from PyQt5.QtGui import QCursor

class MouseEventPenetrateButton(QPushButton):
    def __init__(self, parent: QWidget = None, text: str = ''):
        super().__init__(text, parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
    def mousePressEvent(self, e):
        self.parent().mousePressEvent(e) # 把事件转发给主窗口
        return super().mousePressEvent(e)
    
    def mouseMoveEvent(self, e):
        self.parent().mouseMoveEvent(e)
        return super().mouseMoveEvent(e)
    
    def mouseReleaseEvent(self, e):
        self.parent().mouseReleaseEvent(e) # 把事件转发给主窗口
        return super().mouseReleaseEvent(e)

class MouseEventPenetrateLineEdit(QLineEdit):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        
    def mousePressEvent(self, e):
        self.parent().mousePressEvent(e) # 把事件转发给主窗口
        return super().mousePressEvent(e)
    
    def mouseMoveEvent(self, e):
        self.parent().mouseMoveEvent(e)
        return super().mouseMoveEvent(e)
    
    def mouseReleaseEvent(self, e):
        self.parent().mouseReleaseEvent(e) # 把事件转发给主窗口
        return super().mouseReleaseEvent(e)
    
    def keyPressEvent(self, event):
        # if event.key() == Qt.Key.Key_Tab:
        #     print('tab pressed')
            
        if event.key() == Qt.Key.Key_Return:
            self.on_return_pressed(event)
            event.accept()
            return # 已经处理，不再转发
        
        if event.key() == Qt.Key.Key_Escape:
            self.parent().setFocus()
            event.accept()
            return
        
        return super().keyPressEvent(event)
    
    def on_return_pressed(self, event):
        """将焦点转移到下一个lineEdit控件，如果没有则触发父窗口editingFinishedEvent事件"""
        # 获取当前控件的父级
        parent = self.parent()
        
        # 获取父级布局
        layout = parent.layout() if parent else None
        if not layout:
            return
        # 获取控件在布局中的索引
        index = layout.indexOf(self)
        
        if index == -1:
            return
        # 如果有下一个控件，则将焦点转移过去
        if index + 1 < layout.count():
            next_widget = layout.itemAt(index + 1).widget()
            if isinstance(next_widget, QLineEdit):
                next_widget.setFocus()
            else:
                parent.editingFinishedEvent(event)
                parent.setFocus()

class DraggableMixin:
    def __init__(self, clipped = False):
        super().__init__()

        # 最小拖拽的距离
        self.DRAG_OFFSET_MINIMUM = 5
        
        # 存储鼠标按下的初始位置
        self.dragging = False
        self.drag_offset = QPoint()
        
        # 限制在屏幕内拖动
        self.clipped = clipped

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 记录鼠标按下时的窗口位置
            self.dragging = True
            self.drag_offset = event.globalPos() - self.pos()
            self.first_drag_pos = event.globalPos()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            # 限制拖拽的最小距离
            drag_offset = event.globalPos() - self.first_drag_pos
            if abs(drag_offset.x()) <= self.DRAG_OFFSET_MINIMUM and abs(drag_offset.y()) <= self.DRAG_OFFSET_MINIMUM:
                return
            self.first_drag_pos = QPoint(-100, -100)
            
            # 合理的屏幕范围
            self.screen_geometry = QApplication.primaryScreen().availableGeometry()
            # 计算新的窗口位置
            new_pos = event.globalPos() - self.drag_offset
            if self.clipped == True:
                # 限制窗口位置在屏幕范围内
                new_x = max(self.screen_geometry.left(), min(new_pos.x(), self.screen_geometry.right() - self.width()))
                new_y = max(self.screen_geometry.top(), min(new_pos.y(), self.screen_geometry.bottom() - self.height()))
            else:
                new_x, new_y = new_pos.x(), new_pos.y()
            self.move(new_x, new_y)  # 更新窗口位置
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
        else:
            super().mouseMoveEvent(event)
            
# 只作为基类
# class DraggableMainWindow(DraggableMixin, QMainWindow):
#     def __init__(self, clipped = False):
#         DraggableMixin.__init__(self, clipped)
        
# class DraggableDialog(DraggableMixin, QDialog):
#     def __init__(self, clipped = False):
#         DraggableMixin.__init__(self, clipped)

# class DraggableWidget(DraggableMixin, QWidget):
#     def __init__(self, clipped = False):
#         DraggableMixin.__init__(self, clipped)