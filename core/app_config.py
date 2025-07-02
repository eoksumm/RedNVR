import json
from pathlib import Path


class AppConfig:
    """Simple application configuration"""
    
    def __init__(self):
        self.config_file = Path("config/app_config.json")
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
                
        # Default configuration
        return {
            'theme': 'dark',
            'recording_path': 'recordings',
            'recording_quality': 'high',
            'recording_format': 'mp4',
            'default_fps': 30,
            'enable_audio': True,
            'motion_detection': False,
            'auto_start': True
        }
        
    def save_config(self):
        """Save configuration to file"""
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
        
    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
