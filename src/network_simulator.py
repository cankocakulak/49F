import json
from datetime import datetime, timedelta
import time
from src.dtn_core import DTNNode, Bundle
from src.visualization import DTNVisualizer
from src.performance_metrics import DTNMetricsAnalyzer
import numpy as np
from src.utils.config import ConfigLoader
import random
from src.utils.logger import DTNLogger
import networkx as nx

class SimpleNetworkSimulator:
    def __init__(self):
        self.nodes = {}
        self.config = ConfigLoader()
        self.logger = DTNLogger()
        self.visualizer = DTNVisualizer(self.config)
        self.topology = self.load_topology()
        self.buffer = {}
        self.network_graph = self._build_network_graph()
        
    def _build_network_graph(self):
        """Build a NetworkX graph from topology for path finding."""
        G = nx.Graph()
        for link in self.topology["links"]:
            G.add_edge(link["source"], link["target"], 
                      delay=link["delay"],
                      distance=link["distance"])
        return G
        
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
        
    def simulate_transmission(self, message: str, source: str = "mars_rover_1", 
                            destination: str = "earth_station_1"):
        """Run automated simulation with retry mechanism and store-and-forward."""
        bundle_id = f"bundle_{datetime.now().strftime('%H%M%S')}"
        bundle = Bundle(
            id=bundle_id,
            source=source,
            destination=destination,
            payload=message,
            creation_timestamp=datetime.now()
        )
        
        # Find all possible paths
        all_paths = list(nx.all_simple_paths(self.network_graph, source, destination))
        paths_with_delays = []
        for path in all_paths:
            total_path_delay = sum(self.network_graph[path[i]][path[i+1]]["delay"] 
                                 for i in range(len(path)-1))
            paths_with_delays.append((path, total_path_delay))
        
        paths_with_delays.sort(key=lambda x: x[1])
        
        self.logger.log_network_event("PathsFound", {
            "num_paths": len(all_paths),
            "paths": all_paths,
            "delays": {str(p): d for p, d in paths_with_delays}
        })
        
        # Simulation state
        disrupted_links = set()
        total_delay = 0
        retransmissions = 0
        successful_delivery = False
        max_retries_per_link = 3
        stored_bundles = {node: [] for node in self.network_graph.nodes()}
        
        while not successful_delivery:
            for current_path, estimated_delay in paths_with_delays:
                if successful_delivery:
                    break
                    
                self.logger.log_network_event("AttemptingPath", {
                    "path": current_path,
                    "bundle": bundle_id,
                    "estimated_delay": estimated_delay
                })
                
                i = 0
                while i < len(current_path) - 1:
                    current_node = current_path[i]
                    next_node = current_path[i + 1]
                    
                    # Check if link is currently disrupted
                    if (current_node, next_node) in disrupted_links:
                        retry_count = 0
                        while retry_count < max_retries_per_link:
                            self.logger.log_bundle_event(
                                "RetryingDisruptedLink",
                                bundle_id,
                                current_node,
                                next_node,
                                f"Attempt {retry_count + 1}/{max_retries_per_link}"
                            )
                            
                            # Store bundle if not already stored
                            if bundle not in stored_bundles[current_node]:
                                stored_bundles[current_node].append(bundle)
                                self.logger.log_bundle_event(
                                    "StoredBundle",
                                    bundle_id,
                                    current_node,
                                    details={"buffer_size": len(stored_bundles[current_node])}
                                )
                            
                            # Simulate waiting for link recovery
                            time.sleep(2)
                            
                            # Check if link recovers
                            if random.random() > self.config.get_simulation_params()["network"]["error_rate"]:
                                disrupted_links.remove((current_node, next_node))
                                stored_bundles[current_node].remove(bundle)
                                self.logger.log_bundle_event(
                                    "LinkRecovered",
                                    bundle_id,
                                    current_node,
                                    next_node
                                )
                                break
                            
                            retry_count += 1
                            retransmissions += 1
                            
                            # Update visualization during retries
                            self.visualizer.update_simulation_state(
                                current_path=current_path,
                                current_node=current_node,
                                disrupted_links=disrupted_links,
                                bundle_info={
                                    "id": bundle_id,
                                    "total_delay": total_delay,
                                    "retransmissions": retransmissions,
                                    "status": f"Retrying ({retry_count}/{max_retries_per_link})",
                                    "stored_bundles": {k: len(v) for k, v in stored_bundles.items()},
                                    "current_path_index": f"Path {paths_with_delays.index((current_path, estimated_delay)) + 1}/{len(paths_with_delays)}"
                                }
                            )
                        
                        if (current_node, next_node) in disrupted_links:
                            # If max retries reached, try next path
                            break
                    
                    # Attempt transmission
                    link_delay = self.network_graph[current_node][next_node]["delay"]
                    distance = self.network_graph[current_node][next_node]["distance"]
                    
                    # Distance-based disruption probability
                    base_error_rate = self.config.get_simulation_params()["network"]["error_rate"]
                    distance_factor = 1.0 if "km" in distance else 1.5
                    
                    if random.random() < (base_error_rate * distance_factor):
                        disrupted_links.add((current_node, next_node))
                        self.logger.log_bundle_event(
                            "Disruption",
                            bundle_id,
                            current_node,
                            next_node,
                            "Failed",
                            {"delay": link_delay, "distance": distance}
                        )
                        continue
                    
                    # Successful transmission
                    total_delay += link_delay
                    
                    self.logger.log_bundle_event(
                        "Transmission",
                        bundle_id,
                        current_node,
                        next_node,
                        "Success",
                        {
                            "delay": link_delay,
                            "total_delay": total_delay,
                            "distance": distance,
                            "retransmissions": retransmissions
                        }
                    )
                    
                    # Update visualization
                    self.visualizer.update_simulation_state(
                        current_path=current_path,
                        current_node=current_node,
                        disrupted_links=disrupted_links,
                        bundle_info={
                            "id": bundle_id,
                            "total_delay": total_delay,
                            "retransmissions": retransmissions,
                            "status": "In Transit",
                            "stored_bundles": {k: len(v) for k, v in stored_bundles.items()},
                            "current_path_index": f"Path {paths_with_delays.index((current_path, estimated_delay)) + 1}/{len(paths_with_delays)}"
                        }
                    )
                    
                    time.sleep(1)
                    i += 1
                    
                    if i == len(current_path) - 1:  # Reached destination
                        successful_delivery = True
                        break
        
        # Final statistics
        final_stats = {
            "bundle_id": bundle_id,
            "total_delay": total_delay,
            "total_retransmissions": retransmissions,
            "final_path": current_path,
            "disruptions": len(disrupted_links),
            "paths_attempted": paths_with_delays.index((current_path, estimated_delay)) + 1,
            "total_available_paths": len(paths_with_delays),
            "max_stored_bundles": max(len(bundles) for bundles in stored_bundles.values())
        }
        
        self.logger.log_network_event("SimulationComplete", final_stats)
        return final_stats