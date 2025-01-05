from datetime import datetime
import time
import json
from src.dtn_core import DTNNode, Bundle
from src.visualization import DTNVisualizer
from src.base import NetworkSimulatorBase
import numpy as np
from src.utils.config import ConfigLoader
import random
from src.utils.logger import DTNLogger
import networkx as nx
from src.routing_algorithms import DTNRoutingAlgorithm

class SimpleNetworkSimulator(NetworkSimulatorBase):
    def __init__(self):
        self.nodes = {}
        self.config = ConfigLoader()
        self.logger = DTNLogger()
        self.visualizer = DTNVisualizer(self.config)
        self.topology = self.load_topology()
        self.buffer = {}
        self.network_graph = self._build_network_graph()
        self.router = DTNRoutingAlgorithm(self._build_network_graph())
        
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
        
        # Initialize simulation state
        disrupted_links = set()
        total_delay = 0
        retransmissions = 0
        successful_delivery = False
        stored_bundles_count = 0
        current_node = source
        
        # Get initial path options from router
        path_options = self.router.get_alternative_paths(current_node, destination)
        current_path = path_options[0][0] if path_options else []
        initial_paths_count = len(path_options)
        paths_attempted = 0
        max_retries_per_link = 3
        
        # Add path history tracking
        path_history = []
        completed_path = []
        
        while not successful_delivery and path_options:
            paths_attempted += 1
            
            # Record path attempt
            path_history.append({
                "attempt": paths_attempted,
                "path": current_path,
                "status": "Started"
            })
            
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
                    "available_paths": len(path_options)
                }
            )
            
            # Get next node in current path
            current_idx = current_path.index(current_node)
            if current_idx == len(current_path) - 1:
                successful_delivery = True
                completed_path.append(current_node)
                path_history[-1]["status"] = "Completed"
                break
            
            next_node = current_path[current_idx + 1]
            
            # Check for disruption or error
            is_error = random.random() < self.config.get_simulation_params()["network"]["error_rate"]
            is_disrupted = random.random() < self.config.get_simulation_params()["network"]["disruption_rate"]
            
            if is_error or is_disrupted:
                print(f"Link disrupted: {current_node} -> {next_node}")
                self.logger.log_network_event("LinkDisrupted", f"Link disrupted: {current_node} -> {next_node}")
                disrupted_links.add((current_node, next_node))
                path_history[-1]["status"] = f"Failed at {current_node}->{next_node}"
                
                # Store bundle at current node
                if current_node not in self.buffer:
                    self.buffer[current_node] = []
                self.buffer[current_node].append(bundle)
                stored_bundles_count += 1
                
                # Recalculate path from current node
                path_options = self.router.get_alternative_paths(current_node, destination)
                
                # Filter out paths that start with disrupted links
                path_options = [
                    (path, delay) for path, delay in path_options
                    if not (path[0], path[1]) in disrupted_links
                ]
                
                if path_options:
                    print(f"Found new path from {current_node}: {path_options[0][0]}")
                    self.logger.log_network_event("NewPath", f"Found new path from {current_node}: {path_options[0][0]}")
                    current_path = path_options[0][0]
                    path_history.append({
                        "attempt": paths_attempted + 1,
                        "path": current_path,
                        "status": "Rerouted"
                    })
                    continue
                else:
                    print("No alternative paths available, attempting to retry disrupted links...")
                    self.logger.log_network_event("RetryingLinks", "No alternative paths available, attempting to retry disrupted links...")
                    # Try to recover disrupted links
                    retry_count = 0
                    while retry_count < max_retries_per_link:
                        print(f"Retry attempt {retry_count + 1}/{max_retries_per_link}")
                        self.logger.log_network_event("RetryAttempt", f"Retry attempt {retry_count + 1}/{max_retries_per_link}")
                        time.sleep(1)  # Wait before retry
                        
                        # Check if link recovers
                        if random.random() > (self.config.get_simulation_params()["network"]["error_rate"] + 
                                            self.config.get_simulation_params()["network"]["disruption_rate"]) / 2:
                            print(f"Link recovered: {current_node} -> {next_node}")
                            self.logger.log_network_event("LinkRecovered", f"Link recovered: {current_node} -> {next_node}")
                            disrupted_links.remove((current_node, next_node))
                            retransmissions += 1
                            
                            # Recalculate path options after recovery
                            path_options = self.router.get_alternative_paths(current_node, destination)
                            if path_options:
                                current_path = path_options[0][0]
                                print(f"Found new path after recovery: {current_path}")
                                self.logger.log_network_event("NewPathAfterRecovery", f"Found new path after recovery: {current_path}")
                                path_history.append({
                                    "attempt": paths_attempted + 1,
                                    "path": current_path,
                                    "status": "Recovered and Rerouted"
                                })
                            break
                        
                        retry_count += 1
                        retransmissions += 1
                    
                    if retry_count == max_retries_per_link:
                        print(f"Failed to recover after {max_retries_per_link} attempts")
                        self.logger.log_network_event("RecoveryFailed", f"Failed to recover after {max_retries_per_link} attempts")
                        path_history[-1]["status"] = "Failed - Max retries reached"
                        break
                    continue
            
            # Successful transmission
            total_delay += self.network_graph[current_node][next_node]["delay"]
            completed_path.append(current_node)
            current_node = next_node
            
            # Remove from buffer if it was stored
            if current_node in self.buffer and bundle in self.buffer[current_node]:
                self.buffer[current_node].remove(bundle)
            
            time.sleep(0.5)  # Visualization delay
        
        final_status = "Delivered" if successful_delivery else "Failed"
        print(f"Simulation completed: {final_status}")
        self.logger.log_network_event("SimulationComplete", f"Simulation completed: {final_status}")
        
        # Calculate max stored bundles
        max_stored_bundles = max([len(bundles) for bundles in self.buffer.values()]) if self.buffer else 0
        
        return {
            "total_delay": total_delay,
            "total_retransmissions": retransmissions,
            "disruptions": len(disrupted_links),
            "stored_bundles": stored_bundles_count,
            "max_stored_bundles": max_stored_bundles,
            "total_storage_events": stored_bundles_count,
            "status": final_status,
            "final_path": completed_path,
            "path_history": path_history,
            "total_available_paths": initial_paths_count,
            "paths_attempted": paths_attempted,
            "bundle_id": bundle_id,
            "source": source,
            "destination": destination,
            "message": message,
            "simulation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "disrupted_links": list(disrupted_links),
            "buffer_states": {k: len(v) for k, v in self.buffer.items()},
            "successful_delivery": successful_delivery,
            "recovery_attempts": retransmissions,
            "successful_recoveries": len([link for link in disrupted_links if link not in self.buffer])
        }