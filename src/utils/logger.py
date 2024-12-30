import logging
from datetime import datetime
from pathlib import Path

class DTNLogger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        Path("logs").mkdir(exist_ok=True)
        
        # Set up file handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(f"logs/dtn_simulation_{timestamp}.log")
        file_handler.setLevel(logging.INFO)
        
        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Set up logger
        self.logger = logging.getLogger('DTNSimulation')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log_bundle_event(self, event_type: str, bundle_id: str, 
                        current_node: str, next_node: str = None, 
                        status: str = None, details: dict = None):
        """Log bundle-related events with detailed information."""
        msg = f"Bundle {bundle_id} - {event_type} at {current_node}"
        if next_node:
            msg += f" -> {next_node}"
        if status:
            msg += f" ({status})"
        if details:
            msg += f"\nDetails: {details}"
        
        self.logger.info(msg)
        
    def log_network_event(self, event_type: str, details: dict):
        """Log network-related events."""
        self.logger.info(f"Network Event - {event_type}: {details}")
