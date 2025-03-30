import os
import sys
import tkinter as tk
from typing import Dict, List, Tuple

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.nav_graph import NavGraph
from models.robot import Robot, RobotStatus
from controllers.fleet_manager import FleetManager
from controllers.traffic_manager import TrafficManager
from gui.fleet_gui import FleetGUI
from utils.helpers import ensure_directory_exists

def main():
    """
    Main function to initialize and start the Fleet Management System.
    """
    # Create necessary directories
    ensure_directory_exists("logs")
    ensure_directory_exists("../data")  # Adjusted for the actual location
    
    # Check if the navigation graph file exists
    nav_graph_file = "../data/nav_graph.json"  # Updated path
    if not os.path.exists(nav_graph_file):
        print(f"Error: Navigation graph file not found at {nav_graph_file}")
        print("Please make sure the file exists before running the application.")
        sys.exit(1)
    
    # Initialize the navigation graph
    try:
        nav_graph = NavGraph(nav_graph_file)
        print(f"Successfully loaded navigation graph: {len(nav_graph.vertices)} vertices, {len(nav_graph.lanes)} lanes")
    except Exception as e:
        print(f"Error loading navigation graph: {e}")
        sys.exit(1)
    
    # Initialize the fleet manager
    fleet_manager = FleetManager(nav_graph, "logs/fleet_logs.txt")
    
    # Initialize the traffic manager
    traffic_manager = TrafficManager(nav_graph)
    
    # Initialize the GUI
    root = tk.Tk()
    root.geometry("1000x800")
    app = FleetGUI(root, nav_graph, fleet_manager)
    
    # Start the Tkinter event loop
    print("Starting Fleet Management System...")
    root.mainloop()

if __name__ == "__main__":
    main()
