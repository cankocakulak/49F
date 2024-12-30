import pytest
from src.visualization import DTNVisualizer
from src.network_simulator import SimpleNetworkSimulator

def test_visualizer_initialization():
    visualizer = DTNVisualizer()
    assert visualizer is not None

def test_network_graph_creation():
    simulator = SimpleNetworkSimulator()
    simulator.setup_mars_earth_network()
    
    # Temel topoloji kontrolü
    nodes = simulator.nodes.keys()
    assert "mars_rover" in nodes
    assert "earth_station" in nodes
    
    # Görselleştirici kontrolü
    assert simulator.visualizer is not None
    assert simulator.visualizer.G is not None