from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ControlPanel(QWidget):
    """Right-side control panel"""
    
    # Signals
    camera_added = pyqtSignal(dict)  # camera_data
    camera_removed = pyqtSignal(str)  # camera_id
    recording_toggled = pyqtSignal(str, bool)  # camera_id, state
    settings_changed = pyqtSignal(str, dict)  # camera_id, settings
    
    def __init__(self):
        super().__init__()
        self.current_camera_id = None
        self.cameras = {}  # camera_id -> camera_name
        self.audio_states = {}  # camera_id -> muted/unmuted
        self.audio_volumes = {}  # camera_id -> volume (0-100)
        self.setObjectName("controlPanel")
        self.init_ui()
        # Default: all muted
        self.audio_check.setChecked(False)
        self.volume_slider.setValue(0)
        self.volume_slider.setEnabled(False)

    def init_ui(self):
        """Initialize control panel UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Controls")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: white;
            padding: 10px 0;
        """)
        layout.addWidget(title)
        
        # Camera list section
        camera_section = self.create_camera_section()
        layout.addWidget(camera_section)
        
        # Recording controls
        recording_section = self.create_recording_section()
        layout.addWidget(recording_section)
        
        # PTZ controls
        self.ptz_section = self.create_ptz_section()
        self.ptz_section.setVisible(False)  # Hidden by default
        layout.addWidget(self.ptz_section)
        
        # Audio controls
        audio_section = self.create_audio_section()
        layout.addWidget(audio_section)
        
        layout.addStretch()
        
        # Apply panel styling
        self.setStyleSheet("""
            #controlPanel {
                background-color: #232328;
                border-left: 1px solid #2D2D32;
            }
            QGroupBox {
                background-color: #2D2D32;
                border: none;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
            }
            QGroupBox::title {
                color: #888;
                font-weight: 500;
                subcontrol-origin: margin;
                left: 15px;
                top: -5px;
            }
        """)
        
    def create_camera_section(self):
        """Create camera management section"""
        group = QGroupBox("Cameras")
        layout = QVBoxLayout(group)
        
        # Camera list
        self.camera_list = QListWidget()
        self.camera_list.setMaximumHeight(200)
        self.camera_list.itemClicked.connect(self.on_camera_selected)
        layout.addWidget(self.camera_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("+ Add")
        add_btn.setObjectName("primaryButton")
        add_btn.clicked.connect(self.show_add_camera_dialog)
        btn_layout.addWidget(add_btn)
        
        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self.remove_selected_camera)
        btn_layout.addWidget(self.remove_btn)
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setEnabled(False)
        self.settings_btn.clicked.connect(self.show_camera_settings)
        btn_layout.addWidget(self.settings_btn)
        
        layout.addLayout(btn_layout)
        
        return group
        
    def create_recording_section(self):
        """Create recording controls section"""
        group = QGroupBox("Recording")
        layout = QVBoxLayout(group)
        
        # Record button
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setObjectName("primaryButton")
        self.record_btn.setCheckable(True)
        self.record_btn.setEnabled(False)
        self.record_btn.toggled.connect(self.on_record_toggled)
        layout.addWidget(self.record_btn)
        
        # Quality selector
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["High (1080p)", "Medium (720p)", "Low (480p)"])
        quality_layout.addWidget(self.quality_combo)
        
        layout.addLayout(quality_layout)
        
        # Recording info
        self.recording_info = QLabel("No active recordings")
        self.recording_info.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.recording_info)
        
        return group
        
    def create_ptz_section(self):
        """Create PTZ controls section"""
        group = QGroupBox("PTZ Control")
        layout = QVBoxLayout(group)
        
        # Direction controls
        control_widget = QWidget()
        control_layout = QGridLayout(control_widget)
        control_layout.setSpacing(5)
        
        # Create PTZ buttons
        self.ptz_up = self.create_ptz_button("↑")
        self.ptz_down = self.create_ptz_button("↓")
        self.ptz_left = self.create_ptz_button("←")
        self.ptz_right = self.create_ptz_button("→")
        self.ptz_home = self.create_ptz_button("⌂")
        
        # Layout PTZ buttons
        control_layout.addWidget(self.ptz_up, 0, 1)
        control_layout.addWidget(self.ptz_left, 1, 0)
        control_layout.addWidget(self.ptz_home, 1, 1)
        control_layout.addWidget(self.ptz_right, 1, 2)
        control_layout.addWidget(self.ptz_down, 2, 1)
        
        layout.addWidget(control_widget)
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom:"))
        
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedSize(30, 30)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(0, 100)
        self.zoom_slider.setValue(0)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setFixedSize(30, 30)
        zoom_layout.addWidget(self.zoom_out_btn)
        
        layout.addLayout(zoom_layout)
        
        # Presets
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["Home", "Entrance", "Parking", "Custom 1", "Custom 2"])
        preset_layout.addWidget(self.preset_combo)
        
        self.preset_go_btn = QPushButton("Go")
        preset_layout.addWidget(self.preset_go_btn)
        
        layout.addLayout(preset_layout)
        
        return group
        
    def create_audio_section(self):
        """Create audio controls section"""
        group = QGroupBox("Audio")
        layout = QVBoxLayout(group)

        # Audio enable
        self.audio_check = QCheckBox("Enable Audio")
        self.audio_check.setEnabled(False)
        self.audio_check.setChecked(False)
        self.audio_check.stateChanged.connect(self.on_audio_check_changed)
        layout.addWidget(self.audio_check)

        # Volume control
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(0)
        self.volume_slider.setEnabled(False)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("0%")
        volume_layout.addWidget(self.volume_label)

        layout.addLayout(volume_layout)

        # Audio meter
        self.audio_meter = AudioMeter()
        self.audio_meter.setFixedHeight(20)
        layout.addWidget(self.audio_meter)

        return group
        
    def create_ptz_button(self, text):
        """Create PTZ control button"""
        btn = QPushButton(text)
        btn.setFixedSize(40, 40)
        btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: bold;
            }
        """)
        return btn
        
    def add_camera_to_list(self, camera_id, camera_name):
        """Add camera to list"""
        self.cameras[camera_id] = camera_name
        self.camera_list.addItem(camera_name)
        
    def show_add_camera_dialog(self):
        """Show add camera dialog"""
        dialog = AddCameraDialog(self)
        if dialog.exec_():
            camera_data = dialog.get_camera_data()
            self.camera_added.emit(camera_data)
            
    def remove_selected_camera(self):
        """Remove selected camera"""
        current_item = self.camera_list.currentItem()
        if current_item:
            # Find camera ID by name
            camera_name = current_item.text()
            camera_id = None
            for cid, cname in self.cameras.items():
                if cname == camera_name:
                    camera_id = cid
                    break
                    
            if camera_id:
                # Confirm removal
                reply = QMessageBox.question(
                    self, 'Remove Camera',
                    f'Remove camera "{camera_name}"?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.camera_list.takeItem(self.camera_list.row(current_item))
                    del self.cameras[camera_id]
                    self.camera_removed.emit(camera_id)
                    
                    # Clear selection
                    self.current_camera_id = None
                    self.update_controls_state()
                    
    def show_camera_settings(self):
        """Show camera settings dialog"""
        if self.current_camera_id:
            dialog = CameraSettingsDialog(
                self.current_camera_id,
                self.cameras[self.current_camera_id],
                self
            )
            if dialog.exec_():
                settings = dialog.get_settings()
                self.settings_changed.emit(self.current_camera_id, settings)
                
    def on_camera_selected(self, item):
        """Handle camera selection from list"""
        camera_name = item.text()
        for camera_id, name in self.cameras.items():
            if name == camera_name:
                self.select_camera(camera_id)
                break
                
    def select_camera(self, camera_id):
        """Select a camera"""
        self.current_camera_id = camera_id
        self.update_controls_state()
        
        # Update list selection
        camera_name = self.cameras.get(camera_id)
        if camera_name:
            items = self.camera_list.findItems(camera_name, Qt.MatchExactly)
            if items:
                self.camera_list.setCurrentItem(items[0])
                
    def update_controls_state(self):
        """Update controls based on selection"""
        has_selection = self.current_camera_id is not None
        
        self.remove_btn.setEnabled(has_selection)
        self.settings_btn.setEnabled(has_selection)
        self.record_btn.setEnabled(has_selection)
        self.audio_check.setEnabled(has_selection)
        self.volume_slider.setEnabled(has_selection and self.audio_check.isChecked())
        
    def set_ptz_enabled(self, enabled):
        """Enable/disable PTZ controls"""
        self.ptz_section.setVisible(enabled)
        
    def on_record_toggled(self, checked):
        """Handle record button toggle"""
        if self.current_camera_id:
            self.record_btn.setText("Stop Recording" if checked else "Start Recording")
            self.recording_toggled.emit(self.current_camera_id, checked)
            
    def update_recording_state(self, camera_id, is_recording):
        """Update recording state for camera"""
        if camera_id == self.current_camera_id:
            self.record_btn.setChecked(is_recording)

    def on_audio_check_changed(self, state):
        # Enable/disable volume slider
        enabled = state == Qt.Checked
        self.volume_slider.setEnabled(enabled)
        # Kamera widget'ına mute/unmute bildir
        if self.current_camera_id:
            from ui.main_window import MainWindow
            mw = self.parent()
            while mw and not isinstance(mw, MainWindow):
                mw = mw.parent()
            if mw and self.current_camera_id in mw.cameras:
                cam = mw.cameras[self.current_camera_id]
                cam.set_audio_enabled(enabled)
        # Save state
        if self.current_camera_id:
            self.audio_states[self.current_camera_id] = enabled

    def on_volume_changed(self, value):
        self.volume_label.setText(f"{value}%")
        # Kamera widget'ına volume bildir
        if self.current_camera_id:
            from ui.main_window import MainWindow
            mw = self.parent()
            while mw and not isinstance(mw, MainWindow):
                mw = mw.parent()
            if mw and self.current_camera_id in mw.cameras:
                cam = mw.cameras[self.current_camera_id]
                cam.set_audio_volume(value)
        # Save volume
        if self.current_camera_id:
            self.audio_volumes[self.current_camera_id] = value

    def select_camera(self, camera_id):
        self.current_camera_id = camera_id
        self.update_controls_state()
        # Audio state/volume yükle
        muted = self.audio_states.get(camera_id, False)
        self.audio_check.setChecked(muted)
        vol = self.audio_volumes.get(camera_id, 0)
        self.volume_slider.setValue(vol)
        self.volume_slider.setEnabled(muted)


class AddCameraDialog(QDialog):
    """Simple dialog for adding cameras"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Camera")
        self.setFixedSize(480, 360)
        self.init_ui()
        
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Camera name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Front Door")
        form_layout.addRow("Name:", self.name_edit)
        
        # RTSP URL
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("rtsp://192.168.1.100:554/stream")
        form_layout.addRow("RTSP URL:", self.url_edit)
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Optional")
        form_layout.addRow("Username:", self.username_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Optional")
        form_layout.addRow("Password:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # Test connection button
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        layout.addWidget(self.test_btn)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.add_btn = QPushButton("Add Camera")
        self.add_btn.setObjectName("primaryButton")
        self.add_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.add_btn)
        
        layout.addLayout(button_layout)
        
    def test_connection(self):
        """Test camera connection"""
        url = self.url_edit.text().strip()
        if not url:
            self.status_label.setText("Please enter RTSP URL")
            self.status_label.setStyleSheet("color: #F44336;")
            return
            
        self.status_label.setText("Testing connection...")
        self.status_label.setStyleSheet("color: #888;")
        QApplication.processEvents()
        
        # Simple connection test
        import cv2
        
        # Build URL with credentials if provided
        if self.username_edit.text() and self.password_edit.text():
            import re
            test_url = re.sub(r'(rtsp://)', rf'\1{self.username_edit.text()}:{self.password_edit.text()}@', url)
        else:
            test_url = url
            
        cap = cv2.VideoCapture(test_url)
        
        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            
            if ret:
                self.status_label.setText("✓ Connection successful")
                self.status_label.setStyleSheet("color: #4CAF50;")
            else:
                self.status_label.setText("✗ Failed to read stream")
                self.status_label.setStyleSheet("color: #F44336;")
        else:
            self.status_label.setText("✗ Failed to connect")
            self.status_label.setStyleSheet("color: #F44336;")
            
    def validate_and_accept(self):
        """Validate input and accept dialog"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a camera name")
            return
            
        if not self.url_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter RTSP URL")
            return
            
        self.accept()
        
    def get_camera_data(self):
        """Get camera data from form"""
        return {
            'name': self.name_edit.text().strip(),
            'url': self.url_edit.text().strip(),
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text().strip()
        }


class CameraSettingsDialog(QDialog):
    """Camera settings dialog"""
    
    def __init__(self, camera_id, camera_name, parent=None):
        super().__init__(parent)
        self.camera_id = camera_id
        self.camera_name = camera_name
        self.setWindowTitle(f"Camera Settings - {camera_name}")
        self.setFixedSize(480, 360)
        self.init_ui()
        
    def init_ui(self):
        """Initialize settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Camera name
        self.name_edit = QLineEdit(self.camera_name)
        form_layout.addRow("Name:", self.name_edit)
        
        # Video settings group
        video_group = QGroupBox("Video Settings")
        video_layout = QFormLayout(video_group)
        
        # Resolution
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1920x1080", "1280x720", "640x480"])
        video_layout.addRow("Resolution:", self.resolution_combo)
        
        # FPS
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["30", "25", "20", "15", "10"])
        video_layout.addRow("FPS:", self.fps_combo)
        
        # Quality
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["High", "Medium", "Low"])
        video_layout.addRow("Quality:", self.quality_combo)
        
        form_layout.addRow(video_group)
        
        # Features
        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout(features_group)
        
        self.motion_check = QCheckBox("Motion Detection")
        features_layout.addWidget(self.motion_check)
        
        self.audio_check = QCheckBox("Enable Audio")
        features_layout.addWidget(self.audio_check)
        
        self.ptz_check = QCheckBox("PTZ Camera")
        features_layout.addWidget(self.ptz_check)
        
        form_layout.addRow(features_group)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
    def get_settings(self):
        """Get settings from dialog"""
        return {
            'name': self.name_edit.text().strip(),
            'resolution': self.resolution_combo.currentText(),
            'fps': int(self.fps_combo.currentText()),
            'quality': self.quality_combo.currentText(),
            'motion_detection': self.motion_check.isChecked(),
            'audio_enabled': self.audio_check.isChecked(),
            'ptz_enabled': self.ptz_check.isChecked()
        }


class AudioMeter(QWidget):
    """Simple audio level meter"""
    
    def __init__(self):
        super().__init__()
        self.level = 0
        self.setFixedHeight(20)
        
    def set_level(self, level):
        """Set audio level (0-100)"""
        self.level = max(0, min(100, level))
        self.update()
        
    def paintEvent(self, event):
        """Paint audio meter"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(45, 45, 50))
        
        # Level bar
        if self.level > 0:
            width = int(self.width() * self.level / 100)
            
            # Color based on level
            if self.level < 60:
                color = QColor(76, 175, 80)  # Green
            elif self.level < 80:
                color = QColor(255, 193, 7)  # Yellow
            else:
                color = QColor(244, 67, 54)  # Red
                
            painter.fillRect(0, 0, width, self.height(), color)