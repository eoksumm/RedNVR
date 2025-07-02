from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import numpy as np
from datetime import datetime
import logging
import ffmpeg
import pyaudio
import threading
import subprocess

logger = logging.getLogger(__name__)


class CameraWidget(QWidget):
    """Individual camera display widget"""
    
    # Signals
    selected = pyqtSignal(str)  # camera_id
    recording_toggled = pyqtSignal(str, bool)  # camera_id, is_recording
    snapshot_taken = pyqtSignal(str, str)  # camera_id, filepath
    error_occurred = pyqtSignal(str, str)  # camera_id, error
    double_clicked = pyqtSignal(str)  # camera_id
    
    def __init__(self, camera_id, name, url, username="", password=""):
        super().__init__()
        self.camera_id = camera_id
        self.name = name
        self.url = url
        self.username = username
        self.password = password
        
        self.is_recording = False
        self.is_selected = False
        self.has_ptz = False  # Will be detected from camera
        self.current_frame = None
        self.audio_enabled = False  # Default muted
        self.audio_volume = 0       # Default 0
        
        # Video capture
        self.capture_thread = None
        self.capture = None
        
        self.setObjectName("cameraWidget")
        self.init_ui()
        self.start()
        
    def init_ui(self):
        """Initialize UI"""
        self.setMinimumSize(320, 240)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Video container
        self.video_container = QWidget()
        self.video_container.setObjectName("videoContainer")
        video_layout = QVBoxLayout(self.video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        # Video display
        self.video_label = VideoLabel()
        self.video_label.setScaledContents(True)
        self.video_label.setStyleSheet("background-color: #000;")
        self.video_label.clicked.connect(lambda: self.selected.emit(self.camera_id))
        self.video_label.double_clicked.connect(lambda: self.double_clicked.emit(self.camera_id))
        video_layout.addWidget(self.video_label)
        
        # Overlay container
        self.overlay = OverlayWidget(self.video_label)
        self.overlay.snapshot_clicked.connect(self.take_snapshot)
        self.overlay.record_clicked.connect(self.toggle_recording)
        
        layout.addWidget(self.video_container)
        
        # Bottom bar
        self.bottom_bar = QWidget()
        self.bottom_bar.setFixedHeight(30)
        self.bottom_bar.setObjectName("cameraBottomBar")
        
        bottom_layout = QHBoxLayout(self.bottom_bar)
        bottom_layout.setContentsMargins(10, 0, 10, 0)
        
        # Camera name
        self.name_label = QLabel(self.name)
        self.name_label.setObjectName("cameraTitle")
        bottom_layout.addWidget(self.name_label)
        
        bottom_layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("color: #4CAF50;")
        bottom_layout.addWidget(self.status_indicator)
        
        # Recording indicator
        self.recording_indicator = QLabel("● REC")
        self.recording_indicator.setObjectName("recordingIndicator")
        self.recording_indicator.setVisible(False)
        bottom_layout.addWidget(self.recording_indicator)
        
        layout.addWidget(self.bottom_bar)
        
        # Apply styling
        self.setStyleSheet("""
            #cameraWidget {
                background-color: #2D2D32;
                border-radius: 8px;
            }
            #cameraBottomBar {
                background-color: #232328;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
            #videoContainer {
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
        """)
        
    def start(self):
        """Start video capture"""
        self.capture_thread = CaptureThread(self.url, self.username, self.password, self.audio_enabled, self.audio_volume)
        self.capture_thread.frame_ready.connect(self.update_frame)
        self.capture_thread.error.connect(self.handle_error)
        self.capture_thread.start()
        
    def stop(self):
        """Stop video capture"""
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread.wait()
            
    def update_frame(self, frame):
        """Update video frame"""
        self.current_frame = frame
        
        # Convert to QImage
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # Scale to widget size
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.video_label.setPixmap(scaled_pixmap)
        
        # Update status
        self.status_indicator.setStyleSheet("color: #4CAF50;")
        
    def handle_error(self, error_msg):
        """Handle capture error"""
        self.status_indicator.setStyleSheet("color: #F44336;")
        self.error_occurred.emit(self.camera_id, error_msg)
        
        # Show error on video
        self.video_label.setText(f"Connection Error\n{error_msg}")
        self.video_label.setStyleSheet("""
            background-color: #000;
            color: #F44336;
            font-size: 14px;
        """)
        
    def take_snapshot(self):
        """Take snapshot of current frame"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"snapshot_{self.name}_{timestamp}.jpg"
            filepath = f"recordings/{filename}"
            
            # Convert RGB to BGR for cv2
            bgr_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(filepath, bgr_frame)
            
            self.snapshot_taken.emit(self.camera_id, filepath)
            
            # Show feedback
            self.overlay.show_feedback("Snapshot saved!")
            
    def toggle_recording(self):
        """Toggle recording state"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
            
    def start_recording(self):
        """Start recording"""
        self.is_recording = True
        self.recording_indicator.setVisible(True)
        self.overlay.set_recording(True)
        self.recording_toggled.emit(self.camera_id, True)
        
        # Start actual recording
        if self.capture_thread:
            self.capture_thread.start_recording(self.name)
            
    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        self.recording_indicator.setVisible(False)
        self.overlay.set_recording(False)
        self.recording_toggled.emit(self.camera_id, False)
        
        # Stop actual recording
        if self.capture_thread:
            self.capture_thread.stop_recording()
            
    def set_selected(self, selected):
        """Set selection state"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                #cameraWidget {
                    background-color: #2D2D32;
                    border-radius: 8px;
                    border: 2px solid #EB3B5A;
                }
            """)
        else:
            self.setStyleSheet("""
                #cameraWidget {
                    background-color: #2D2D32;
                    border-radius: 8px;
                }
            """)
            
    def update_settings(self, settings):
        """Update camera settings"""
        self.name = settings.get('name', self.name)
        self.url = settings.get('url', self.url)
        self.username = settings.get('username', self.username)
        self.password = settings.get('password', self.password)
        
        self.name_label.setText(self.name)
        
        # Restart capture with new settings
        self.stop()
        self.start()
        
    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        if hasattr(self, 'overlay'):
            self.overlay.resize(self.video_label.size())
            
    def set_audio_enabled(self, enabled):
        self.audio_enabled = enabled
        if self.capture_thread:
            self.capture_thread.set_audio_enabled(enabled)

    def set_audio_volume(self, volume):
        self.audio_volume = volume
        if self.capture_thread:
            self.capture_thread.set_audio_volume(volume)


class VideoLabel(QLabel):
    """Custom label for video display with click support"""
    
    clicked = pyqtSignal()
    double_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit()


class OverlayWidget(QWidget):
    """Overlay widget for camera controls"""
    
    snapshot_clicked = pyqtSignal()
    record_clicked = pyqtSignal()
    
    def __init__(self, parent):
        super().__init__(parent)
        self.is_recording = False
        self.feedback_timer = QTimer()
        self.feedback_timer.timeout.connect(self.hide_feedback)
        
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.init_ui()
        
    def init_ui(self):
        """Initialize overlay UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Top row - controls
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        
        # Snapshot button
        self.snapshot_btn = QPushButton()
        self.snapshot_btn.setFixedSize(36, 36)
        self.snapshot_btn.setIcon(self.create_icon("camera"))
        self.snapshot_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(45, 45, 50, 0.8);
                border: none;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: rgba(61, 61, 66, 0.9);
            }
        """)
        self.snapshot_btn.clicked.connect(self.snapshot_clicked.emit)
        top_layout.addWidget(self.snapshot_btn)
        
        # Record button
        self.record_btn = QPushButton()
        self.record_btn.setFixedSize(36, 36)
        self.record_btn.setIcon(self.create_icon("record"))
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(45, 45, 50, 0.8);
                border: none;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: rgba(61, 61, 66, 0.9);
            }
        """)
        self.record_btn.clicked.connect(self.record_clicked.emit)
        top_layout.addWidget(self.record_btn)
        
        layout.addLayout(top_layout)
        layout.addStretch()
        
        # Feedback label
        self.feedback_label = QLabel()
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setStyleSheet("""
            background-color: rgba(235, 59, 90, 0.9);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 500;
        """)
        self.feedback_label.hide()
        layout.addWidget(self.feedback_label, 0, Qt.AlignCenter)
        
        layout.addStretch()
        
        # Initially hide controls
        self.setVisible(False)
        
    def create_icon(self, name):
        """Create icon"""
        icon = QIcon()
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(Qt.NoBrush)
        
        if name == "camera":
            # Camera icon
            painter.drawRect(6, 8, 12, 10)
            painter.drawEllipse(10, 11, 4, 4)
            painter.drawLine(9, 8, 11, 6)
            painter.drawLine(11, 6, 13, 6)
            painter.drawLine(13, 6, 15, 8)
        elif name == "record":
            # Record icon
            if self.is_recording:
                painter.setBrush(QBrush(Qt.red))
                painter.drawRect(8, 8, 8, 8)
            else:
                painter.setBrush(QBrush(Qt.red))
                painter.drawEllipse(8, 8, 8, 8)
                
        painter.end()
        icon.addPixmap(pixmap)
        return icon
        
    def set_recording(self, recording):
        """Set recording state"""
        self.is_recording = recording
        self.record_btn.setIcon(self.create_icon("record"))
        if recording:
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(235, 59, 90, 0.8);
                    border: none;
                    border-radius: 18px;
                }
                QPushButton:hover {
                    background-color: rgba(235, 59, 90, 0.8); /* Hover'da da kırmızı kalacak */
                }
            """)
        else:
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(45, 45, 50, 0.8);
                    border: none;
                    border-radius: 18px;
                }
                QPushButton:hover {
                    background-color: rgba(61, 61, 66, 0.9);
                }
            """)
            
    def show_feedback(self, message):
        """Show feedback message"""
        self.feedback_label.setText(message)
        self.feedback_label.show()
        self.feedback_timer.start(2000)
        
    def hide_feedback(self):
        """Hide feedback message"""
        self.feedback_label.hide()
        self.feedback_timer.stop()
        
    def enterEvent(self, event):
        """Show controls on hover"""
        self.setVisible(True)
        
    def leaveEvent(self, event):
        """Hide controls on leave"""
        self.setVisible(False)


class CaptureThread(QThread):
    """Thread for video capture"""
    
    frame_ready = pyqtSignal(np.ndarray)
    error = pyqtSignal(str)
    
    def __init__(self, url, username="", password="", audio_enabled=False, audio_volume=0):
        super().__init__()
        self.url = url
        self.username = username
        self.password = password
        self.running = True
        self.recording = False
        self.video_writer = None
        self.audio_thread = None
        self.audio_running = False
        self.audio_process = None
        self.pyaudio_instance = None
        self.audio_stream = None
        self.audio_enabled = audio_enabled
        self.audio_volume = audio_volume
        self._audio_muted = not audio_enabled

    def run(self):
        """Run capture loop"""
        # Build URL with credentials
        if self.username and self.password:
            import re
            self.url = re.sub(r'(rtsp://)', rf'\1{self.username}:{self.password}@', self.url)
            
        # Open capture
        cap = cv2.VideoCapture(self.url)
        
        if not cap.isOpened():
            self.error.emit("Failed to connect to camera")
            return
            
        # Set buffer size to reduce latency
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Ses thread'ini başlat
        self.audio_running = True
        self.audio_thread = threading.Thread(target=self.play_audio, daemon=True)
        self.audio_thread.start()
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Emit frame
                self.frame_ready.emit(rgb_frame)
                
                # Record if enabled
                if self.recording and self.video_writer:
                    self.video_writer.write(frame)
                    
                # Small delay to control frame rate
                self.msleep(33)  # ~30 FPS
            else:
                self.error.emit("Failed to read frame")
                self.msleep(1000)  # Wait before retry
                
                # Try to reconnect
                cap.release()
                cap = cv2.VideoCapture(self.url)
                
        # Cleanup
        cap.release()
        if self.video_writer:
            self.video_writer.release()
        self.audio_running = False
        if self.audio_thread:
            self.audio_thread.join(timeout=2)
        try:
            if self.audio_stream:
                if hasattr(self.audio_stream, 'is_active') and self.audio_stream.is_active():
                    self.audio_stream.stop_stream()
                self.audio_stream.close()
        except Exception:
            pass
        try:
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
        except Exception:
            pass
        try:
            if self.audio_process:
                self.audio_process.terminate()
        except Exception:
            pass

    def set_audio_enabled(self, enabled):
        self.audio_enabled = enabled
        self._audio_muted = not enabled

    def set_audio_volume(self, volume):
        self.audio_volume = volume
        # pyaudio volume ayarı için (destekliyorsa)
        if self.audio_stream:
            try:
                self.audio_stream._volume = volume / 100.0
            except Exception:
                pass

    def play_audio(self):
        """RTSP ses akışını ffmpeg ile çekip pyaudio ile oynat"""
        # ffmpeg komutu: sadece ses streamini PCM olarak çıkar
        # Not: ffmpeg'in sistemde kurulu olması gerekir
        if self.username and self.password:
            import re
            url = re.sub(r'(rtsp://)', rf'\\1{self.username}:{self.password}@', self.url)
        else:
            url = self.url
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', url,
            '-vn',  # video yok
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            '-f', 's16le',
            '-loglevel', 'quiet',
            '-'
        ]
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            self.audio_stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=2,
                rate=44100,
                output=True
            )
            self.audio_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=4096)
            while self.audio_running:
                data = self.audio_process.stdout.read(4096)
                if not data:
                    break
                # Mute kontrolü
                if self._audio_muted or self.audio_volume == 0:
                    self.audio_stream.write(b'\x00' * len(data))
                else:
                    # Volume ayarı (basit çarpan)
                    import array
                    arr = array.array('h', data)
                    factor = self.audio_volume / 100.0
                    arr = array.array('h', [int(s * factor) for s in arr])
                    self.audio_stream.write(arr.tobytes())
        except Exception as e:
            logger.error(f"Audio playback error: {e}")
        finally:
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
            if self.audio_process:
                self.audio_process.terminate()

    def stop(self):
        """Stop capture"""
        self.running = False
        self.audio_running = False
        self.wait()
        
    def start_recording(self, camera_name):
        """Start recording video"""
        if not self.recording:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/{camera_name}_{timestamp}.mp4"
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filename, fourcc, 30.0, (1920, 1080))
            
            self.recording = True
            logger.info(f"Started recording: {filename}")
            
    def stop_recording(self):
        """Stop recording video"""
        if self.recording:
            self.recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            logger.info("Stopped recording")