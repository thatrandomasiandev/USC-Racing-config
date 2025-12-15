"""
Telemetry Device Interface
For connecting to actual telemetry hardware or simulating data
"""

import serial
import time
import json
import requests
from datetime import datetime
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from internal.config.settings import settings

class TelemetryDevice:
    def __init__(self, port=None, api_url=None, baud=None, update_rate=None):
        self.port = port or settings.DEVICE_PORT
        self.api_url = api_url or settings.API_URL
        self.baud = baud or settings.DEVICE_BAUD
        self.update_rate = update_rate or settings.DEVICE_UPDATE_RATE_HZ
        self.running = False
        self.serial = None
        
    def connect(self):
        """Connect to telemetry device"""
        if self.port:
            try:
                self.serial = serial.Serial(self.port, self.baud, timeout=1)
                print(f"Connected to device on {self.port} at {self.baud} baud")
                return True
            except Exception as e:
                print(f"Failed to connect to {self.port}: {e}")
                return False
        return False
    
    def read_data(self):
        """Read data from device"""
        if self.serial and self.serial.is_open:
            try:
                line = self.serial.readline().decode('utf-8').strip()
                if line:
                    data = json.loads(line)
                    # Validate data structure
                    return self.validate_data(data)
            except json.JSONDecodeError:
                print(f"Invalid JSON from device: {line}")
            except UnicodeDecodeError:
                print("Invalid encoding from device")
            except Exception as e:
                print(f"Error reading from device: {e}")
        
        return None
    
    def validate_data(self, data: dict) -> dict:
        """Validate data structure against schema"""
        validated = {}
        initial_data = settings.get_initial_telemetry_data()
        
        # Only include fields that are in the schema
        for key in initial_data.keys():
            if key in data:
                validated[key] = data[key]
        
        return validated if validated else None
    
    def send_to_server(self, data):
        """Send telemetry data to server"""
        if not data:
            return False
            
        try:
            response = requests.post(
                f"{self.api_url}/api/telemetry",
                json=data,
                timeout=0.5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Failed to send data to server: {e}")
            return False
    
    def run(self, update_rate=None):
        """Main loop - read and send telemetry data"""
        if not self.port:
            print("No device port specified. Use TEL_DEVICE_PORT environment variable or pass port as argument.")
            return
        
        if not self.connect():
            print("Failed to connect to device. Exiting.")
            return
        
        self.running = True
        rate = update_rate or self.update_rate
        interval = 1.0 / rate
        
        print(f"Telemetry device started. Sending data at {rate}Hz to {self.api_url}")
        
        try:
            while self.running:
                start_time = time.time()
                
                data = self.read_data()
                if data:
                    self.send_to_server(data)
                
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\nStopping telemetry device...")
        finally:
            if self.serial and self.serial.is_open:
                self.serial.close()
            self.running = False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="USC Racing Telemetry Device Interface")
    parser.add_argument("port", nargs="?", help="Serial port (e.g., /dev/ttyUSB0 or COM3)")
    parser.add_argument("--api-url", help="API server URL")
    parser.add_argument("--baud", type=int, help="Baud rate")
    parser.add_argument("--rate", type=float, help="Update rate in Hz")
    
    args = parser.parse_args()
    
    device = TelemetryDevice(
        port=args.port,
        api_url=args.api_url,
        baud=args.baud,
        update_rate=args.rate
    )
    device.run()
