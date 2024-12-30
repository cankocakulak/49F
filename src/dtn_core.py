from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

@dataclass
class Bundle:
    """DTN'de kullanılacak temel veri paketi."""
    source: str
    destination: str
    payload: Any
    creation_timestamp: datetime = datetime.now()
    expiry: Optional[datetime] = None

class DTNNode:
    """DTN ağındaki bir düğümü temsil eder."""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.storage = []  # Store-and-Forward için basit depolama

    def receive_bundle(self, bundle: Bundle) -> bool:
        """Bundle'ı al ve depola."""
        if bundle.destination == self.node_id:
            print(f"Bundle delivered to destination: {self.node_id}")
            return True
        self.storage.append(bundle)
        return True

    def forward_bundle(self, next_hop: 'DTNNode') -> bool:
        """Depolanan bundle'ı ilet."""
        if not self.storage:
            return False
        
        bundle = self.storage.pop(0)
        return next_hop.receive_bundle(bundle)