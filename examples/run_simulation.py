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
    print("\nStarting simulation with test message...")
    
    # Run simulation from Mars Rover 1 to Earth Station 1
    stats = simulator.simulate_transmission(
        message=test_message,
        source="mars_rover_1",
        destination="earth_station_1"
    )
    
    # Print final statistics
    print("\nSimulation completed!")
    print("\nFinal Statistics:")
    print(f"Total Delay: {stats['total_delay']} seconds")
    print(f"Total Retransmissions: {stats['total_retransmissions']}")
    print(f"Number of Disruptions: {stats['disruptions']}")
    print(f"Paths Attempted: {stats['paths_attempted']}/{stats['total_available_paths']}")
    print(f"Final Path: {' -> '.join(stats['final_path'])}")

if __name__ == "__main__":
    main()