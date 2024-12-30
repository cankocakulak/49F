import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List
from datetime import datetime

class DTNVisualizer:
    def __init__(self):
        self.G = nx.Graph()
        self.pos = None
        self.current_step = 0
        self.simulation_steps = []
        self.fig = None
        self.bundle_info = None
        
    def create_network_graph(self, nodes: List[str], connections: List[tuple]) -> None:
        """Create network topology."""
        self.G.add_nodes_from(nodes)
        self.G.add_edges_from(connections)
        self.pos = nx.spring_layout(self.G, k=1, iterations=50)
    
    def visualize_network(self, title: str = "DTN Network Topology"):
        """Show initial network topology."""
        self.fig = plt.figure(figsize=(12, 8))
        
        nx.draw_networkx_nodes(self.G, self.pos, 
                             node_color='lightblue',
                             node_size=2000)
        
        nx.draw_networkx_edges(self.G, self.pos, 
                             edge_color='gray',
                             width=1)
        
        nx.draw_networkx_labels(self.G, self.pos)
        
        plt.title(title)
        plt.axis('off')
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(3)
        plt.close()

    def on_keyboard(self, event):
        """Handle keyboard events."""
        if event.key == 'right' and self.current_step < len(self.simulation_steps) - 1:
            self.current_step += 1
            self.update_visualization()
        elif event.key == 'left' and self.current_step > 0:
            self.current_step -= 1
            self.update_visualization()
        elif event.key == 'q':
            plt.close()

    def update_visualization(self):
        """Update the visualization based on current step."""
        plt.clf()
        current_node = self.simulation_steps[self.current_step]
        path = self.simulation_steps
        
        # Draw all nodes in gray
        nx.draw_networkx_nodes(self.G, self.pos,
                             node_color='lightgray',
                             node_size=2000)
        
        # Draw completed path in green
        completed_path = path[:self.current_step]
        if len(completed_path) > 1:
            completed_edges = list(zip(completed_path[:-1], completed_path[1:]))
            nx.draw_networkx_edges(self.G, self.pos,
                                 edgelist=completed_edges,
                                 edge_color='green',
                                 width=2)
        
        # Draw remaining path in gray dashed
        remaining_path = path[self.current_step:]
        if len(remaining_path) > 1:
            remaining_edges = list(zip(remaining_path[:-1], remaining_path[1:]))
            nx.draw_networkx_edges(self.G, self.pos,
                                 edgelist=remaining_edges,
                                 edge_color='gray',
                                 style='dashed',
                                 width=1)
        
        # Draw active node in red
        nx.draw_networkx_nodes(self.G, self.pos,
                             nodelist=[current_node],
                             node_color='red',
                             node_size=2000)
        
        nx.draw_networkx_labels(self.G, self.pos)
        
        # Show bundle info
        info_text = f"Bundle Transfer Status:\n"
        info_text += f"Source: {self.bundle_info['source']}\n"
        info_text += f"Destination: {self.bundle_info['destination']}\n"
        info_text += f"Current Node: {current_node}\n"
        info_text += f"Step: {self.current_step + 1}/{len(path)}\n\n"
        info_text += "Use ← → keys to navigate\nPress 'q' to quit"
        
        plt.figtext(0.02, 0.02, info_text, fontsize=10, 
                   bbox=dict(facecolor='white', alpha=0.8))
        
        plt.title(f"DTN Bundle Transmission - Step {self.current_step + 1}")
        plt.axis('off')
        plt.tight_layout()
        plt.draw()

    def simulate_transmission(self, path: List[str], bundle_info: Dict):
        """Simulate the transmission with interactive controls."""
        self.simulation_steps = path
        self.bundle_info = bundle_info
        self.current_step = 0
        
        self.fig = plt.figure(figsize=(12, 8))
        self.fig.canvas.mpl_connect('key_press_event', self.on_keyboard)
        
        self.update_visualization()
        plt.show()