import uuid
import logging

logger = logging.getLogger(__name__)


class CameraManager:
    """Simple camera manager"""
    
    def __init__(self):
        self.cameras = {}
        
    def generate_id(self):
        """Generate unique camera ID"""
        return str(uuid.uuid4())[:8]
        
    def add_camera(self, camera_data):
        """Add camera"""
        camera_id = camera_data.get('id', self.generate_id())
        self.cameras[camera_id] = camera_data
        logger.info(f"Added camera: {camera_data['name']} ({camera_id})")
        return camera_id
        
    def remove_camera(self, camera_id):
        """Remove camera"""
        if camera_id in self.cameras:
            camera_name = self.cameras[camera_id].get('name', 'Unknown')
            del self.cameras[camera_id]
            logger.info(f"Removed camera: {camera_name} ({camera_id})")
            
    def get_camera(self, camera_id):
        """Get camera by ID"""
        return self.cameras.get(camera_id)
        
    def get_all_cameras(self):
        """Get all cameras"""
        return list(self.cameras.values())