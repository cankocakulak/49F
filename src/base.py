from abc import ABC, abstractmethod
from typing import Dict, List, Set

class NetworkSimulatorBase(ABC):
    @abstractmethod
    def setup_mars_earth_network(self):
        pass
        
    @abstractmethod
    def simulate_transmission(self, message: str, source: str, destination: str):
        pass

class VisualizerBase(ABC):
    @abstractmethod
    def create_network_graph(self, nodes: List[str], connections: List[tuple]):
        pass
        
    @abstractmethod
    def update_simulation_state(self, current_path: List[str], 
                              current_node: str,
                              disrupted_links: Set[tuple],
                              bundle_info: Dict):
        pass
        
    @abstractmethod
    def visualize_network(self, title: str):
        pass
