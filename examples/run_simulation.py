import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.network_simulator import SimpleNetworkSimulator
from src.analysis.results_analyzer import DTNResultsAnalyzer

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
    print("\nStarting simulation with test message...")
    
    # Run simulation from Mars Rover 1 to Earth Station 1
    stats = simulator.simulate_transmission(
        message=test_message,
        source="mars_rover_1",
        destination="earth_station_1"
    )
    
    # Analyze results
    analyzer = DTNResultsAnalyzer()
    analyzer.analyze_simulation(stats)
    
    print("\nSimulation completed!")
    print("Results have been saved to data/results/")

if __name__ == "__main__":
    main()