import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.network_simulator import SimpleNetworkSimulator

def main():
    # Create simulator
    simulator = SimpleNetworkSimulator()
    
    # Setup network
    if not simulator.setup_mars_earth_network():
        print("Failed to setup network. Exiting...")
        return
    
    # Show initial network topology
    simulator.visualizer.visualize_network(title="Mars-Earth DTN Network")
    
    # Run simulation
    test_message = "Hello from Mars! This is a test transmission."
    simulator.simulate_transmission(test_message)

if __name__ == "__main__":
    main()