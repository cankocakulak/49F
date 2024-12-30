import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.network_simulator import SimpleNetworkSimulator
from src.visualization import DTNVisualizer

def main():
    # Simülatörü oluştur
    simulator = SimpleNetworkSimulator()
    
    # Ağı kur
    simulator.setup_mars_earth_network()
    
    # Temel topolojiyi görselleştir
    simulator.visualizer.visualize_network(title="Mars-Earth DTN Network")
    
    # Test mesajı gönder
    message = "Hello from Mars! This is a test transmission."
    print(f"\nStarting transmission simulation...")
    print(f"Message: {message}\n")
    
    simulator.simulate_transmission(message)
    
    print("\nSimulation completed!")

if __name__ == "__main__":
    main()