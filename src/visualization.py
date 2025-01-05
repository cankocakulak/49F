import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Set
import time
from src.base import VisualizerBase

class DTNVisualizer(VisualizerBase):
    def __init__(self, config):
        self.G = nx.Graph()
        self.pos = None
        self.config = config
        self.vis_params = config.get_visualization_params()
        self.fig = plt.figure(figsize=self.vis_params["figure_size"])
        
    def create_network_graph(self, nodes: List[str], connections: List[tuple]) -> None:
        """Create network topology."""
        self.G.add_nodes_from(nodes)
        self.G.add_edges_from(connections)
        self.pos = nx.spring_layout(self.G, k=1, iterations=50)
        
    def update_simulation_state(self, current_path: List[str], 
                              current_node: str,
                              disrupted_links: Set[tuple],
                              bundle_info: Dict):
        """Update visualization with current simulation state."""
        plt.clf()
        
        # Draw all nodes in default color
        nx.draw_networkx_nodes(self.G, self.pos,
                             node_color=self.vis_params["node_colors"]["default"],
                             node_size=self.vis_params["node_size"])
        
        # Draw completed path nodes in green
        current_idx = current_path.index(current_node)
        completed_nodes = current_path[:current_idx]
        if completed_nodes:
            nx.draw_networkx_nodes(self.G, self.pos,
                                 nodelist=completed_nodes,
                                 node_color=self.vis_params["node_colors"]["completed"],
                                 node_size=self.vis_params["node_size"])
        
        # Draw current node in red
        nx.draw_networkx_nodes(self.G, self.pos,
                             nodelist=[current_node],
                             node_color=self.vis_params["node_colors"]["active"],
                             node_size=self.vis_params["node_size"])
        
        # Draw edges with different colors based on status
        for (source, target) in self.G.edges():
            if (source, target) in disrupted_links or (target, source) in disrupted_links:
                # Disrupted links in red dashed
                nx.draw_networkx_edges(self.G, self.pos,
                                     edgelist=[(source, target)],
                                     edge_color='red',
                                     style='dashed')
            elif source in completed_nodes and target in completed_nodes:
                # Completed path in green
                nx.draw_networkx_edges(self.G, self.pos,
                                     edgelist=[(source, target)],
                                     edge_color=self.vis_params["edge_colors"]["active"])
            else:
                # Other links in default color
                nx.draw_networkx_edges(self.G, self.pos,
                                     edgelist=[(source, target)],
                                     edge_color=self.vis_params["edge_colors"]["default"])
        
        # Draw labels
        nx.draw_networkx_labels(self.G, self.pos)
        
        # Show bundle information
        info_text = f"Bundle Status:\n"
        info_text += f"ID: {bundle_info['id']}\n"
        info_text += f"Current Node: {current_node}\n"
        info_text += f"Total Delay: {bundle_info['total_delay']}s\n"
        info_text += f"Retransmissions: {bundle_info['retransmissions']}\n"
        info_text += f"Status: {bundle_info['status']}"
        
        plt.figtext(0.02, 0.02, info_text, fontsize=10,
                   bbox=dict(facecolor='white', alpha=0.8))
        
        # Show network statistics
        stats_text = f"Network Statistics:\n"
        stats_text += f"Disrupted Links: {len(disrupted_links)}\n"
        stats_text += f"Progress: {current_idx + 1}/{len(current_path)} hops"
        
        plt.figtext(0.02, 0.98, stats_text, fontsize=10,
                   bbox=dict(facecolor='white', alpha=0.8),
                   verticalalignment='top')
        
        # Draw alternative paths in different colors
        if 'alternative_paths' in bundle_info:
            colors = ['lightblue', 'lightgreen', 'lightyellow']
            for i, path in enumerate(bundle_info['alternative_paths'][:3]):
                path_edges = list(zip(path[:-1], path[1:]))
                nx.draw_networkx_edges(self.G, self.pos,
                                     edgelist=path_edges,
                                     edge_color=colors[i],
                                     style='dotted',
                                     alpha=0.3)
        
        # Add routing information to status text
        routing_text = f"\nRouting Info:\n"
        routing_text += f"Available Paths: {bundle_info.get('available_paths', 0)}\n"
        routing_text += f"Current Path: {current_path}\n"
        
        plt.figtext(0.02, 0.15, routing_text, fontsize=10,
                    bbox=dict(facecolor='white', alpha=0.8))
        
        plt.title("DTN Bundle Transmission Simulation")
        plt.axis('off')
        plt.tight_layout()
        
        # Update display
        plt.draw()
        plt.pause(0.5)  # Short pause to allow visualization to update
        
    def visualize_network(self, title: str = "DTN Network Topology"):
        """Show initial network topology."""
        plt.clf()
        
        nx.draw_networkx_nodes(self.G, self.pos,
                             node_color=self.vis_params["node_colors"]["default"],
                             node_size=self.vis_params["node_size"])
        
        nx.draw_networkx_edges(self.G, self.pos,
                             edge_color=self.vis_params["edge_colors"]["default"])
        
        nx.draw_networkx_labels(self.G, self.pos)
        
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(3)  # Show initial topology for 3 seconds

