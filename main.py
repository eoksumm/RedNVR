import sys
import os
import json
import logging
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from ui.main_window import MainWindow
from core.app_config import AppConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rednvr.log'),
        logging.StreamHandler()
    ]
)

class RedNVR(QApplication):
    """Main application class"""
    
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("RedNVR v1.0")
        self.setApplicationVersion("1.0")
        self.setOrganizationName("RedNVR Systems")
        
        # Set application style
        self.setStyle('Fusion')
        
        # Load config
        self.config = AppConfig()
        
        # Apply theme
        self.apply_theme()
        
        # Create main window
        self.main_window = MainWindow()
        
    def apply_theme(self):
        """Apply modern dark theme"""
        dark_palette = QPalette()
        
        # Window colors
        dark_palette.setColor(QPalette.Window, QColor(25, 25, 28))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        
        # Base colors
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 40))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 50))
        
        # Text colors
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        
        # Button colors
        dark_palette.setColor(QPalette.Button, QColor(45, 45, 50))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        
        # Highlight colors
        dark_palette.setColor(QPalette.Highlight, QColor(235, 59, 90))
        dark_palette.setColor(QPalette.HighlightedText, Qt.white)
        
        self.setPalette(dark_palette)
        
        # Additional styling
        style = """
        QWidget {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            font-size: 14px;
        }
        
        QMainWindow {
            background-color: #19191C;
        }
        
        QPushButton {
            background-color: #2D2D32;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            color: white;
        }
        
        QPushButton:hover {
            background-color: #3D3D42;
        }
        
        QPushButton:pressed {
            background-color: #1D1D22;
        }
        
        QPushButton#primaryButton {
            background-color: #EB3B5A;
        }
        
        QPushButton#primaryButton:hover {
            background-color: #FC5C7D;
        }
        
        QPushButton#primaryButton:pressed {
            background-color: #C92A4A;
        }
        
        QLineEdit, QComboBox, QSpinBox {
            background-color: #2D2D32;
            border: 1px solid #3D3D42;
            border-radius: 6px;
            padding: 8px;
            color: white;
        }
        
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border-color: #EB3B5A;
            outline: none;
        }
        
        QTabWidget::pane {
            background-color: #232328;
            border: none;
        }
        
        QTabBar::tab {
            background-color: transparent;
            color: #888;
            padding: 10px 20px;
            margin-right: 5px;
        }
        
        QTabBar::tab:selected {
            color: white;
            border-bottom: 2px solid #EB3B5A;
        }
        
        QTabBar::tab:hover {
            color: #CCC;
        }
        
        QScrollBar:vertical {
            background-color: #232328;
            width: 10px;
            border: none;
        }
        
        QScrollBar::handle:vertical {
            background-color: #3D3D42;
            border-radius: 5px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #4D4D52;
        }
        
        QToolBar {
            background-color: #232328;
            border: none;
            spacing: 10px;
            padding: 5px;
        }
        
        QToolButton {
            background-color: transparent;
            border: none;
            border-radius: 6px;
            padding: 8px;
        }
        
        QToolButton:hover {
            background-color: #2D2D32;
        }
        
        QToolButton:pressed {
            background-color: #1D1D22;
        }
        
        QToolButton:checked {
            background-color: #EB3B5A;
        }
        
        QStatusBar {
            background-color: #232328;
            color: #888;
        }
        
        QMenu {
            background-color: #2D2D32;
            border: 1px solid #3D3D42;
            border-radius: 6px;
            padding: 5px;
        }
        
        QMenu::item {
            padding: 8px 20px;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #EB3B5A;
        }
        
        QSlider::groove:horizontal {
            background-color: #3D3D42;
            height: 4px;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background-color: #EB3B5A;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        
        QSlider::handle:horizontal:hover {
            background-color: #FC5C7D;
        }
        
        QCheckBox {
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            background-color: #2D2D32;
            border: 1px solid #3D3D42;
        }
        
        QCheckBox::indicator:checked {
            background-color: #EB3B5A;
            image: url(assets/icons/check-white.svg);
        }
        
        QGroupBox {
            font-weight: bold;
            border: 1px solid #3D3D42;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px;
        }
        
        QListWidget {
            background-color: #2D2D32;
            border: 1px solid #3D3D42;
            border-radius: 6px;
            outline: none;
        }
        
        QListWidget::item {
            padding: 8px;
            border-radius: 4px;
        }
        
        QListWidget::item:selected {
            background-color: #EB3B5A;
        }
        
        QListWidget::item:hover {
            background-color: #3D3D42;
        }
        
        QTableWidget {
            background-color: #2D2D32;
            border: none;
            gridline-color: #3D3D42;
        }
        
        QTableWidget::item:selected {
            background-color: #EB3B5A;
        }
        
        QHeaderView::section {
            background-color: #232328;
            color: white;
            padding: 8px;
            border: none;
            font-weight: 500;
        }
        
        QProgressBar {
            background-color: #2D2D32;
            border: none;
            border-radius: 4px;
            text-align: center;
            color: white;
        }
        
        QProgressBar::chunk {
            background-color: #EB3B5A;
            border-radius: 4px;
        }
        
        /* Custom styles for camera widgets */
        #cameraWidget {
            background-color: #2D2D32;
            border-radius: 8px;
        }
        
        #cameraTitle {
            font-weight: 600;
            font-size: 12px;
            color: #CCC;
        }
        
        #recordingIndicator {
            color: #EB3B5A;
            font-weight: bold;
        }
        """
        
        self.setStyleSheet(style)
        
    def show_splash(self):
        splash_pix = QPixmap("assets/rednvr.png") 
        splash = QSplashScreen(splash_pix)
        splash.show()
        self.processEvents()
        QTimer.singleShot(1500, splash.close)
        QTimer.singleShot(1500, self.main_window.show)
        return splash


def main():
    """Main entry point"""
    # Create necessary directories
    Path("recordings").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Create application
    app = RedNVR(sys.argv)
    
    # Set icon
    app.setWindowIcon(QIcon("assets/icons/rednvr.svg"))
    
    # Show splash and start
    splash = app.show_splash()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()