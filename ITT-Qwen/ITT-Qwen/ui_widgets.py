import tempfile
import os
import textwrap
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QFileDialog, QMessageBox, QDialog, QCheckBox, QFrame, QSizePolicy,
                             QTextBrowser, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, Signal, QSettings, QSize, QRect, QPoint, QRectF
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QPainter, QColor, QPainterPath, QPen
import markdown

from config import COLORS, DEFAULT_TUTORIAL_MESSAGE
from custom_window import CustomTitleBar

class SelectionImageLabel(QLabel):
    dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.selection_mode = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.original_pixmap = None

    def set_selection_mode(self, active):
        self.selection_mode = active
        if not active:
            self.clear_selection()
        self.setCursor(Qt.CursorShape.CrossCursor if active else Qt.CursorShape.ArrowCursor)

    def clear_selection(self):
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.update()

    def has_selection(self):
        return not self.start_point.isNull() and not self.end_point.isNull()

    def get_selection_rect(self):
        return QRect(self.start_point, self.end_point).normalized()

    def setPixmap(self, pixmap):
        self.original_pixmap = pixmap.copy() if pixmap and not pixmap.isNull() else None
        super().setPixmap(pixmap)
        self.clear_selection()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].path().lower().endswith(
            ('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.dropped.emit(file_path)

    def mousePressEvent(self, event):
        if self.selection_mode and event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.end_point = self.start_point
            self.update()

    def mouseMoveEvent(self, event):
        if self.selection_mode and event.buttons() & Qt.MouseButton.LeftButton:
            self.end_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.selection_mode and event.button() == Qt.MouseButton.LeftButton:
            self.end_point = event.position().toPoint()
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selection_mode and self.has_selection():
            painter = QPainter(self)
            rect_to_draw = QRect(self.start_point, self.end_point).normalized()
            pen = QPen(QColor(255, 0, 0, 200), 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QColor(255, 0, 0, 30))
            painter.drawRect(rect_to_draw)

class BubbleWidget(QWidget):
    def __init__(self, is_user, parent=None):
        super().__init__(parent)
        self.is_user = is_user

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = COLORS['user_message'] if self.is_user else COLORS['bot_message']
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)

        rect = self.rect()
        path = QPainterPath()
        
        bubble_rect = QRectF(rect.left(), rect.top(), rect.width(), rect.height() - 10)
        radius = 15.0
        
        path.addRoundedRect(bubble_rect, radius, radius)

        if self.is_user:
            tail_x = bubble_rect.right() - radius
            tail_y = bubble_rect.bottom()
            path.moveTo(tail_x, tail_y)
            path.quadTo(tail_x, tail_y + 10, tail_x - 10, tail_y)
        else:
            tail_x = bubble_rect.left() + radius
            tail_y = bubble_rect.bottom()
            path.moveTo(tail_x, tail_y)
            path.quadTo(tail_x, tail_y + 10, tail_x + 10, tail_y)
            
        painter.drawPath(path)

class MarkdownTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def sizeHint(self) -> QSize:
        doc_height = self.document().size().height()
        return QSize(super().sizeHint().width(), int(doc_height) + 5)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.document().setTextWidth(self.viewport().width())
        self.updateGeometry()

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(450, 320)
        
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)

        container_widget = QWidget()
        dialog_layout.addWidget(container_widget)
        
        container_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self, title="About ITT-Qwen", show_minimize=False, show_maximize=False)
        container_layout.addWidget(self.title_bar)

        content_widget = QWidget()
        content_widget.setStyleSheet("border: none;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.addWidget(content_widget)

        about_text = """
            ### ITT-Qwen (Image To Text)
            **Version 1.0**

            Built by: **Matt Wesney**

            This application leverages the power of the Qwen Vision Language Model (`qwen2.5vl:7b`) via Ollama to provide detailed analysis and answers based on the images you provide.
        """

        about_browser = MarkdownTextBrowser()
        about_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: transparent;
                border: none;
                color: {COLORS['text']};
                font-size: 14px;
            }}
        """)
        
        cleaned_text = textwrap.dedent(about_text).strip()
        html = markdown.markdown(cleaned_text, extensions=['fenced_code', 'codehilite', 'extra'])
        doc_style = f"""
        <style>
            h3 {{ color: {COLORS['text_secondary']}; }}
            a {{ color: #81A2BE; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
        """
        about_browser.setHtml(doc_style + html)
        
        content_layout.addWidget(about_browser)
        content_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.setFixedWidth(100)
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['text']};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
        """)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        content_layout.addLayout(button_layout)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('ImageChat', 'Settings')
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('Settings')
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        
        tutorial_group = QWidget()
        tutorial_layout = QVBoxLayout(tutorial_group)
        
        self.show_tutorial = QCheckBox('Show Tutorial Message on Startup')
        self.show_tutorial.setChecked(self.settings.value('show_tutorial', True, type=bool))
        tutorial_layout.addWidget(self.show_tutorial)
        
        self.tutorial_text = QTextEdit()
        self.tutorial_text.setPlaceholderText('Custom tutorial message...')
        self.tutorial_text.setText(self.settings.value('tutorial_message', DEFAULT_TUTORIAL_MESSAGE))
        tutorial_layout.addWidget(self.tutorial_text)
        
        layout.addWidget(tutorial_group)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton('Save')
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QTextEdit {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
            QCheckBox {{
                color: {COLORS['text']};
            }}
        """)
    
    def save_settings(self):
        self.settings.setValue('show_tutorial', self.show_tutorial.isChecked())
        self.settings.setValue('tutorial_message', self.tutorial_text.toPlainText())
        self.accept()

class NotificationWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedHeight(24)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        
        self.message_label = QLabel()
        self.message_label.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 11px;
        """)
        layout.addWidget(self.message_label)

        layout.addStretch()

        self.disclaimer_label = QLabel("Always check vital details; though we strive for accuracy, no system is perfect.")
        self.disclaimer_label.setStyleSheet(f"""
            color: {COLORS['border']};
            font-size: 10px;
        """)
        layout.addWidget(self.disclaimer_label)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['background']};
                border: none;
            }}
        """)
        
    def show_message(self, message, message_type='info'):
        colors = {
            'success': '#4CAF5066',
            'error': '#F4433666',
            'info': COLORS['text_secondary']
        }
        
        self.message_label.setStyleSheet(f"""
            color: {colors.get(message_type, COLORS['text_secondary'])};
            font-size: 11px;
        """)
        
        self.message_label.setText(message)

class ChatMessage(QWidget):
    def __init__(self, text, is_user=True, timestamp="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(0)

        main_container = QWidget()
        main_container_layout = QVBoxLayout(main_container)
        main_container_layout.setContentsMargins(0,0,0,0)
        main_container_layout.setSpacing(3)
        main_container.setMaximumWidth(800)

        bubble = BubbleWidget(is_user)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(15, 12, 15, 22)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 80))
        bubble.setGraphicsEffect(shadow)

        message_browser = MarkdownTextBrowser()
        message_browser.setOpenExternalLinks(True)
        message_browser.setReadOnly(True)
        message_browser.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        message_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        message_browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        try:
            cleaned_text = textwrap.dedent(text).strip()
            html = markdown.markdown(cleaned_text, extensions=['fenced_code', 'codehilite', 'extra'])
        except ImportError:
            html = f"<p>Please install 'markdown' and 'pygments' libraries to see formatted text.</p><pre><code>pip install markdown pygments</code></pre>"
        except Exception as e:
            html = f"<p>Error rendering Markdown: {e}</p>"

        doc_style = f"""
        <style>
            body {{
                color: {COLORS['text']};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }}
            p {{ 
                margin-bottom: 10px; 
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: {COLORS['text']};
                margin: 10px 0;
            }}
            h3 {{
                font-size: 16px;
            }}
            strong, b {{
                font-weight: bold;
            }}
            em, i {{
                font-style: italic;
            }}
            ul, ol {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            li {{
                margin: 3px 0;
            }}
            a {{ 
                color: #81A2BE; 
                text-decoration: none; 
            }}
            a:hover {{ 
                text-decoration: underline; 
            }}
            pre {{ 
                background-color: {COLORS['background']}; 
                padding: 10px; 
                border-radius: 5px; 
                border: 1px solid {COLORS['border']};
                font-family: Consolas, "Courier New", monospace;
                margin: 10px 0;
            }}
            code {{
                font-family: Consolas, "Courier New", monospace;
            }}
            blockquote {{
                border-left: 3px solid {COLORS['accent']};
                margin: 10px 0;
                padding-left: 10px;
                color: {COLORS['text_secondary']};
            }}
            /* Pygments syntax highlighting */
            .highlight .c  {{ color: #586e75; }}
            .highlight .err {{ color: #93a1a1; }}
            .highlight .k  {{ color: #859900; }}
            .highlight .l  {{ color: #2aa198; }}
            .highlight .n  {{ color: #268bd2; }}
            .highlight .o  {{ color: #859900; }}
            .highlight .p  {{ color: #cb4b16; }}
            .highlight .cm {{ color: #586e75; }}
            .highlight .cp {{ color: #859900; }}
            .highlight .c1 {{ color: #586e75; }}
            .highlight .cs {{ color: #859900; }}
            .highlight .gd {{ color: #2aa198; }}
            .highlight .ge {{ font-style: italic; }}
            .highlight .gh {{ color: #cb4b16; }}
            .highlight .gs {{ font-weight: bold; }}
            .highlight .gu {{ color: #cb4b16; }}
            .highlight .kc {{ color: #cb4b16; }}
            .highlight .kd {{ color: #268bd2; }}
            .highlight .kn {{ color: #859900; }}
            .highlight .kp {{ color: #859900; }}
            .highlight .kr {{ color: #268bd2; }}
            .highlight .kt {{ color: #dc322f; }}
            .highlight .ld {{ color: #93a1a1; }}
            .highlight .m  {{ color: #2aa198; }}
            .highlight .s  {{ color: #2aa198; }}
            .highlight .na {{ color: #93a1a1; }}
            .highlight .nb {{ color: #B58900; }}
            .highlight .nc {{ color: #268bd2; }}
            .highlight .no {{ color: #cb4b16; }}
            .highlight .nd {{ color: #268bd2; }}
            .highlight .ni {{ color: #cb4b16; }}
            .highlight .ne {{ color: #cb4b16; }}
            .highlight .nf {{ color: #268bd2; }}
            .highlight .nl {{ color: #93a1a1; }}
            .highlight .nn {{ color: #93a1a1; }}
            .highlight .nx {{ color: #93a1a1; }}
            .highlight .py {{ color: #93a1a1; }}
            .highlight .nt {{ color: #268bd2; }}
            .highlight .nv {{ color: #268bd2; }}
            .highlight .ow {{ color: #859900; }}
            .highlight .w  {{ color: #93a1a1; }}
            .highlight .mf {{ color: #2aa198; }}
            .highlight .mh {{ color: #2aa198; }}
            .highlight .mi {{ color: #2aa198; }}
            .highlight .mo {{ color: #2aa198; }}
            .highlight .sb {{ color: #586e75; }}
            .highlight .sc {{ color: #2aa198; }}
            .highlight .sd {{ color: #93a1a1; }}
            .highlight .s2 {{ color: #2aa198; }}
            .highlight .se {{ color: #cb4b16; }}
            .highlight .sh {{ color: #2aa198; }}
            .highlight .si {{ color: #2aa198; }}
            .highlight .sx {{ color: #2aa198; }}
            .highlight .sr {{ color: #dc322f; }}
            .highlight .s1 {{ color: #2aa198; }}
            .highlight .ss {{ color: #2aa198; }}
            .highlight .bp {{ color: #268bd2; }}
            .highlight .vc {{ color: #268bd2; }}
            .highlight .vg {{ color: #268bd2; }}
            .highlight .vi {{ color: #268bd2; }}
            .highlight .il {{ color: #2aa198; }}
        </style>
        """
        
        message_browser.setHtml(doc_style + html)
        
        bubble_layout.addWidget(message_browser)
        
        message_browser.setStyleSheet(f"""
            QTextBrowser {{
                background-color: transparent;
                border: none;
                color: {COLORS['text']};
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }}
        """)
        
        main_container_layout.addWidget(bubble)
        
        if timestamp:
            time_label = QLabel(timestamp)
            time_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9px; margin-top: 2px;")
            
            time_alignment = Qt.AlignmentFlag.AlignRight if is_user else Qt.AlignmentFlag.AlignLeft
            main_container_layout.addWidget(time_label, alignment=time_alignment)

        if is_user:
            layout.addStretch()
        layout.addWidget(main_container)
        if not is_user:
            layout.addStretch()

class ImagePreviewWidget(QWidget):
    image_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image_path = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
    
        self.image_preview = SelectionImageLabel('Drag and drop or click to select an image')
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumHeight(200)
        self.image_preview.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {COLORS['accent']};
                border-radius: 8px;
                background-color: {COLORS['secondary_bg']};
                padding: 20px;
                font-size: 14px;
                color: {COLORS['text_secondary']};
            }}
        """)
        self.image_preview.dropped.connect(self.handle_image_selection)
        layout.addWidget(self.image_preview)
    
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
    
        button_style = f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['text']};
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['accent_hover']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['accent']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text_secondary']};
            }}
        """
        checkable_button_style = button_style + f"""
            QPushButton:checked {{
                background-color: {COLORS['accent_hover']};
                border: 1px solid {COLORS['border']};
            }}
        """
    
        self.select_btn = QPushButton('Select Image')
        self.select_btn.setStyleSheet(button_style)
        self.select_btn.clicked.connect(self.select_image)
        button_layout.addWidget(self.select_btn)
    
        self.select_area_btn = QPushButton('Select Area')
        self.select_area_btn.setStyleSheet(checkable_button_style)
        self.select_area_btn.setCheckable(True)
        self.select_area_btn.toggled.connect(self.toggle_selection_mode)
        button_layout.addWidget(self.select_area_btn)

        self.clear_btn = QPushButton('Clear Image')
        self.clear_btn.setStyleSheet(button_style)
        self.clear_btn.clicked.connect(self.clear_image)
        button_layout.addWidget(self.clear_btn)
    
        layout.addLayout(button_layout)

    def get_image_for_model(self):
        if self.image_preview.has_selection() and self.image_preview.original_pixmap:
            selection_rect_widget = self.image_preview.get_selection_rect()
            
            original_pixmap = self.image_preview.original_pixmap
            widget_size = self.image_preview.size()
            pixmap_size = original_pixmap.size()
            
            scaled_pixmap = original_pixmap.scaled(widget_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            scaled_size = scaled_pixmap.size()

            offset_x = (widget_size.width() - scaled_size.width()) / 2
            offset_y = (widget_size.height() - scaled_size.height()) / 2

            scale_x = pixmap_size.width() / scaled_size.width()
            scale_y = pixmap_size.height() / scaled_size.height()

            crop_x = (selection_rect_widget.x() - offset_x) * scale_x
            crop_y = (selection_rect_widget.y() - offset_y) * scale_y
            crop_width = selection_rect_widget.width() * scale_x
            crop_height = selection_rect_widget.height() * scale_y
            
            crop_x = max(0, crop_x)
            crop_y = max(0, crop_y)
            crop_width = min(crop_width, pixmap_size.width() - crop_x)
            crop_height = min(crop_height, pixmap_size.height() - crop_y)

            crop_rect_original = QRect(int(crop_x), int(crop_y), int(crop_width), int(crop_height))

            if not crop_rect_original.isEmpty():
                cropped_pixmap = original_pixmap.copy(crop_rect_original)
                fd, temp_path = tempfile.mkstemp(suffix=".png")
                os.close(fd)
                cropped_pixmap.save(temp_path, "PNG")
                return temp_path, True
        
        return self.current_image_path, False

    def toggle_selection_mode(self, checked):
        self.image_preview.set_selection_mode(checked)
    
    def handle_image_selection(self, file_path):
        try:
            self.current_image_path = file_path
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                raise Exception("Invalid image file")
            
            self.image_preview.original_pixmap = pixmap.copy()
                
            scaled_pixmap = pixmap.scaled(
                self.image_preview.width() - 40,
                self.image_preview.height() - 40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_preview.setPixmap(scaled_pixmap)
            self.image_selected.emit(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")
    
    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        
        if file_name:
            self.handle_image_selection(file_name)
    
    def clear_image(self):
        self.current_image_path = None
        self.image_preview.setPixmap(QPixmap())
        self.image_preview.setText('Drag and drop or click to select an image')
        self.image_selected.emit("")
        if self.select_area_btn.isChecked():
            self.select_area_btn.setChecked(False)
        self.image_preview.clear_selection()