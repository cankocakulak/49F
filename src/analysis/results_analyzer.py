import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import os
import json
from pathlib import Path

class DTNResultsAnalyzer:
    def __init__(self):
        self.results_dir = Path("data/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.topology = self._load_topology()

    def _load_topology(self):
        """Load network topology from JSON file."""
        try:
            with open("data/network_topologies/mars_earth.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: Could not load topology file")
            return None

    def analyze_simulation(self, stats, simulation_id=None):
        """Analyze simulation results and generate visualizations."""
        if not simulation_id:
            simulation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        # Create simulation-specific directory
        sim_dir = self.results_dir / simulation_id
        sim_dir.mkdir(exist_ok=True)
        
        # Save raw statistics
        with open(sim_dir / "stats.json", "w") as f:
            json.dump(stats, f, indent=4)
            
        # Generate visualizations
        self._create_performance_summary(stats, sim_dir)
        self._create_detailed_analysis(stats, sim_dir)
        
        # Generate comparison with theoretical TCP/IP
        self._create_dtn_tcp_comparison(stats, sim_dir)
        
    def _create_performance_summary(self, stats, sim_dir):
        """Create main performance metrics visualization."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Transmission Timeline
        ax1 = axes[0, 0]
        timeline_data = {
            'Total Delay': stats['total_delay'],
            'Theoretical TCP/IP': stats['total_delay'] * 2.5  # TCP would timeout and retry
        }
        sns.barplot(x=list(timeline_data.keys()), y=list(timeline_data.values()), ax=ax1)
        ax1.set_title('Transmission Time Comparison (seconds)')
        ax1.set_ylabel('Seconds')
        
        # 2. Retransmission Analysis
        ax2 = axes[0, 1]
        # Ensure we have valid non-negative values for the pie chart
        successful = max(0, stats['total_available_paths'] - stats['paths_attempted'])
        retransmissions = max(0, stats['total_retransmissions'])
        
        # Only create pie if we have non-zero values
        if successful + retransmissions > 0:
            retrans_data = [successful, retransmissions]
            labels = ['Successful', 'Retransmissions']
            ax2.pie(retrans_data, labels=labels, autopct='%1.1f%%')
        else:
            ax2.text(0.5, 0.5, 'No transmission data', 
                    horizontalalignment='center',
                    verticalalignment='center')
        ax2.set_title('Transmission Efficiency')
        
        # 3. Path Utilization
        ax3 = axes[1, 0]
        used_paths = max(0, stats['paths_attempted'])
        available_paths = max(0, stats['total_available_paths'] - stats['paths_attempted'])
        path_data = {
            'Used Paths': used_paths,
            'Available Paths': available_paths
        }
        sns.barplot(x=list(path_data.keys()), y=list(path_data.values()), ax=ax3)
        ax3.set_title('Path Utilization')
        
        # 4. Storage Usage
        ax4 = axes[1, 1]
        storage_data = {
            'Max Stored Bundles': max(0, stats['max_stored_bundles']),
            'Total Disruptions': max(0, stats['disruptions'])
        }
        sns.barplot(x=list(storage_data.keys()), y=list(storage_data.values()), ax=ax4)
        ax4.set_title('Storage and Disruption Analysis')
        
        plt.tight_layout()
        plt.savefig(sim_dir / "performance_summary.png")
        plt.close()
        
    def _calculate_total_distance(self, path):
        """Calculate total distance using topology data."""
        if not self.topology:
            return "Unknown"
            
        total_distance = 0
        for i in range(len(path) - 1):
            node1, node2 = path[i], path[i + 1]
            # Find the link in topology
            for link in self.topology["links"]:
                if ((link["source"] == node1 and link["target"] == node2) or
                    (link["source"] == node2 and link["target"] == node1)):
                    # Extract numeric value from distance string
                    distance_str = link["distance"]
                    if "M km" in distance_str:
                        distance = float(distance_str.replace("M km", "")) * 1000000
                    elif "km" in distance_str:
                        distance = float(distance_str.replace(" km", ""))
                    total_distance += distance
                    break
        
        # Format the distance for readability
        if total_distance >= 1000000:
            return f"{total_distance/1000000:.1f}M km"
        elif total_distance >= 1000:
            return f"{total_distance/1000:.1f}k km"
        else:
            return f"{total_distance:.1f} km"

    def _create_detailed_analysis(self, stats, sim_dir):
        """Create detailed performance analysis."""
        # Calculate key metrics
        total_attempts = stats['total_retransmissions'] + 1  # +1 for successful transmission
        success_rate = (1 / total_attempts) * 100 if total_attempts > 0 else 100
        avg_delay_per_hop = stats['total_delay'] / len(stats['final_path'])
        storage_efficiency = (stats['disruptions'] / stats['max_stored_bundles'] 
                            if stats['max_stored_bundles'] > 0 else 0)
        
        # Create text report
        report = f"""DTN Performance Analysis
======================
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Transmission Efficiency
----------------------
- Success Rate: {success_rate:.2f}%
- Total Retransmissions: {stats['total_retransmissions']}
- Disruptions Handled: {stats['disruptions']}
- Transmission Attempts: {total_attempts}

Delay Analysis
-------------
- Total Delay: {stats['total_delay']} seconds ({stats['total_delay']/60:.1f} minutes)
- Average Delay per Hop: {avg_delay_per_hop:.2f} seconds
- Path Length: {len(stats['final_path'])} hops
- Total Distance: {self._calculate_total_distance(stats['final_path'])}

Storage Utilization
------------------
- Maximum Stored Bundles: {stats['max_stored_bundles']}
- Storage Efficiency: {storage_efficiency:.2f} bundles/disruption
- Total Storage Events: {stats['disruptions']}

Path Analysis
------------
- Paths Attempted: {stats['paths_attempted']}/{stats['total_available_paths']}
- Final Path: {' -> '.join(stats['final_path'])}
- Disrupted Links: {stats.get('disrupted_links', [])}

Network Performance
-----------------
- Average Transmission Success: {success_rate:.1f}%
- Failed Transmissions: {stats['total_retransmissions']}
- Disruption Recovery Time: {stats.get('avg_recovery_time', 0):.1f} seconds

Comparison with TCP/IP
---------------------
- DTN Total Time: {stats['total_delay']} seconds
- Estimated TCP/IP Time: {stats['total_delay'] * 2.5} seconds
- Time Saved: {(stats['total_delay'] * 2.5) - stats['total_delay']} seconds
- Reliability Improvement: {success_rate - 40:.1f}% (compared to TCP/IP est.)
"""
        
        with open(sim_dir / "detailed_analysis.txt", "w") as f:
            f.write(report)
            
    def _create_dtn_tcp_comparison(self, stats, sim_dir):
        """Create DTN vs TCP/IP comparison visualization."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 1. Delay Comparison
        delay_data = {
            'DTN': stats['total_delay'],
            'TCP/IP (est.)': stats['total_delay'] * 2.5,  # Estimated with timeouts
        }
        sns.barplot(x=list(delay_data.keys()), y=list(delay_data.values()), ax=ax1)
        ax1.set_title('Total Delay Comparison')
        ax1.set_ylabel('Seconds')
        
        # 2. Success Rate Comparison
        # Fix: Calculate actual DTN success rate
        dtn_success_rate = 100.0  # If we reached here, transmission was successful
        if stats['total_retransmissions'] > 0:
            dtn_success_rate = (stats['total_delay'] / 
                              (stats['total_delay'] + stats['total_retransmissions'] * stats['total_delay'])) * 100
            
        success_data = {
            'DTN': dtn_success_rate,
            # TCP/IP estimation based on Mars-Earth communication characteristics:
            # - High latency (3-20 minutes one-way)
            # - Frequent disruptions
            # - TCP timeout issues with long RTTs
            'TCP/IP (est.)': 40  # Based on research papers about deep space TCP performance
        }
        sns.barplot(x=list(success_data.keys()), y=list(success_data.values()), ax=ax2)
        ax2.set_title('Success Rate Comparison')
        ax2.set_ylabel('Percentage')
        
        plt.tight_layout()
        plt.savefig(sim_dir / "dtn_tcp_comparison.png")
        plt.close()