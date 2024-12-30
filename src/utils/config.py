import yaml
from pathlib import Path

class ConfigLoader:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from settings.yaml"""
        try:
            config_path = Path("config/settings.yaml")
            with open(config_path, "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print("Error: settings.yaml not found!")
            return None
            
    def get_simulation_params(self):
        """Get simulation parameters"""
        if not self.config:
            return None
        return self.config.get("simulation", {})
        
    def get_visualization_params(self):
        """Get visualization parameters"""
        if not self.config:
            return None
        return self.config.get("visualization", {})
