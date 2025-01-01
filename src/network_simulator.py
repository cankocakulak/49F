import json
from datetime import datetime, timedelta
import time
from src.dtn_core import DTNNode, Bundle
from src.visualization import DTNVisualizer
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
        recovery_times = []
        disruptions_handled = 0
        stored_bundles_count = 0
        
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
                    
                    # Get configuration parameters
                    error_rate = self.config.get_simulation_params()["network"]["error_rate"]
                    disruption_rate = self.config.get_simulation_params()["network"]["disruption_rate"]
                    
                    # Clear log of disruption check
                    self.logger.log_network_event("DisruptionCheck", {
                        "current_node": current_node,
                        "next_node": next_node,
                        "error_rate": error_rate,
                        "disruption_rate": disruption_rate
                    })
                    
                    # Separate checks for errors and disruptions
                    is_error = random.random() < error_rate
                    is_disrupted = random.random() < disruption_rate
                    
                    if is_error or is_disrupted:
                        disrupted_links.add((current_node, next_node))
                        disruptions_handled += 1
                        
                        # Store bundle at current node
                        if bundle not in self.buffer.get(current_node, []):
                            if current_node not in self.buffer:
                                self.buffer[current_node] = []
                            self.buffer[current_node].append(bundle)
                            stored_bundles_count += 1
                            
                            self.logger.log_bundle_event(
                                "BundleStored",
                                bundle_id,
                                current_node,
                                details={
                                    "reason": "error" if is_error else "disruption",
                                    "buffer_size": len(self.buffer[current_node])
                                }
                            )
                        
                        # Try to recover
                        recovery_start = time.time()
                        retry_count = 0
                        max_retries = 3
                        
                        while retry_count < max_retries:
                            self.logger.log_bundle_event(
                                "RecoveryAttempt",
                                bundle_id,
                                current_node,
                                next_node,
                                f"Attempt {retry_count + 1}/{max_retries}"
                            )
                            
                            time.sleep(1)  # Simulate recovery attempt
                            
                            # Check if link recovers
                            if random.random() > (error_rate + disruption_rate) / 2:
                                recovery_time = time.time() - recovery_start
                                recovery_times.append(recovery_time)
                                
                                # Remove from buffer and continue
                                if current_node in self.buffer:
                                    self.buffer[current_node].remove(bundle)
                                disrupted_links.remove((current_node, next_node))
                                
                                self.logger.log_bundle_event(
                                    "RecoverySuccess",
                                    bundle_id,
                                    current_node,
                                    next_node,
                                    f"Recovered after {retry_count + 1} attempts"
                                )
                                break
                            
                            retry_count += 1
                            retransmissions += 1
                        
                        if retry_count == max_retries:
                            self.logger.log_bundle_event(
                                "RecoveryFailed",
                                bundle_id,
                                current_node,
                                next_node,
                                "Max retries reached"
                            )
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
            "disruptions": disruptions_handled,
            "disrupted_links": list(disrupted_links),
            "avg_recovery_time": sum(recovery_times) / len(recovery_times) if recovery_times else 0,
            "stored_bundles": stored_bundles_count,
            "max_stored_bundles": max([len(bundles) for bundles in self.buffer.values()]) if self.buffer else 0,
            "paths_attempted": paths_with_delays.index((current_path, estimated_delay)) + 1,
            "total_available_paths": len(paths_with_delays),
            "buffer_states": {node: len(bundles) for node, bundles in self.buffer.items()},
            "total_storage_events": stored_bundles_count,
            "recovery_attempts": retransmissions,
            "successful_recoveries": len(recovery_times)
        }
        
        self.logger.log_network_event("SimulationComplete", final_stats)
        return final_stats