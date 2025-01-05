import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.network_simulator import SimpleNetworkSimulator
from src.analysis.results_analyzer import DTNResultsAnalyzer
from datetime import datetime

def main():
    # Initialize simulator and analyzer
    simulator = SimpleNetworkSimulator()
    analyzer = DTNResultsAnalyzer()
    
    # Setup network
    simulator.setup_mars_earth_network()

    # Try different paths
    paths_to_test = [
        ("mars_rover_1", "earth_station_1"),  # Default path
      #  ("mars_rover_2", "earth_station_2"),  # Alternative path
     #   ("mars_rover_1", "mars_base"),        # Short path
      #  ("mars_orbiter_1", "earth_station_1") # Partial path
    ]
    
    for source, dest in paths_to_test:
        print(f"\nTesting path from {source} to {dest}")
        stats = simulator.simulate_transmission(
            message=f"Hello from {source}!",
            source=source,
            destination=dest
        )
        analyzer.analyze_simulation(stats)

if __name__ == "__main__":
    main()