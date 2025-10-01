import os
import tempfile
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QMessageBox, QScrollArea,
                             QLineEdit, QSizePolicy, QDialog, QMenuBar)
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QAction

from config import COLORS, DEFAULT_TUTORIAL_MESSAGE
from custom_window import FramelessWindow
from ui_widgets import SettingsDialog, ImagePreviewWidget, NotificationWidget, ChatMessage, AboutDialog
from model_thread import ModelThread

class ImageToTextChatApp(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.message_history = []
        self.current_image_path = None
        self.process_thread = None
        self.settings = QSettings('ImageChat', 'Settings')
        self.chat_scroll_area = None
        self.temp_files = []
        self.initUI()
        self.show_tutorial_if_enabled()
    
    def create_menu_bar(self):
        menubar = QMenuBar(self)
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text']};
                border: none;
                padding: 2px;
            }}
            QMenuBar::item:selected {{
                background-color: {COLORS['accent']};
            }}
            QMenu {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
            }}
            QMenu::item:selected {{
                background-color: {COLORS['accent']};
            }}
        """)
        
        file_menu = menubar.addMenu('File')
        
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        clear_history_action = QAction('Clear History', self)
        clear_history_action.triggered.connect(self.clear_history)
        file_menu.addAction(clear_history_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu('Help')
        
        show_tutorial_action = QAction('Show Tutorial', self)
        show_tutorial_action.triggered.connect(lambda: self.show_tutorial_message(force=True))
        help_menu.addAction(show_tutorial_action)
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        return menubar

    def initUI(self):
        self.setMinimumSize(1200, 800)
    
        self.menubar = self.create_menu_bar()
        self.notification = NotificationWidget()

        self.layout.addWidget(self.menubar)
        self.layout.addWidget(self.content_container, stretch=1)
        self.layout.addWidget(self.notification)

        self.content_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                border: none;
            }}
        """)
    
        main_layout = QVBoxLayout(self.content_container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)
    
        content_widget = QWidget()
        content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
        """)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(20)
        main_layout.addWidget(content_widget)
    
        chat_container = QWidget()
        chat_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
        """)
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
    
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                border-radius: 8px;
                background-color: {COLORS['secondary_bg']};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {COLORS['secondary_bg']};
                width: 14px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['accent']};
                border-radius: 7px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['accent_hover']};
            }}
            QScrollBar::handle:vertical:pressed {{
                background-color: {COLORS['border']};
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                width: 0px;
            }}
        """)
    
        self.chat_widget = QWidget()
        self.chat_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['secondary_bg']};
            }}
        """)
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.addStretch()
        self.chat_scroll_area.setWidget(self.chat_widget)
        chat_layout.addWidget(self.chat_scroll_area)
    
        input_container = QWidget()
        input_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
        """)
        input_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 10, 0, 0)
    
        message_row = QHBoxLayout()
    
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText('Type your message...')
        self.message_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px 15px;
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)
        self.message_input.returnPressed.connect(self.send_message)
        message_row.addWidget(self.message_input)
    
        button_container = QWidget()
        button_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(8)
    
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
    
        self.send_btn = QPushButton('Send')
        self.send_btn.setStyleSheet(button_style)
        self.send_btn.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_btn)
    
        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.setStyleSheet(button_style)
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.hide()
        button_layout.addWidget(self.cancel_btn)
    
        message_row.addWidget(button_container)
        input_layout.addLayout(message_row)
    
        chat_layout.addWidget(input_container)
    
        content_layout.addWidget(chat_container, stretch=7)
    
        self.image_preview = ImagePreviewWidget()
        self.image_preview.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
        """)
        self.image_preview.image_selected.connect(self.handle_image_selection)
        content_layout.addWidget(self.image_preview, stretch=3)
    
        self.notification.show_message("Ready", 'info')
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.show_notification("Settings saved", 'success')
    
    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec()
    
    def show_tutorial_if_enabled(self):
        if self.settings.value('show_tutorial', True, type=bool):
            self.show_tutorial_message()
    
    def show_tutorial_message(self, force=False):
        if force or self.settings.value('show_tutorial', True, type=bool):
            tutorial_text = self.settings.value('tutorial_message', DEFAULT_TUTORIAL_MESSAGE)
            self.add_message(tutorial_text, False, "")
    
    def handle_image_selection(self, file_path):
        self.current_image_path = file_path if file_path else None
        if file_path:
            self.show_notification(f"Selected image: {os.path.basename(file_path)}", 'success')
        else:
            self.show_notification("Image cleared", 'info')
    
    def show_notification(self, message, message_type='info'):
        self.notification.show_message(message, message_type)
    
    def add_message(self, text, is_user=True, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().strftime('%I:%M %p')

        message_widget = ChatMessage(text, is_user, timestamp)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, message_widget)
        self.message_history.append({
            'text': text,
            'is_user': is_user,
            'timestamp': timestamp
        })
    
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        if self.chat_scroll_area:
            vsb = self.chat_scroll_area.verticalScrollBar()
            vsb.setValue(vsb.maximum())
    
    def cleanup_temp_files(self):
        for temp_file in self.temp_files:
            try:
                os.remove(temp_file)
            except OSError as e:
                print(f"Error removing temp file {temp_file}: {e}")
        self.temp_files.clear()

    def clear_history(self):
        reply = QMessageBox.question(
            self,
            'Clear History',
            'Are you sure you want to clear all chat history?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
    
        if reply == QMessageBox.StandardButton.Yes:
            while self.chat_layout.count() > 1:
                item = self.chat_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
            self.message_history.clear()
        
            if self.current_image_path:
                self.image_preview.clear_image()
            
            self.cleanup_temp_files()
            self.show_notification("Chat history cleared", 'info')
    
    def cancel_processing(self):
        if self.process_thread and self.process_thread.isRunning():
            self.process_thread.cancel()
            self.process_thread.wait()
            self.show_notification("Processing cancelled", 'info')
            self.reset_ui_after_processing()
    
    def reset_ui_after_processing(self):
        self.message_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.send_btn.show()
        self.cancel_btn.hide()
    
    def send_message(self):
        message = self.message_input.text().strip()
        if not message:
            return
        
        if self.process_thread and self.process_thread.isRunning():
            self.show_notification("Please wait for the current processing to complete", 'error')
            return
        
        try:
            self.add_message(message, True)
            self.message_input.clear()
            
            self.show_notification("Processing your request...", 'info')
            self.message_input.setEnabled(False)
            self.send_btn.hide()
            self.cancel_btn.show()

            image_path_for_model, is_temp = self.image_preview.get_image_for_model()
            if is_temp:
                self.temp_files.append(image_path_for_model)
            
            self.process_thread = ModelThread(self.message_history, image_path_for_model)
            self.process_thread.finished.connect(self.handle_response)
            self.process_thread.error.connect(self.handle_error)
            self.process_thread.start()
            
        except Exception as e:
            self.handle_error(f"Failed to send message: {str(e)}")
    
    def handle_response(self, response):
        try:
            self.add_message(response, False)
            self.reset_ui_after_processing()
            self.show_notification("Response received", 'success')
        except Exception as e:
            self.handle_error(f"Failed to handle response: {str(e)}")
    
    def handle_error(self, error_message):
        self.reset_ui_after_processing()
        self.show_notification(f"Error: {error_message}", 'error')
        QMessageBox.critical(self, "Error", error_message)
    
    def closeEvent(self, event):
        if self.process_thread and self.process_thread.isRunning():
            self.process_thread.cancel()
            self.process_thread.wait()
        self.cleanup_temp_files()
        event.accept()