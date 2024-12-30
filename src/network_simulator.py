from datetime import datetime
from src.dtn_core import DTNNode, Bundle
from src.visualization import DTNVisualizer

class SimpleNetworkSimulator:
    def __init__(self):
        self.nodes = {}
        self.visualizer = DTNVisualizer()
    
    def add_node(self, node_id: str) -> None:
        """Ağa yeni bir düğüm ekle."""
        self.nodes[node_id] = DTNNode(node_id)
        
    def setup_mars_earth_network(self):
        """Mars-Dünya ağını kur ve görselleştir."""
        # Düğümleri oluştur
        nodes = ["mars_rover", "mars_orbiter", "relay_satellite", "earth_station"]
        for node in nodes:
            self.add_node(node)
            
        # Bağlantıları tanımla
        connections = [
            ("mars_rover", "mars_orbiter"),
            ("mars_orbiter", "relay_satellite"),
            ("relay_satellite", "earth_station")
        ]
        
        # Görselleştirme için ağı oluştur
        self.visualizer.create_network_graph(nodes, connections)
        
    def simulate_transmission(self, message: str):
        """Simulate transmission with interactive visualization."""
        path = ["mars_rover", "mars_orbiter", "relay_satellite", "earth_station"]
        
        bundle = Bundle(
            source="mars_rover",
            destination="earth_station",
            payload=message
        )
        
        bundle_info = {
            "source": bundle.source,
            "destination": bundle.destination,
            "timestamp": bundle.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("\nStarting Bundle Transmission Simulation...")
        print("Use left/right arrow keys to navigate through steps")
        print("Press 'q' to quit the simulation")
        
        self.visualizer.simulate_transmission(path, bundle_info)
        
        print("\nSimulation ended!")