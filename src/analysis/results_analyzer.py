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
        sim_dir.mkdir(parents=True, exist_ok=True)
        
        # Save raw statistics
        with open(sim_dir / "stats.json", "w") as f:
            json.dump(stats, f, indent=4)
            
        # Generate visualizations
        self._create_performance_summary(stats, sim_dir)
        self._create_detailed_analysis(stats, sim_dir)
        self._create_dtn_tcp_comparison(stats, sim_dir)
        
        print(f"Analysis results saved to: {sim_dir}")
        
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
        """Create detailed performance analysis with focus on DTN advantages."""
        # Calculate DTN efficiency metrics with safety checks
        total_data_sent = len(stats['final_path']) if stats['final_path'] else 0
        retransmission_overhead = stats['total_retransmissions']
        storage_events = stats['total_storage_events']
        
        # Calculate efficiency rate
        total_transmissions = len(stats['final_path']) - 1  # Number of hops actually used
        total_attempts = stats['total_retransmissions'] + total_transmissions
        efficiency_rate = (total_transmissions / total_attempts * 100) if total_attempts > 0 else 0
        
        # Calculate recovery rate
        total_disruptions = len(stats['disrupted_links'])
        successful_recoveries = sum(1 for link in stats['disrupted_links'] 
                                  if link not in [(path['path'][i], path['path'][i+1]) 
                                                for path in stats['path_history'] 
                                                if path['status'] == 'Failed' 
                                                for i in range(len(path['path'])-1)])
        recovery_rate = (successful_recoveries / total_disruptions * 100) if total_disruptions > 0 else 0
        
        # Build path history string
        path_history = "\nPath History:\n"
        for attempt in stats['path_history']:
            path_history += f"\nAttempt {attempt['attempt']}:\n"
            path_history += f"Planned Path: {' -> '.join(attempt['path'])}\n"
            path_history += f"Status: {attempt['status']}\n"
        
        report = f"""DTN Performance Analysis
======================
Timestamp: {stats['simulation_timestamp']}

Route Information
----------------
Source: {stats['source']}
Destination: {stats['destination']}
Final Status: {stats['status']}

Complete Path Taken
----------------
{' -> '.join(stats['final_path']) if stats['final_path'] else 'No path completed'}

{path_history}

Disruption Analysis
-----------------
Total Disruptions: {total_disruptions}
Disrupted Links: {', '.join([f"{src}->{dst}" for src, dst in stats['disrupted_links']])}
Recovery Attempts: {stats['recovery_attempts']}
Successful Recoveries: {successful_recoveries}
Recovery Success Rate: {recovery_rate:.1f}%

Storage Analysis
--------------
Storage Events: {storage_events}
Max Stored Bundles: {stats['max_stored_bundles']}
Buffer States at End:
{chr(10).join([f"  {node}: {count} bundles" for node, count in stats['buffer_states'].items() if count > 0])}

Time Analysis
-----------
Total Transmission Time: {stats['total_delay']} seconds ({stats['total_delay']/60:.1f} minutes)
Average Hop Delay: {(stats['total_delay'] / len(stats['final_path'])) if stats['final_path'] else 0:.2f} seconds

Performance Metrics
----------------
Data Units Transmitted: {total_transmissions} bundles
Retransmission Overhead: {stats['total_retransmissions']} bundles
Efficiency Rate: {efficiency_rate:.1f}%

DTN Advantages Demonstrated
------------------------
1. Store and Forward: {storage_events} times utilized
2. Path Flexibility: {stats['paths_attempted']} paths tried
3. Disruption Handling: {successful_recoveries} successful recoveries
4. Data Preservation: {stats['stored_bundles']} bundles temporarily stored

Message Details
-------------
Bundle ID: {stats['bundle_id']}
Message: {stats['message']}

Notes
-----
- Simulation used store-and-forward {storage_events} times to handle disruptions
- {successful_recoveries} of {total_disruptions} disruptions were recovered from
- Path changes occurred {stats['paths_attempted'] - 1} times during transmission
"""

        # Write the report to a file
        with open(sim_dir / "detailed_analysis.txt", "w") as f:
            f.write(report)
            
    def _create_dtn_tcp_comparison(self, stats, sim_dir):
        """Create DTN vs TCP/IP comparison visualization focusing on efficiency."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Data Transmission Efficiency
        ax1 = axes[0, 0]
        total_dtn_data = len(stats['final_path']) + stats['total_retransmissions']
        tcp_total_data = len(stats['final_path']) * (stats['disruptions'] + 1)
        data_comparison = {
            'DTN': total_dtn_data,
            'TCP/IP (est.)': tcp_total_data
        }
        sns.barplot(x=list(data_comparison.keys()), y=list(data_comparison.values()), ax=ax1)
        ax1.set_title('Data Units Transmitted')
        ax1.set_ylabel('Data Units')
        
        # 2. Time Efficiency
        ax2 = axes[0, 1]
        time_comparison = {
            'DTN Total Time': stats['total_delay'],
            'TCP/IP Est. Time': stats['total_delay'] * (stats['disruptions'] + 1)
        }
        sns.barplot(x=list(time_comparison.keys()), y=list(time_comparison.values()), ax=ax2)
        ax2.set_title('Total Transmission Time')
        ax2.set_ylabel('Seconds')
        
        # 3. Disruption Handling
        ax3 = axes[1, 0]
        handling_data = {
            'Storage Events': stats['total_storage_events'],
            'Successful Recoveries': stats['successful_recoveries'],
            'TCP/IP Restarts': stats['disruptions']  # Each disruption would cause TCP restart
        }
        sns.barplot(x=list(handling_data.keys()), y=list(handling_data.values()), ax=ax3)
        ax3.set_title('Disruption Handling')
        ax3.set_ylabel('Count')
        
        # 4. Resource Usage
        ax4 = axes[1, 1]
        resource_data = {
            'Storage Points Used': len(stats['buffer_states']),
            'Max Stored Bundles': stats['max_stored_bundles'],
            'Retransmissions': stats['total_retransmissions']
        }
        sns.barplot(x=list(resource_data.keys()), y=list(resource_data.values()), ax=ax4)
        ax4.set_title('Resource Utilization')
        ax4.set_ylabel('Count')
        
        plt.tight_layout()
        plt.savefig(sim_dir / "protocol_comparison.png")
        plt.close()