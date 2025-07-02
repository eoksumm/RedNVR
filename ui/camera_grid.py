from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math


class CameraGrid(QWidget):
    """Dynamic camera grid widget"""
    
    camera_selected = pyqtSignal(str)  # camera_id
    
    def __init__(self):
        super().__init__()
        self.cameras = []  # List of camera widgets
        self.selected_camera = None
        self.layout_mode = 'grid'  # grid, single, 2x2
        self.before_layout_change = lambda: None
        self.after_layout_change = lambda: None
        self.init_ui()
        
    def init_ui(self):
        """Initialize grid UI"""
        # Create scroll area for cameras
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget
        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setSpacing(10)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll_area.setWidget(self.container)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll_area)
        
        # Empty state
        self.empty_label = QLabel("No cameras added\n\nClick '+ Add' to add a camera")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("""
            color: #666;
            font-size: 16px;
            padding: 40px;
        """)
        self.grid_layout.addWidget(self.empty_label, 0, 0, Qt.AlignCenter)
        
    def add_camera(self, camera_widget):
        """Add camera to grid"""
        # Remove empty state if this is the first camera
        if len(self.cameras) == 0:
            self.empty_label.setParent(None)
            
        # Connect signals
        camera_widget.selected.connect(self.on_camera_selected)
        camera_widget.double_clicked.connect(self.on_camera_double_clicked)
        
        # Add to list
        self.cameras.append(camera_widget)
        
        # Update layout
        self.update_layout()
        
    def remove_camera(self, camera_widget):
        """Remove camera from grid"""
        if camera_widget in self.cameras:
            # Remove from layout
            self.grid_layout.removeWidget(camera_widget)
            camera_widget.setParent(None)
            
            # Remove from list
            self.cameras.remove(camera_widget)
            
            # Update layout
            self.update_layout()
            
            # Show empty state if no cameras left
            if len(self.cameras) == 0:
                self.grid_layout.addWidget(self.empty_label, 0, 0, Qt.AlignCenter)
                
    def set_layout_mode(self, mode):
        """Set layout mode (grid, single, 2x2)"""
        self.layout_mode = mode
        self.update_layout()
        
    def update_layout(self):
        """Update camera layout based on mode"""
        if not self.cameras:
            return
        self.before_layout_change()
        # Tüm kameraları gizle (flash engelleme)
        for cam in self.cameras:
            cam.hide()
        # Clear current layout
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        if self.layout_mode == 'grid':
            self.setup_grid_layout()
        elif self.layout_mode == 'single':
            self.setup_single_layout()
        elif self.layout_mode == '2x2':
            self.setup_2x2_layout()
        self.after_layout_change()
            
    def setup_grid_layout(self):
        """Setup dynamic grid layout"""
        count = len(self.cameras)
        if count == 0:
            return
            
        # Calculate grid dimensions
        if count == 1:
            cols = 1
            rows = 1
        elif count == 2:
            cols = 2
            rows = 1
        elif count <= 4:
            cols = 2
            rows = 2
        elif count <= 9:
            cols = 3
            rows = math.ceil(count / 3)
        else:
            cols = 4
            rows = math.ceil(count / 4)
            
        # Calculate size for each camera
        available_width = self.scroll_area.width() - 40  # Account for margins and scrollbar
        available_height = self.scroll_area.height() - 40
        
        camera_width = (available_width - (cols - 1) * 10) // cols
        camera_height = (available_height - (rows - 1) * 10) // rows
        
        # Maintain aspect ratio (16:9)
        aspect_ratio = 16 / 9
        if camera_width / camera_height > aspect_ratio:
            camera_width = int(camera_height * aspect_ratio)
        else:
            camera_height = int(camera_width / aspect_ratio)
            
        # Place cameras in grid
        for i, camera in enumerate(self.cameras):
            row = i // cols
            col = i % cols
            
            camera.setFixedSize(camera_width, camera_height)
            self.grid_layout.addWidget(camera, row, col)
            camera.show()

    def setup_single_layout(self):
        """Setup single camera layout"""
        if self.selected_camera and self.selected_camera in self.cameras:
            camera = self.selected_camera
        else:
            camera = self.cameras[0]
            
        # Hide all cameras except selected (zaten update_layout başında gizlendi)
                
        # Size camera to fill available space
        available_width = self.scroll_area.width() - 20
        available_height = self.scroll_area.height() - 20
        
        # Maintain aspect ratio
        aspect_ratio = 16 / 9
        if available_width / available_height > aspect_ratio:
            width = int(available_height * aspect_ratio)
            height = available_height
        else:
            width = available_width
            height = int(available_width / aspect_ratio)
            
        camera.setFixedSize(width, height)
        self.grid_layout.addWidget(camera, 0, 0, Qt.AlignCenter)
        camera.show()

    def setup_2x2_layout(self):
        """Setup 2x2 layout"""
        # Show only first 4 cameras
        visible_cameras = self.cameras[:4]
        
        # Hide other cameras (zaten update_layout başında gizlendi)
            
        # Calculate size
        available_width = self.scroll_area.width() - 30
        available_height = self.scroll_area.height() - 30
        
        camera_width = (available_width - 10) // 2
        camera_height = (available_height - 10) // 2
        
        # Maintain aspect ratio
        aspect_ratio = 16 / 9
        if camera_width / camera_height > aspect_ratio:
            camera_width = int(camera_height * aspect_ratio)
        else:
            camera_height = int(camera_width / aspect_ratio)
            
        # Place cameras
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for i, camera in enumerate(visible_cameras):
            row, col = positions[i]
            camera.setFixedSize(camera_width, camera_height)
            self.grid_layout.addWidget(camera, row, col)
            camera.show()
            
    def on_camera_selected(self, camera_id):
        """Handle camera selection"""
        # Find camera widget
        for camera in self.cameras:
            if camera.camera_id == camera_id:
                # Update selection
                if self.selected_camera:
                    self.selected_camera.set_selected(False)
                    
                self.selected_camera = camera
                camera.set_selected(True)
                
                # Emit signal
                self.camera_selected.emit(camera_id)
                break
                
    def on_camera_double_clicked(self, camera_id):
        """Handle camera double click"""
        # Toggle single/grid view
        if self.layout_mode == 'single' and self.selected_camera and self.selected_camera.camera_id == camera_id:
            self.set_layout_mode('grid')
        else:
            self.set_layout_mode('single')
            self.on_camera_selected(camera_id)
        
    def resizeEvent(self, event):
        """Handle resize event"""
        super().resizeEvent(event)
        # Update layout when resized
        QTimer.singleShot(100, self.update_layout)