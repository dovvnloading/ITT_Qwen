from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen

from config import COLORS

class TitleBarButton(QPushButton):
    def __init__(self, icon_name, hover_color, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.hover_color = hover_color
        self.icon_name = icon_name
        self.setStyleSheet(f"""
            QPushButton {{
                border: none;
                border-radius: 0px;
                background-color: transparent;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor(COLORS['text']))
        painter.setPen(pen)
        
        if self.icon_name == 'minimize':
            painter.drawLine(10, 15, 20, 15)
        elif self.icon_name == 'maximize':
            painter.drawRect(10, 8, 10, 10)
        elif self.icon_name == 'close':
            painter.drawLine(10, 10, 20, 20)
            painter.drawLine(20, 10, 10, 20)

class CustomTitleBar(QWidget):
    def __init__(self, parent=None, title='ITT-Qwen', show_minimize=True, show_maximize=True):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.drag_pos = None
        self.title = title
        self.show_minimize = show_minimize
        self.show_maximize = show_maximize
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 13px;
            font-weight: bold;
            border: none;
            background-color: transparent;
        """)
        layout.addWidget(self.title_label)
        layout.addStretch()

        if self.show_minimize:
            self.minimize_btn = TitleBarButton('minimize', COLORS['secondary_bg'])
            self.minimize_btn.clicked.connect(self.parent.showMinimized)
            layout.addWidget(self.minimize_btn)
        else:
            self.minimize_btn = None
        
        if self.show_maximize:
            self.maximize_btn = TitleBarButton('maximize', COLORS['secondary_bg'])
            self.maximize_btn.clicked.connect(self.toggle_maximize)
            layout.addWidget(self.maximize_btn)
        else:
            self.maximize_btn = None
        
        self.close_btn = TitleBarButton('close', '#FF4444')
        self.close_btn.clicked.connect(self.parent.close)
        layout.addWidget(self.close_btn)

        self.setStyleSheet(f"""
            CustomTitleBar {{
                background-color: {COLORS['background']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.parent.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            self.parent.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.show_maximize:
            self.toggle_maximize()

class FramelessWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.central_widget = QWidget()
        self.central_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.title_bar = CustomTitleBar(self)
        self.layout.addWidget(self.title_bar)
        
        self.content_container = QWidget()
        self.content_container.setStyleSheet("border: none; border-radius: 0px;")

    def resizeEvent(self, event):
        super().resizeEvent(event)