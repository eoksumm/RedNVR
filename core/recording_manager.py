import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class RecordingManager:
    """Simple recording manager"""
    
    def __init__(self):
        self.recordings = {}
        self.recording_path = Path("recordings")
        self.recording_path.mkdir(exist_ok=True)
        
    def start_recording(self, camera_id, camera_name):
        """Start recording for camera"""
        if camera_id not in self.recordings:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{camera_name}_{timestamp}.mp4"
            filepath = self.recording_path / filename
            
            self.recordings[camera_id] = {
                'filename': filename,
                'filepath': str(filepath),
                'start_time': datetime.now(),
                'status': 'recording'
            }
            
            logger.info(f"Started recording: {filename}")
            return filepath
            
    def stop_recording(self, camera_id):
        """Stop recording for camera"""
        if camera_id in self.recordings:
            recording = self.recordings[camera_id]
            recording['end_time'] = datetime.now()
            recording['status'] = 'completed'
            
            duration = recording['end_time'] - recording['start_time']
            logger.info(f"Stopped recording: {recording['filename']} (Duration: {duration})")
            
            del self.recordings[camera_id]
            
    def stop_all(self):
        """Stop all recordings"""
        camera_ids = list(self.recordings.keys())
        for camera_id in camera_ids:
            self.stop_recording(camera_id)
            
    def get_recordings(self):
        """Get list of recorded files"""
        recordings = []
        for file in self.recording_path.glob("*.mp4"):
            recordings.append({
                'filename': file.name,
                'filepath': str(file),
                'size': file.stat().st_size,
                'created': datetime.fromtimestamp(file.stat().st_ctime)
            })
        return sorted(recordings, key=lambda x: x['created'], reverse=True)


# ui/__init__.py
# Empty file to make ui a package
