from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
from pathlib import Path

from .camera_grid import CameraGrid
from .control_panel import ControlPanel
from .camera_widget import CameraWidget
from core.camera_manager import CameraManager
from core.recording_manager import RecordingManager
import logging


class MainWindow(QMainWindow):
    """Main application window with modern UI"""
    
    def __init__(self):
        super().__init__()
        self.cameras = {}
        self.camera_manager = CameraManager()
        self.recording_manager = RecordingManager()
        
        self.setWindowTitle("RedNVR v1.0")
        self.setMinimumSize(1280, 720)
        self.resize(1600, 900)
        
        # Center window
        self.center_window()
        
        # Initialize UI
        self.init_ui()
        
        # Load cameras
        self.load_cameras()
        
        # Setup shortcuts
        self.setup_shortcuts()
        
        self.single_view_camera_id = None
        
        # Kamera grid'de layout değişimlerinde flash engelleme
        self.camera_grid.before_layout_change = self.before_camera_grid_layout_change
        self.camera_grid.after_layout_change = self.after_camera_grid_layout_change

    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left panel - Camera grid
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = self.create_header()
        left_layout.addWidget(header)
        
        # Camera grid
        self.camera_grid = CameraGrid()
        self.camera_grid.camera_selected.connect(self.on_camera_selected)
        left_layout.addWidget(self.camera_grid)
        
        main_layout.addWidget(left_panel, 3)
        
        # Right panel - Controls
        self.control_panel = ControlPanel()
        self.control_panel.setMaximumWidth(350)
        self.control_panel.camera_added.connect(self.add_camera)
        self.control_panel.camera_removed.connect(self.remove_camera)
        self.control_panel.recording_toggled.connect(self.toggle_recording)
        self.control_panel.settings_changed.connect(self.update_camera_settings)
        
        main_layout.addWidget(self.control_panel, 1)
        
        # Status bar
        self.create_status_bar()
        
        # Apply custom styles
        left_panel.setStyleSheet("""
            #leftPanel {
                background-color: #19191C;
                border-right: 1px solid #2D2D32;
            }
        """)
        
    def create_header(self):
        """Create header with title and view controls"""
        header = QWidget()
        header.setFixedHeight(60)
        layout = QHBoxLayout(header)
        
        # Logo/Title
        logo_label = QLabel("RedNVR v1.0")
        logo_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #EB3B5A;
        """)
        layout.addWidget(logo_label)
        
        layout.addStretch()
        
        # View mode buttons
        view_group = QButtonGroup(self)
        
        # Grid view
        grid_btn = QToolButton()
        grid_btn.setIcon(self.create_icon("grid"))
        grid_btn.setToolTip("Grid View")
        grid_btn.setCheckable(True)
        grid_btn.setChecked(True)
        grid_btn.clicked.connect(lambda: self.camera_grid.set_layout_mode('grid'))
        view_group.addButton(grid_btn)
        layout.addWidget(grid_btn)
        
        # Single view
        single_btn = QToolButton()
        single_btn.setIcon(self.create_icon("maximize"))
        single_btn.setToolTip("Single View")
        single_btn.setCheckable(True)
        single_btn.clicked.connect(lambda: self.camera_grid.set_layout_mode('single'))
        view_group.addButton(single_btn)
        layout.addWidget(single_btn)
        
        # 2x2 view
        quad_btn = QToolButton()
        quad_btn.setIcon(self.create_icon("grid-2x2"))
        quad_btn.setToolTip("2x2 View")
        quad_btn.setCheckable(True)
        quad_btn.clicked.connect(lambda: self.camera_grid.set_layout_mode('2x2'))
        view_group.addButton(quad_btn)
        layout.addWidget(quad_btn)
        
        layout.addSpacing(20)
        
        # Fullscreen button
        fullscreen_btn = QToolButton()
        fullscreen_btn.setIcon(self.create_icon("fullscreen"))
        fullscreen_btn.setToolTip("Fullscreen")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        layout.addWidget(fullscreen_btn)
        
        return header
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #19191C;
                color: #888;
                border-top: 1px solid #2D2D32;
            }
        """)
        
        # Recording indicator
        self.recording_label = QLabel("● Recording: 0")
        self.recording_label.setStyleSheet("color: #EB3B5A; font-weight: bold;")
        self.status_bar.addWidget(self.recording_label)
        
        # Camera count
        self.camera_count_label = QLabel("Cameras: 0")
        self.status_bar.addWidget(self.camera_count_label)
        
        # CPU usage
        self.cpu_label = QLabel("CPU: 0%")
        self.status_bar.addPermanentWidget(self.cpu_label)
        
        # Storage
        self.storage_label = QLabel("Storage: 0 GB free")
        self.status_bar.addPermanentWidget(self.storage_label)
        
        # Update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)
        
    def create_icon(self, name):
        """Create icon with proper color"""
        icon = QIcon()
        
        # Create pixmap
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white, 2))
        
        if name == "grid":
            # Draw grid icon
            painter.drawRect(2, 2, 8, 8)
            painter.drawRect(14, 2, 8, 8)
            painter.drawRect(2, 14, 8, 8)
            painter.drawRect(14, 14, 8, 8)
        elif name == "maximize":
            # Draw maximize icon
            painter.drawRect(4, 4, 16, 16)
        elif name == "grid-2x2":
            # Draw 2x2 grid
            painter.drawRect(2, 2, 10, 10)
            painter.drawRect(12, 2, 10, 10)
            painter.drawRect(2, 12, 10, 10)
            painter.drawRect(12, 12, 10, 10)
        elif name == "fullscreen":
            # Draw fullscreen icon
            painter.drawLine(2, 2, 8, 2)
            painter.drawLine(2, 2, 2, 8)
            painter.drawLine(16, 2, 22, 2)
            painter.drawLine(22, 2, 22, 8)
            painter.drawLine(2, 16, 2, 22)
            painter.drawLine(2, 22, 8, 22)
            painter.drawLine(22, 16, 22, 22)
            painter.drawLine(16, 22, 22, 22)
            
        painter.end()
        
        icon.addPixmap(pixmap)
        return icon
        
    def center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        self.move(
            rect.center().x() - self.width() // 2,
            rect.center().y() - self.height() // 2
        )
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Add camera
        QShortcut(QKeySequence("Ctrl+N"), self, self.control_panel.show_add_camera_dialog)
        
        # Toggle fullscreen
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        
        # Grid views
        QShortcut(QKeySequence("1"), self, lambda: self.camera_grid.set_layout_mode('grid'))
        QShortcut(QKeySequence("2"), self, lambda: self.camera_grid.set_layout_mode('2x2'))
        QShortcut(QKeySequence("3"), self, lambda: self.camera_grid.set_layout_mode('single'))
        
        # Record all
        QShortcut(QKeySequence("Ctrl+R"), self, self.toggle_all_recording)
        
    def load_cameras(self):
        """Load cameras from config"""
        config_file = Path("config/cameras.json")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    cameras_data = json.load(f)
                    for camera_data in cameras_data:
                        self.add_camera(camera_data)
            except Exception as e:
                logging.error(f"Failed to load cameras: {e}")
                
    def save_cameras(self):
        """Save cameras to config"""
        cameras_data = []
        for camera_id, camera in self.cameras.items():
            cameras_data.append({
                'id': camera_id,
                'name': camera.name,
                'url': camera.url,
                'username': camera.username,
                'password': camera.password
            })
            
        config_file = Path("config/cameras.json")
        with open(config_file, 'w') as f:
            json.dump(cameras_data, f, indent=2)
            
    def add_camera(self, camera_data):
        """Add new camera"""
        camera_id = camera_data.get('id') or self.camera_manager.generate_id()
        
        # Create camera widget
        camera_widget = CameraWidget(
            camera_id,
            camera_data['name'],
            camera_data['url'],
            camera_data.get('username', ''),
            camera_data.get('password', '')
        )
        
        # Connect signals
        camera_widget.recording_toggled.connect(self.on_recording_toggled)
        camera_widget.snapshot_taken.connect(self.on_snapshot_taken)
        camera_widget.error_occurred.connect(self.on_camera_error)
        
        # Add to grid
        self.camera_grid.add_camera(camera_widget)
        
        # Store reference
        self.cameras[camera_id] = camera_widget
        
        # Update control panel
        self.control_panel.add_camera_to_list(camera_id, camera_data['name'])
        
        # Save config
        self.save_cameras()
        
        # Update status
        self.update_camera_count()
        
    def remove_camera(self, camera_id):
        """Remove camera"""
        if camera_id in self.cameras:
            # Stop camera
            camera_widget = self.cameras[camera_id]
            camera_widget.stop()
            
            # Remove from grid
            self.camera_grid.remove_camera(camera_widget)
            
            # Remove reference
            del self.cameras[camera_id]
            
            # Save config
            self.save_cameras()
            
            # Update status
            self.update_camera_count()
            
    def on_camera_selected(self, camera_id):
        """Handle camera selection"""
        self.control_panel.select_camera(camera_id)
        
        # Update PTZ controls if camera supports it
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            self.control_panel.set_ptz_enabled(camera.has_ptz)
            
    def toggle_recording(self, camera_id, state):
        """Toggle camera recording"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            if state:
                camera.start_recording()
            else:
                camera.stop_recording()
                
    def toggle_all_recording(self):
        """Toggle recording for all cameras"""
        recording_count = sum(1 for cam in self.cameras.values() if cam.is_recording)
        
        if recording_count > 0:
            # Stop all recordings
            for camera in self.cameras.values():
                camera.stop_recording()
        else:
            # Start all recordings
            for camera in self.cameras.values():
                camera.start_recording()
                
    def update_camera_settings(self, camera_id, settings):
        """Update camera settings"""
        if camera_id in self.cameras:
            camera = self.cameras[camera_id]
            camera.update_settings(settings)
            self.save_cameras()
            
    def on_recording_toggled(self, camera_id, is_recording):
        """Handle recording state change"""
        self.control_panel.update_recording_state(camera_id, is_recording)
        self.update_recording_count()
        
    def on_snapshot_taken(self, camera_id, filepath):
        """Handle snapshot taken"""
        self.status_bar.showMessage(f"Snapshot saved: {filepath}", 3000)
        
    def on_camera_error(self, camera_id, error):
        """Handle camera error"""
        camera = self.cameras.get(camera_id)
        if camera:
            self.status_bar.showMessage(f"Error - {camera.name}: {error}", 5000)
            
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def update_camera_count(self):
        """Update camera count in status bar"""
        count = len(self.cameras)
        self.camera_count_label.setText(f"Cameras: {count}")
        
    def update_recording_count(self):
        """Update recording count in status bar"""
        count = sum(1 for cam in self.cameras.values() if cam.is_recording)
        self.recording_label.setText(f"● Recording: {count}")
        
    def update_status(self):
        """Update status bar information"""
        # Update CPU usage
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_label.setText(f"CPU: {cpu_percent:.0f}%")
        
        # Update storage
        disk_usage = psutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        self.storage_label.setText(f"Storage: {free_gb:.1f} GB free")
        
    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(
            self, 'Exit RedNVR',
            'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Stop all cameras
            for camera in self.cameras.values():
                camera.stop()
                
            # Stop recording manager
            self.recording_manager.stop_all()
            
            event.accept()
        else:
            event.ignore()
            
    def before_camera_grid_layout_change(self):
        # Tüm kameraları gizle (flash engelleme)
        for cam in self.cameras.values():
            cam.hide()

    def after_camera_grid_layout_change(self):
        # Gerekli olanlar zaten grid tarafından gösterilecek
        pass

    def on_camera_double_clicked(self, camera_id):
        """Handle camera double click"""
        # Toggle single/grid view
        if self.camera_grid.layout_mode == 'single' and self.single_view_camera_id == camera_id:
            self.camera_grid.set_layout_mode('grid')
            self.single_view_camera_id = None
        else:
            self.camera_grid.set_layout_mode('single')
            self.single_view_camera_id = camera_id
            self.camera_grid.on_camera_selected(camera_id)