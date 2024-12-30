from dataclasses import dataclass
from typing import List, Dict
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

@dataclass
class TransmissionMetrics:
    delay_times: List[float]
    success_rate: float
    buffer_usage: Dict[str, List[float]]
    disruption_periods: List[tuple]
    total_data_sent: int
    total_data_received: int

class DTNMetricsAnalyzer:
    def __init__(self):
        self.metrics = {}
        
    def calculate_metrics(self, bundle_size: int = 1024,  # 1KB bundles
                         simulation_duration: int = 3600,  # 1 hour
                         disruption_probability: float = 0.2):
        """Calculate DTN performance metrics."""
        
        # Simulate disruptions
        disruptions = self._generate_disruptions(simulation_duration, disruption_probability)
        
        # Calculate delays including disruptions
        delays = self._calculate_delays(disruptions)
        
        # Calculate success rate
        success_rate = self._calculate_success_rate(delays, disruptions)
        
        # Simulate buffer usage
        buffer_usage = self._simulate_buffer_usage(disruptions)
        
        # Calculate throughput
        total_sent = bundle_size * len(delays)
        total_received = bundle_size * int(len(delays) * success_rate)
        
        return TransmissionMetrics(
            delay_times=delays,
            success_rate=success_rate,
            buffer_usage=buffer_usage,
            disruption_periods=disruptions,
            total_data_sent=total_sent,
            total_data_received=total_received
        )
    
    def _generate_disruptions(self, duration: int, probability: float) -> List[tuple]:
        """Generate random communication disruptions."""
        disruptions = []
        current_time = 0
        
        while current_time < duration:
            if np.random.random() < probability:
                disruption_start = current_time
                disruption_length = np.random.randint(60, 300)  # 1-5 minutes
                disruptions.append((disruption_start, disruption_start + disruption_length))
                current_time += disruption_length
            current_time += 60  # Check every minute
            
        return disruptions
    
    def _calculate_delays(self, disruptions: List[tuple]) -> List[float]:
        """Calculate transmission delays including disruptions."""
        base_delays = [960]  # 16 minutes base delay Mars-Earth
        
        # Add delay variation and disruption effects
        delays = []
        for base_delay in base_delays:
            delay = base_delay + np.random.normal(0, 60)  # Add random variation
            # Add disruption delays
            for start, end in disruptions:
                if np.random.random() < 0.5:  # 50% chance of being affected by each disruption
                    delay += (end - start)
            delays.append(max(0, delay))
            
        return delays
    
    def _calculate_success_rate(self, delays: List[float], 
                              disruptions: List[tuple]) -> float:
        """Calculate packet success rate."""
        total_packets = len(delays)
        failed_packets = sum(1 for d in delays if d > 3600)  # Packets delayed > 1 hour considered failed
        return 1 - (failed_packets / total_packets)
    
    def _simulate_buffer_usage(self, disruptions: List[tuple]) -> Dict[str, List[float]]:
        """Simulate buffer usage at each node during disruptions."""
        nodes = ["mars_rover", "mars_orbiter", "relay_satellite"]
        buffer_usage = {node: [] for node in nodes}
        
        for node in nodes:
            usage = []
            buffer_size = 0
            for start, end in disruptions:
                # Buffer fills during disruption
                buffer_size += np.random.randint(100, 1000)  # 100KB-1MB per minute
                usage.extend([buffer_size] * (end - start))
                # Buffer empties after disruption
                buffer_size = max(0, buffer_size - np.random.randint(500, 1500))
            buffer_usage[node] = usage
            
        return buffer_usage

    def visualize_metrics(self, metrics: TransmissionMetrics):
        """Create visualizations for DTN metrics."""
        fig = plt.figure(figsize=(15, 10))
        
        # 1. Delay Distribution
        plt.subplot(2, 2, 1)
        plt.hist(metrics.delay_times, bins=20)
        plt.title('Transmission Delay Distribution')
        plt.xlabel('Delay (seconds)')
        plt.ylabel('Frequency')
        
        # 2. Buffer Usage Over Time
        plt.subplot(2, 2, 2)
        for node, usage in metrics.buffer_usage.items():
            if usage:  # Only plot if we have data
                plt.plot(usage, label=node)
        plt.title('Buffer Usage During Disruptions')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Buffer Usage (KB)')
        plt.legend()
        
        # 3. Success Rate
        plt.subplot(2, 2, 3)
        plt.pie([metrics.success_rate, 1-metrics.success_rate], 
                labels=['Successful', 'Failed'],
                autopct='%1.1f%%')
        plt.title('Transmission Success Rate')
        
        # 4. Disruption Timeline
        plt.subplot(2, 2, 4)
        for start, end in metrics.disruption_periods:
            plt.axvspan(start, end, color='red', alpha=0.3)
        plt.title('Communication Disruption Periods')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Connection Status')
        
        plt.tight_layout()
        plt.show()
