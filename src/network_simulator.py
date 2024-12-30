import json
from datetime import datetime, timedelta
import time
from src.dtn_core import DTNNode, Bundle
from src.visualization import DTNVisualizer

class SimpleNetworkSimulator:
    def __init__(self):
        self.nodes = {}
        self.visualizer = DTNVisualizer()
        self.topology = self.load_topology()
        
    def load_topology(self):
        """Load network topology from JSON file."""
        try:
            with open('data/network_topologies/mars_earth.json', 'r') as f:
                topology = json.load(f)
                print("Network topology loaded successfully")
                return topology
        except FileNotFoundError:
            print("Error: Topology file not found!")
            return None
        
    def add_node(self, node_id: str) -> None:
        """Ağa yeni bir düğüm ekle."""
        self.nodes[node_id] = DTNNode(node_id)
        
    def setup_mars_earth_network(self):
        """Setup network using loaded topology."""
        if not self.topology:
            return False
            
        # Create nodes
        for node in self.topology['nodes']:
            self.add_node(node['id'])
            
        # Create connections list for visualization
        connections = [(link['source'], link['target']) 
                      for link in self.topology['links']]
        
        # Setup visualization
        node_ids = [node['id'] for node in self.topology['nodes']]
        self.visualizer.create_network_graph(node_ids, connections)
        
        return True
        
    def simulate_transmission(self, message: str):
        """Simulate transmission using topology data."""
        if not self.topology:
            print("Error: No topology loaded!")
            return
            
        path = ["mars_rover", "mars_orbiter", "relay_satellite", "earth_station"]
        
        bundle = Bundle(
            source=path[0],
            destination=path[-1],
            payload=message
        )
        
        # Get delays and distances from topology
        delays = {(link['source'], link['target']): link['delay'] 
                 for link in self.topology['links']}
        distances = {(link['source'], link['target']): link['distance'] 
                    for link in self.topology['links']}
        
        # Calculate totals
        total_delay = sum(delays.get((path[i], path[i+1]), 0) 
                         for i in range(len(path)-1))
        total_distance = sum(link['distance_km'] 
                           for link in self.topology['links'])
        
        bundle_info = {
            "source": bundle.source,
            "destination": bundle.destination,
            "timestamp": bundle.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "total_delay": f"{total_delay//60} minutes {total_delay%60} seconds",
            "total_distance": f"{total_distance:,} km",
            "delays": delays,
            "distances": distances,
            "topology": self.topology
        }
        
        print("\nStarting Bundle Transmission Simulation...")
        print(f"Total transmission time: {bundle_info['total_delay']}")
        print(f"Total distance: {bundle_info['total_distance']}")
        print("Use left/right arrow keys to navigate through steps")
        print("Press 'q' to quit the simulation")
        
        self.visualizer.simulate_transmission(path, bundle_info)
        
        print("\nSimulation ended!")