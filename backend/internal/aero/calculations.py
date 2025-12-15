"""
Aerodynamics calculations for pressure data
Calculates coefficient of pressure (Cp) and coefficient of total pressure (Cpt)
"""

from typing import Dict, List, Optional
from collections import deque
import statistics
import numpy as np

class AeroCalculations:
    """Calculate aerodynamic coefficients from pressure data"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.reference_port_dynamic = self.config.get("reference_dynamic_port", 7)
        self.reference_port_static = self.config.get("reference_static_port", 8)
        self.num_ports = self.config.get("num_ports", 8)
        
        # Scenario detection thresholds (configurable)
        self.straight_threshold = self.config.get("straight_threshold", 0.1)  # steering angle
        self.turn_threshold = self.config.get("turn_threshold", 0.3)  # steering angle
        self.lateral_g_threshold = self.config.get("lateral_g_threshold", 0.2)  # G-force
        
        # Averaging windows for scenarios
        self.averaging_window_size = self.config.get("averaging_window_size", 100)
        self.scenario_data = {
            "straight": {f"port_{i}": deque(maxlen=self.averaging_window_size) for i in range(1, 7)},
            "turn_left": {f"port_{i}": deque(maxlen=self.averaging_window_size) for i in range(1, 7)},
            "turn_right": {f"port_{i}": deque(maxlen=self.averaging_window_size) for i in range(1, 7)}
        }
        
        # Histogram configuration
        self.histogram_bins = self.config.get("histogram_bins", 20)
        self.histogram_range = self.config.get("histogram_range", [-3.0, 3.0])
    
    def calculate_cp(self, pressure_port: float, reference_dynamic: float, reference_static: float) -> float:
        """
        Calculate coefficient of pressure (Cp)
        Cp = (P - P_static) / (P_dynamic - P_static)
        
        Where:
        - P = pressure at measurement port
        - P_static = static reference pressure (port 8)
        - P_dynamic = dynamic reference pressure (port 7)
        """
        if reference_dynamic is None or reference_static is None:
            return 0.0
        
        denominator = reference_dynamic - reference_static
        if abs(denominator) < 0.001:  # Avoid division by zero
            return 0.0
        
        return (pressure_port - reference_static) / denominator
    
    def calculate_cpt(self, pressure_port: float, reference_dynamic: float, reference_static: float) -> float:
        """
        Calculate coefficient of total pressure (Cpt)
        Cpt = (P - P_static) / (P_dynamic - P_static)
        
        For total pressure ports, this is similar to Cp but represents total pressure coefficient
        """
        return self.calculate_cp(pressure_port, reference_dynamic, reference_static)
    
    def detect_scenario(self, steering: float, lateral_g: float) -> str:
        """
        Detect current car scenario based on steering and lateral G-forces
        Returns: 'straight', 'turn_left', or 'turn_right'
        """
        abs_steering = abs(steering)
        abs_lateral_g = abs(lateral_g)
        
        # Check if turning
        if abs_steering > self.turn_threshold or abs_lateral_g > self.lateral_g_threshold:
            if steering > 0 or lateral_g > 0:
                return "turn_left"
            else:
                return "turn_right"
        
        # Otherwise straight
        return "straight"
    
    def process_pressure_data(self, pressure_data: Dict, steering: float, lateral_g: float) -> Dict:
        """
        Process pressure data and calculate coefficients
        
        Expected pressure_data format:
        {
            "pressure_port_1": float,
            "pressure_port_2": float,
            ...
            "pressure_port_8": float
        }
        """
        results = {
            "coefficients": {},
            "scenario": self.detect_scenario(steering, lateral_g),
            "averages": {}
        }
        
        # Get reference pressures
        ref_dynamic = pressure_data.get(f"pressure_port_{self.reference_port_dynamic}")
        ref_static = pressure_data.get(f"pressure_port_{self.reference_port_static}")
        
        if ref_dynamic is None or ref_static is None:
            return results
        
        # Calculate coefficients for measurement ports (1-6)
        for port_num in range(1, 7):
            port_key = f"pressure_port_{port_num}"
            pressure = pressure_data.get(port_key)
            
            if pressure is not None:
                # Calculate Cp
                cp = self.calculate_cp(pressure, ref_dynamic, ref_static)
                results["coefficients"][f"cp_port_{port_num}"] = cp
                
                # Calculate Cpt (can be same as Cp depending on port type)
                cpt = self.calculate_cpt(pressure, ref_dynamic, ref_static)
                results["coefficients"][f"cpt_port_{port_num}"] = cpt
                
                # Add to scenario averaging
                scenario = results["scenario"]
                scenario_port_key = f"port_{port_num}"
                self.scenario_data[scenario][scenario_port_key].append(cp)
        
        # Calculate scenario averages
        results["averages"] = self.get_scenario_averages()
        
        return results
    
    def get_scenario_averages(self) -> Dict:
        """Get average and standard deviation coefficient values for each scenario"""
        averages = {}
        
        for scenario, port_data in self.scenario_data.items():
            scenario_avg = {}
            for port_key, values in port_data.items():
                if len(values) > 0:
                    port_num = port_key.replace("port_", "")
                    values_list = list(values)
                    scenario_avg[f"cp_port_{port_num}_avg"] = statistics.mean(values_list)
                    scenario_avg[f"cp_port_{port_num}_std"] = statistics.stdev(values_list) if len(values_list) > 1 else 0.0
                    scenario_avg[f"cp_port_{port_num}_count"] = len(values_list)
                    scenario_avg[f"cp_port_{port_num}_min"] = min(values_list)
                    scenario_avg[f"cp_port_{port_num}_max"] = max(values_list)
            
            if scenario_avg:
                averages[scenario] = scenario_avg
        
        return averages
    
    def get_histogram_data(self, scenario: str, port: int) -> Dict:
        """Get histogram data for a specific scenario and port"""
        port_key = f"port_{port}"
        if scenario not in self.scenario_data:
            return {"bins": [], "counts": [], "range": self.histogram_range}
        
        values = list(self.scenario_data[scenario][port_key])
        if len(values) == 0:
            return {"bins": [], "counts": [], "range": self.histogram_range}
        
        # Calculate histogram
        counts, bin_edges = np.histogram(
            values,
            bins=self.histogram_bins,
            range=self.histogram_range
        )
        
        # Convert to percentages
        total = len(values)
        percentages = (counts / total * 100) if total > 0 else counts
        
        # Bin centers for plotting
        bin_centers = [(bin_edges[i] + bin_edges[i+1]) / 2 for i in range(len(bin_edges) - 1)]
        
        return {
            "bins": bin_centers,
            "counts": counts.tolist(),
            "percentages": percentages.tolist(),
            "range": self.histogram_range,
            "total_samples": total
        }
    
    def get_all_histograms(self, scenario: str) -> Dict:
        """Get histogram data for all ports in a scenario"""
        histograms = {}
        for port in range(1, 7):
            histograms[f"port_{port}"] = self.get_histogram_data(scenario, port)
        return histograms
    
    def reset_scenario_data(self, scenario: Optional[str] = None):
        """Reset averaging data for a scenario (or all if None)"""
        if scenario:
            if scenario in self.scenario_data:
                for port_key in self.scenario_data[scenario]:
                    self.scenario_data[scenario][port_key].clear()
        else:
            for scenario_data in self.scenario_data.values():
                for port_key in scenario_data:
                    scenario_data[port_key].clear()

