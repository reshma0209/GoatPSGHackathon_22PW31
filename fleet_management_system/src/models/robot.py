import time
import random
from enum import Enum
from typing import List, Tuple, Optional, Callable

class RobotStatus(Enum):
    """Enum representing the possible statuses of a robot."""
    IDLE = "idle"
    MOVING = "moving"
    WAITING = "waiting"
    CHARGING = "charging"
    TASK_COMPLETE = "task_complete"

class Robot:
    """
    Class representing a robot in the fleet management system.
    Manages robot state, position, and navigation tasks.
    """
    # Available colors for robots
    COLORS = [
        "#FF5733", "#33FF57", "#3357FF", "#FF33F5", "#F5FF33",
        "#33FFF5", "#FF5733", "#FF8C33", "#33FF8C", "#8C33FF",
        "#FF338C", "#338CFF"
    ]
    
    def __init__(self, robot_id: str, current_vertex: int, log_callback: Callable = None):
        """
        Initialize a robot.
        
        Args:
            robot_id: Unique identifier for the robot.
            current_vertex: Index of the vertex where the robot starts.
            log_callback: Function to call for logging robot actions.
        """
        self.id = robot_id
        self.current_vertex = current_vertex
        self.target_vertex = None
        self.path = []
        self.current_path_index = 0
        self.status = RobotStatus.IDLE
        self.color = random.choice(self.COLORS)
        self.progress = 0.0  # Progress along the current lane (0.0 to 1.0)
        self.speed = 0.05  # Speed at which the robot moves (progress units per update)
        self.from_vertex = None  # Current lane starting vertex
        self.to_vertex = None  # Current lane ending vertex
        self.waiting_time = 0  # Time spent waiting
        self.log_callback = log_callback or (lambda msg: None)  # Default no-op callback
        
        self.log(f"Robot {self.id} spawned at vertex {self.current_vertex}")
    
    def assign_task(self, target_vertex: int, path: List[int]) -> bool:
        """
        Assign a navigation task to the robot.
        
        Args:
            target_vertex: Destination vertex index.
            path: List of vertex indices forming the path.
            
        Returns:
            True if task was assigned successfully, False otherwise.
        """
        if not path or len(path) < 2:
            self.log(f"Invalid path assigned to Robot {self.id}")
            return False
            
        self.target_vertex = target_vertex
        self.path = path
        self.current_path_index = 0
        self.status = RobotStatus.MOVING
        self.progress = 0.0
        self.from_vertex = path[0]
        self.to_vertex = path[1]
        
        self.log(f"Robot {self.id} assigned task to navigate to vertex {target_vertex} via path {path}")
        return True
    
    def update(self, is_lane_free_func, occupy_lane_func, free_lane_func) -> None:
        """
        Update the robot's state.
        
        Args:
            is_lane_free_func: Function to check if a lane is free.
            occupy_lane_func: Function to occupy a lane.
            free_lane_func: Function to free a lane.
        """
        if self.status == RobotStatus.IDLE or self.status == RobotStatus.TASK_COMPLETE:
            return
            
        if self.status == RobotStatus.WAITING:
            self.waiting_time += 1
            # Check if the lane is now free
            if is_lane_free_func(self.from_vertex, self.to_vertex):
                if occupy_lane_func(self.from_vertex, self.to_vertex, self.id):
                    self.status = RobotStatus.MOVING
                    self.waiting_time = 0
                    self.log(f"Robot {self.id} resumed movement from vertex {self.from_vertex} to {self.to_vertex}")
            return
            
        if self.status == RobotStatus.MOVING:
            # Update progress along the current lane
            self.progress += self.speed
            
            if self.progress >= 1.0:
                # Reached the next vertex
                self.progress = 0.0
                self.current_vertex = self.to_vertex
                free_lane_func(self.from_vertex, self.to_vertex, self.id)
                self.log(f"Robot {self.id} reached vertex {self.current_vertex}")
                
                self.current_path_index += 1
                
                # Check if we've reached the destination
                if self.current_path_index >= len(self.path) - 1:
                    self.status = RobotStatus.TASK_COMPLETE
                    self.log(f"Robot {self.id} completed task at vertex {self.current_vertex}")
                    return
                    
                # Start moving along the next lane
                self.from_vertex = self.path[self.current_path_index]
                self.to_vertex = self.path[self.current_path_index + 1]
                
                # Check if the next lane is free
                if is_lane_free_func(self.from_vertex, self.to_vertex):
                    if occupy_lane_func(self.from_vertex, self.to_vertex, self.id):
                        self.log(f"Robot {self.id} moving from vertex {self.from_vertex} to {self.to_vertex}")
                    else:
                        self.status = RobotStatus.WAITING
                        self.log(f"Robot {self.id} couldn't occupy lane from {self.from_vertex} to {self.to_vertex}")
                else:
                    self.status = RobotStatus.WAITING
                    self.log(f"Robot {self.id} waiting at vertex {self.current_vertex} - lane to {self.to_vertex} occupied")
    
    def get_position(self) -> Tuple[int, int, float]:
        """
        Get the current position of the robot.
        
        Returns:
            Tuple of (from_vertex, to_vertex, progress) indicating the robot's position.
        """
        if self.status == RobotStatus.MOVING:
            return (self.from_vertex, self.to_vertex, self.progress)
        return (self.current_vertex, self.current_vertex, 0.0)
    
    def get_status(self) -> RobotStatus:
        """
        Get the current status of the robot.
        
        Returns:
            RobotStatus enum value.
        """
        return self.status
    
    def is_selected(self, vertex_index: int) -> bool:
        """
        Check if the robot is at the specified vertex.
        
        Args:
            vertex_index: The vertex to check.
            
        Returns:
            True if the robot is at this vertex, False otherwise.
        """
        return self.current_vertex == vertex_index and (
            self.status == RobotStatus.IDLE or 
            self.status == RobotStatus.WAITING or 
            self.status == RobotStatus.TASK_COMPLETE
        )
    
    def log(self, message: str) -> None:
        """
        Log a robot action or status change.
        
        Args:
            message: Message to log.
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        if self.log_callback:
            self.log_callback(log_message)