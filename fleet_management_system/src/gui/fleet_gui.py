import os
import tkinter as tk
from tkinter import messagebox, Canvas, Frame, Label, scrolledtext
import math
import time
from typing import Dict, List, Tuple, Optional, Callable

from models.nav_graph import NavGraph
from models.robot import Robot, RobotStatus
from controllers.fleet_manager import FleetManager
from controllers.traffic_manager import TrafficManager

class FleetGUI:
    """
    GUI for the Fleet Management System.
    Visualizes the navigation graph, robots, and allows user interaction.
    """
    def __init__(self, root: tk.Tk, nav_graph: NavGraph, fleet_manager: FleetManager):
        """
        Initialize the Fleet GUI.
        
        Args:
            root: Tkinter root window.
            nav_graph: NavGraph instance representing the environment.
            fleet_manager: FleetManager instance managing the robot fleet.
        """
        self.root = root
        self.root.title("Fleet Management System")
        self.nav_graph = nav_graph
        self.fleet_manager = fleet_manager
        
        self.canvas_width = 800
        self.canvas_height = 600
        self.vertex_radius = 15
        self.robot_radius = 10
        
        # Store screen coordinates mapped from vertex coordinates
        self.vertex_positions = {}
        
        # For scaling and translating vertex coordinates to screen coordinates
        self.scale_factor = 1
        self.offset_x = 0
        self.offset_y = 0
        
        # For tracking selected vertex and robot
        self.selected_vertex = None
        self.selected_robot = None
        
        # GUI elements
        self.canvas = None
        self.log_text = None
        self.status_label = None
        
        # For tracking canvas elements
        self.vertex_elements = {}
        self.lane_elements = {}
        self.robot_elements = {}
        self.label_elements = {}
        
        # Initialize the GUI
        self.setup_gui()
        self.calculate_layout()
        self.draw_navigation_graph()
        
        # Start the update loop
        self.update_display()
    
    def setup_gui(self) -> None:
        """Set up the main GUI layout."""
        # Main frame
        main_frame = Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for canvas
        canvas_frame = Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Canvas for visualization
        self.canvas = Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height, 
                            bg="white", borderwidth=2, relief="sunken")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add mouse event bindings
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # Bottom frame for logs and status
        bottom_frame = Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_label = Label(bottom_frame, text="Ready", anchor="w", padx=5)
        self.status_label.pack(fill=tk.X, side=tk.TOP)
        
        # Log text area
        log_frame = Frame(bottom_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_label = Label(log_frame, text="Event Log:")
        log_label.pack(anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Instructions label
        instructions = (
            "Click on any location to spawn a robot.\n"
            "Click on a robot to select it, then click on a destination to assign a task."
        )
        instructions_label = Label(main_frame, text=instructions, justify=tk.LEFT)
        instructions_label.pack(anchor="w", pady=5)
    
    def calculate_layout(self) -> None:
        """Calculate the layout by scaling vertex coordinates to fit the canvas."""
        vertices = self.nav_graph.get_all_vertices()
        
        if not vertices:
            return
            
        # Find the min/max coordinates
        min_x = min(vertex[1] for vertex in vertices)
        max_x = max(vertex[1] for vertex in vertices)
        min_y = min(vertex[2] for vertex in vertices)
        max_y = max(vertex[2] for vertex in vertices)
        
        # Add some padding
        padding = 50
        
        # Calculate scale factors for x and y dimensions
        width_scale = (self.canvas_width - 2 * padding) / (max_x - min_x if max_x > min_x else 1)
        height_scale = (self.canvas_height - 2 * padding) / (max_y - min_y if max_y > min_y else 1)
        
        # Use the smaller scale factor to maintain aspect ratio
        self.scale_factor = min(width_scale, height_scale)
        
        # Calculate offsets to center the graph
        self.offset_x = padding - min_x * self.scale_factor
        self.offset_y = padding - min_y * self.scale_factor
        
        # Store the screen positions of each vertex
        for vertex in vertices:
            index, x, y, _ = vertex
            screen_x = x * self.scale_factor + self.offset_x
            screen_y = y * self.scale_factor + self.offset_y
            self.vertex_positions[index] = (screen_x, screen_y)
    
    def vertex_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        """
        Convert vertex coordinates to screen coordinates.
        
        Args:
            x: Vertex x-coordinate.
            y: Vertex y-coordinate.
            
        Returns:
            Tuple of (screen_x, screen_y).
        """
        screen_x = x * self.scale_factor + self.offset_x
        screen_y = y * self.scale_factor + self.offset_y
        return screen_x, screen_y
    
    def screen_to_vertex_index(self, screen_x: float, screen_y: float) -> Optional[int]:
        """
        Find the vertex nearest to the given screen coordinates.
        
        Args:
            screen_x: Screen x-coordinate.
            screen_y: Screen y-coordinate.
            
        Returns:
            Index of the nearest vertex, or None if no vertex is close enough.
        """
        closest_dist = float('inf')
        closest_vertex = None
        
        for vertex_index, (x, y) in self.vertex_positions.items():
            dist = math.sqrt((screen_x - x) ** 2 + (screen_y - y) ** 2)
            if dist < self.vertex_radius * 1.5 and dist < closest_dist:
                closest_dist = dist
                closest_vertex = vertex_index
                
        return closest_vertex
    
    def draw_navigation_graph(self) -> None:
        """Draw the navigation graph on the canvas."""
        # Clear existing elements
        for element_id in self.lane_elements.values():
            self.canvas.delete(element_id)
        for element_id in self.vertex_elements.values():
            self.canvas.delete(element_id)
        for element_id in self.label_elements.values():
            self.canvas.delete(element_id)
            
        self.lane_elements = {}
        self.vertex_elements = {}
        self.label_elements = {}
        
        # Draw lanes first (so they're underneath vertices)
        lanes = self.nav_graph.get_all_lanes()
        for lane in lanes:
            from_vertex, to_vertex = lane
            if from_vertex in self.vertex_positions and to_vertex in self.vertex_positions:
                from_x, from_y = self.vertex_positions[from_vertex]
                to_x, to_y = self.vertex_positions[to_vertex]
                
                # Calculate angle for arrow head
                angle = math.atan2(to_y - from_y, to_x - from_x)
                
                # Calculate endpoint adjusted for vertex radius
                end_x = to_x - self.vertex_radius * math.cos(angle)
                end_y = to_y - self.vertex_radius * math.sin(angle)
                
                # Calculate start point adjusted for vertex radius
                start_x = from_x + self.vertex_radius * math.cos(angle)
                start_y = from_y + self.vertex_radius * math.sin(angle)
                
                # Draw lane
                lane_id = f"{from_vertex}->{to_vertex}"
                lane_element = self.canvas.create_line(
                    start_x, start_y, end_x, end_y,
                    arrow=tk.LAST, width=2, fill="gray"
                )
                self.lane_elements[lane_id] = lane_element
        
        # Draw vertices
        vertices = self.nav_graph.get_all_vertices()
        for vertex in vertices:
            index, _, _, attributes = vertex
            if index in self.vertex_positions:
                x, y = self.vertex_positions[index]
                
                # Determine vertex color based on attributes
                color = "#3498db"  # Default blue
                if attributes.get("is_charger", False):
                    color = "#2ecc71"  # Green for chargers
                
                # Draw vertex
                vertex_element = self.canvas.create_oval(
                    x - self.vertex_radius, y - self.vertex_radius,
                    x + self.vertex_radius, y + self.vertex_radius,
                    fill=color, outline="black", width=2
                )
                self.vertex_elements[index] = vertex_element
                
                # Add vertex name label
                name = attributes.get("name", f"V{index}")
                if name:
                    label_element = self.canvas.create_text(
                        x, y - self.vertex_radius - 10,
                        text=name, font=("Arial", 10, "bold")
                    )
                    self.label_elements[f"name_{index}"] = label_element
    
    def draw_robots(self) -> None:
        """Draw all robots on the canvas."""
        # Clear existing robot elements
        for element_id in self.robot_elements.values():
            self.canvas.delete(element_id)
        self.robot_elements = {}
        
        # Get current robot positions and statuses
        robot_positions = self.fleet_manager.get_robot_positions()
        robot_statuses = self.fleet_manager.get_robot_statuses()
        all_robots = self.fleet_manager.get_all_robots()
        
        # Draw each robot
        for robot_id, position in robot_positions.items():
            from_vertex, to_vertex, progress = position
            status = robot_statuses.get(robot_id)
            robot = all_robots.get(robot_id)
            
            if not robot:
                continue
                
            # Calculate robot position
            if status == RobotStatus.MOVING:
                # Interpolate position along the lane
                if from_vertex in self.vertex_positions and to_vertex in self.vertex_positions:
                    from_x, from_y = self.vertex_positions[from_vertex]
                    to_x, to_y = self.vertex_positions[to_vertex]
                    
                    # Adjust for vertex radius
                    angle = math.atan2(to_y - from_y, to_x - from_x)
                    start_x = from_x + self.vertex_radius * math.cos(angle)
                    start_y = from_y + self.vertex_radius * math.sin(angle)
                    end_x = to_x - self.vertex_radius * math.cos(angle)
                    end_y = to_y - self.vertex_radius * math.sin(angle)
                    
                    x = start_x + progress * (end_x - start_x)
                    y = start_y + progress * (end_y - start_y)
                else:
                    continue
            else:
                # Robot is at a vertex
                if from_vertex in self.vertex_positions:
                    x, y = self.vertex_positions[from_vertex]
                else:
                    continue
            
            # Determine robot color based on status
            color = robot.color
            outline_color = "black"
            
            if status == RobotStatus.WAITING:
                outline_color = "red"
            elif status == RobotStatus.TASK_COMPLETE:
                outline_color = "green"
            
            # Determine if this robot is selected
            width = 2
            if robot_id == self.selected_robot:
                width = 4
                
            # Draw robot
            robot_element = self.canvas.create_oval(
                x - self.robot_radius, y - self.robot_radius,
                x + self.robot_radius, y + self.robot_radius,
                fill=color, outline=outline_color, width=width
            )
            
            # Add robot ID label
            label_element = self.canvas.create_text(
                x, y, text=robot_id.split("_")[1], 
                font=("Arial", 8, "bold"), fill="white"
            )
            
            # Store elements
            self.robot_elements[robot_id] = (robot_element, label_element)
            
            # Add status indicator for waiting robots
            if status == RobotStatus.WAITING:
                wait_element = self.canvas.create_text(
                    x, y + self.robot_radius + 10,
                    text="WAIT", font=("Arial", 8), fill="red"
                )
                self.robot_elements[f"{robot_id}_wait"] = wait_element
    
    def on_canvas_click(self, event) -> None:
        """
        Handle click events on the canvas.
        
        Args:
            event: Tkinter event object.
        """
        x, y = event.x, event.y
        vertex_index = self.screen_to_vertex_index(x, y)
        
        if vertex_index is not None:
            # If no robot is selected, spawn a new robot or select an existing one
            if self.selected_robot is None:
                # Check if there's a robot at this vertex to select
                robot_id = self.fleet_manager.select_robot(vertex_index)
                
                if robot_id:
                    # Selected a robot
                    self.selected_robot = robot_id
                    self.update_status(f"Selected {robot_id}. Click on a destination.")
                else:
                    # Spawn a new robot
                    robot_id = self.fleet_manager.spawn_robot(vertex_index)
                    self.update_status(f"Spawned {robot_id}. Click on it to select.")
            else:
                # A robot is already selected, so assign a task to it
                success = self.fleet_manager.assign_task(self.selected_robot, vertex_index)
                
                if success:
                    self.update_status(
                        f"Assigned {self.selected_robot} to navigate to vertex {vertex_index}."
                    )
                else:
                    self.update_status(
                        f"Cannot assign task to {self.selected_robot}. Path may be blocked."
                    )
                
                # Deselect the robot
                self.selected_robot = None
                self.fleet_manager.selected_robot = None
        else:
            # Click was not on a vertex, deselect robot
            self.selected_robot = None
            self.fleet_manager.selected_robot = None
            self.update_status("Ready")
    
    def update_display(self) -> None:
        """Update the display and schedule the next update."""
        # Update all robots
        self.fleet_manager.update_robots()
        
        # Draw the robots
        self.draw_robots()
        
        # Update logs
        self.update_logs()
        
        # Schedule next update (30 FPS)
        self.root.after(33, self.update_display)
    
    def update_status(self, message: str) -> None:
        """
        Update the status message.
        
        Args:
            message: Status message to display.
        """
        self.status_label.config(text=message)
    
    def update_logs(self) -> None:
        """Update the log text area with the latest logs."""
        try:
            with open(self.fleet_manager.log_file, 'r') as f:
                logs = f.readlines()
                
                # Show only the last 10 log entries
                recent_logs = logs[-10:]
                
                log_text = "".join(recent_logs)
                
                # Update log text
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.END, log_text)
                self.log_text.see(tk.END)  # Scroll to the end
        except FileNotFoundError:
            pass
    
    def show_notification(self, message: str) -> None:
        """
        Show a popup notification.
        
        Args:
            message: Message to display.
        """
        messagebox.showinfo("Notification", message)