import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from config import COLORS
from main_application import ImageToTextChatApp

def main():
    try:
        app = QApplication(sys.argv)
        
        app.setStyleSheet(f"""
            QToolTip {{
                background-color: {COLORS['secondary_bg']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                padding: 5px;
                border-radius: 4px;
            }}
        """)
        
        window = ImageToTextChatApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()