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
        # Calculate DTN efficiency metrics
        total_data_sent = len(stats['final_path']) * 1  # 1 bundle per hop
        retransmission_overhead = stats['total_retransmissions']
        storage_events = stats['total_storage_events']
        
        # Calculate theoretical TCP/IP behavior
        tcp_restarts = 0
        tcp_total_data = 0
        tcp_total_delay = 0
        
        for i in range(len(stats['final_path']) - 1):
            node1, node2 = stats['final_path'][i], stats['final_path'][i + 1]
            for link in self.topology['links']:
                if (link['source'] == node1 and link['target'] == node2) or \
                   (link['source'] == node2 and link['target'] == node1):
                    delay = link['delay']
                    distance = link['distance']
                    
                    if 'M km' in distance:  # Deep space links
                        # TCP would likely timeout and restart
                        tcp_restarts += stats['disruptions']  # Each disruption causes restart
                        tcp_total_delay += delay * (tcp_restarts + 1)  # Cumulative delays
                        tcp_total_data += (i + 1) * tcp_restarts  # Resend from beginning
                    else:  # Near space links
                        tcp_total_delay += delay
                        tcp_total_data += 1
        
        report = f"""DTN Performance Analysis
======================
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DTN Efficiency Metrics
---------------------
- Total Path Length: {len(stats['final_path'])} hops
- Data Units Transmitted: {total_data_sent} bundles
- Retransmission Overhead: {retransmission_overhead} bundles
- Storage Events: {storage_events}
- Disruptions Handled: {stats['disruptions']}

Resource Utilization
------------------
- Storage Points Used: {len(stats['buffer_states'])} nodes
- Maximum Stored Bundles: {stats['max_stored_bundles']}
- Buffer States: {stats['buffer_states']}
- Recovery Success Rate: {(stats['successful_recoveries'] / stats['recovery_attempts'] * 100 if stats['recovery_attempts'] > 0 else 100):.1f}%

Time Analysis
------------
- Total Transmission Time: {stats['total_delay']} seconds ({stats['total_delay']/60:.1f} minutes)
- Average Hop Delay: {stats['total_delay'] / len(stats['final_path']):.2f} seconds
- Recovery Time: {stats['avg_recovery_time']:.1f} seconds per disruption
- Total Distance: {self._calculate_total_distance(stats['final_path'])}

Disruption Handling
-----------------
- Disrupted Links: {stats['disrupted_links']}
- Recovery Attempts: {stats['recovery_attempts']}
- Successful Recoveries: {stats['successful_recoveries']}
- Average Recovery Time: {stats['avg_recovery_time']:.1f} seconds

DTN vs TCP/IP Comparison
----------------------
1. Data Transmission Efficiency:
   - DTN Total Data Sent: {total_data_sent + retransmission_overhead} bundles
   - TCP/IP Estimated Data: {tcp_total_data} units (with restarts)
   - Data Overhead Saved: {tcp_total_data - (total_data_sent + retransmission_overhead)} units

2. Time Efficiency:
   - DTN Total Time: {stats['total_delay']} seconds
   - TCP/IP Estimated Time: {tcp_total_delay} seconds
   - Time Saved: {tcp_total_delay - stats['total_delay']} seconds

3. Key DTN Advantages:
   - Partial Progress Preserved: {storage_events} times
   - Restart Prevention: {tcp_restarts} full restarts avoided
   - Local Recovery Success: {stats['successful_recoveries']} times

Note: TCP/IP estimates consider:
- Full restart requirements after timeouts
- No store-and-forward capability
- Cumulative impact of disruptions
- Deep space communication challenges
"""
        
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