from typing import Dict, List, Tuple, Set
import networkx as nx
from collections import defaultdict

class DTNRoutingAlgorithm:
    def __init__(self, network_graph: nx.Graph):
        self.network_graph = network_graph
        self.disrupted_links = set()
        self.node_buffers = defaultdict(list)
        
    def find_best_path(self, source: str, destination: str, 
                      current_disruptions: Set[tuple]) -> Tuple[List[str], float]:
        """Find best path considering current network conditions."""
        # Create a copy of network graph for path calculation
        working_graph = self.network_graph.copy()
        
        # Remove disrupted links from consideration
        for src, dst in current_disruptions:
            if working_graph.has_edge(src, dst):
                working_graph.remove_edge(src, dst)
                
        try:
            # Find path with lowest combined delay and distance
            path = nx.shortest_path(working_graph, source, destination, 
                                  weight=lambda u, v, d: d['delay'] * (1 + float(d['distance'].replace('M km', '000000').replace(' km', ''))))
            total_delay = sum(working_graph[path[i]][path[i+1]]['delay'] 
                            for i in range(len(path)-1))
            return path, total_delay
        except nx.NetworkXNoPath:
            return [], float('inf')
            
    def get_alternative_paths(self, source: str, destination: str, max_paths: int = 3) -> List[Tuple[List[str], float]]:
        """Get multiple alternative paths sorted by estimated reliability."""
        paths = []
        try:
            # Get all simple paths between source and destination
            all_paths = list(nx.all_simple_paths(self.network_graph, source, destination))
            
            for path in all_paths:
                # Calculate total delay for this path
                total_delay = sum(self.network_graph[path[i]][path[i+1]]['delay'] 
                                for i in range(len(path)-1))
                
                # Calculate path reliability based on distance
                reliability = 1.0
                for i in range(len(path)-1):
                    distance = self.network_graph[path[i]][path[i+1]]['distance']
                    if 'M km' in distance:  # Deep space links are less reliable
                        reliability *= 0.7
                    else:
                        reliability *= 0.9
                        
                paths.append((path, total_delay, reliability))
            
            # Sort by combination of delay and reliability
            paths.sort(key=lambda x: x[1] * (1/x[2]))
            
            # Print for debugging
            print(f"Found {len(paths)} possible paths")
            for p, d, r in paths[:max_paths]:
                print(f"Path: {p}")
                print(f"Delay: {d}, Reliability: {r:.2f}")
                
            return [(p[0], p[1]) for p in paths[:max_paths]]
            
        except nx.NetworkXNoPath:
            print(f"No path found between {source} and {destination}")
            return []
        except Exception as e:
            print(f"Error finding paths: {str(e)}")
            return []
