from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Bundle:
    source: str
    destination: str
    payload: str
    creation_timestamp: datetime = None
    id: Optional[str] = None
    priority: int = 1
    
    def __post_init__(self):
        if self.creation_timestamp is None:
            self.creation_timestamp = datetime.now()
        if self.id is None:
            self.id = f"bundle_{self.creation_timestamp.strftime('%H%M%S')}"
            
    def __str__(self):
        return f"Bundle {self.id}: {self.source} -> {self.destination}"
        
    def size(self) -> int:
        """Return bundle size in bytes"""
        return len(self.payload.encode())

class DTNNode:
    def __init__(self, node_id: str):
        self.id = node_id
        self.buffer = []
        self.max_buffer_size = 1024 * 1024  # 1MB default
        
    def store_bundle(self, bundle: Bundle) -> bool:
        """Store bundle in node's buffer"""
        if len(self.buffer) * 1024 < self.max_buffer_size:  # Assuming 1KB per bundle
            self.buffer.append(bundle)
            return True
        return False
        
    def forward_bundle(self) -> Optional[Bundle]:
        """Forward next bundle from buffer"""
        if self.buffer:
            return self.buffer.pop(0)
        return None