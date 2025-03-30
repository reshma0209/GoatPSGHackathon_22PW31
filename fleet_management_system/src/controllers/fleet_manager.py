import time
import logging
from typing import Dict, List, Tuple, Optional, Callable
from models.robot import Robot, RobotStatus
from models.nav_graph import NavGraph

class FleetManager:
    """
    Manages a fleet of robots, including task assignment and state tracking.
    """
    def __init__(self, nav_graph: NavGraph, log_file: str = "logs/fleet_logs.txt"):
        """
        Initialize the fleet manager.
        
        Args:
            nav_graph: NavGraph instance representing the environment.
            log_file: Path to the log file.
        """
        self.nav_graph = nav_graph
        self.robots: Dict[str, Robot] = {}
        self.selected_robot: Optional[str] = None
        self.next_robot_id = 1
        self.log_file = log_file
        
        # Initialize logging
        self.setup_logging()
    
    def setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, mode='a'),
                logging.StreamHandler()
            ]
        )
    
    def log_message(self, message: str) -> None:
        """
        Log a message to the log file.
        
        Args:
            message: Message to log.
        """
        logging.info(message)
    
    def spawn_robot(self, vertex_index: int) -> str:
        """
        Spawn a new robot at the specified vertex.
        
        Args:
            vertex_index: Index of the vertex where the robot will spawn.
            
        Returns:
            ID of the spawned robot.
        """
        robot_id = f"Robot_{self.next_robot_id}"
        self.next_robot_id += 1
        
        # Create a new robot
        robot = Robot(robot_id, vertex_index, self.log_message)
        self.robots[robot_id] = robot
        
        self.log_message(f"Spawned {robot_id} at vertex {vertex_index}")
        return robot_id
    
    def assign_task(self, robot_id: str, target_vertex: int) -> bool:
        """
        Assign a navigation task to a robot.
        
        Args:
            robot_id: ID of the robot.
            target_vertex: Destination vertex index.
            
        Returns:
            True if task was assigned successfully, False otherwise.
        """
        if robot_id not in self.robots:
            self.log_message(f"Cannot assign task: Robot {robot_id} not found")
            return False
            
        robot = self.robots[robot_id]
        current_vertex = robot.current_vertex
        
        # Find path to target
        path = self.nav_graph.find_path(current_vertex, target_vertex)
        
        if not path:
            self.log_message(f"No path found from vertex {current_vertex} to {target_vertex}")
            return False
            
        # Check if the first lane is available
        if len(path) > 1:
            from_vertex, to_vertex = path[0], path[1]
            if not self.nav_graph.is_lane_free(from_vertex, to_vertex):
                self.log_message(f"Cannot start task: Lane from {from_vertex} to {to_vertex} is occupied")
                return False
                
            # Occupy the first lane
            self.nav_graph.occupy_lane(from_vertex, to_vertex, robot_id)
        
        # Assign the task to the robot
        success = robot.assign_task(target_vertex, path)
        
        if success:
            self.log_message(f"Assigned task to {robot_id}: Navigate from {current_vertex} to {target_vertex}")
        else:
            self.log_message(f"Failed to assign task to {robot_id}")
            
        return success
    
    def select_robot(self, vertex_index: int) -> Optional[str]:
        """
        Select a robot at the specified vertex.
        
        Args:
            vertex_index: Index of the vertex.
            
        Returns:
            ID of the selected robot, or None if no robot found.
        """
        for robot_id, robot in self.robots.items():
            if robot.is_selected(vertex_index):
                self.selected_robot = robot_id
                self.log_message(f"Selected {robot_id} at vertex {vertex_index}")
                return robot_id
                
        self.selected_robot = None
        return None
    
    def get_selected_robot(self) -> Optional[str]:
        """
        Get the ID of the currently selected robot.
        
        Returns:
            ID of the selected robot, or None if no robot is selected.
        """
        return self.selected_robot
    
    def update_robots(self) -> None:
        """Update the state of all robots."""
        for robot in self.robots.values():
            robot.update(
                self.nav_graph.is_lane_free,
                self.nav_graph.occupy_lane,
                self.nav_graph.free_lane
            )
    
    def get_all_robots(self) -> Dict[str, Robot]:
        """
        Get all robots in the fleet.
        
        Returns:
            Dictionary mapping robot IDs to Robot instances.
        """
        return self.robots
    
    def get_robot_positions(self) -> Dict[str, Tuple[int, int, float]]:
        """
        Get the current positions of all robots.
        
        Returns:
            Dictionary mapping robot IDs to positions (from_vertex, to_vertex, progress).
        """
        positions = {}
        for robot_id, robot in self.robots.items():
            positions[robot_id] = robot.get_position()
        return positions
    
    def get_robot_statuses(self) -> Dict[str, RobotStatus]:
        """
        Get the current statuses of all robots.
        
        Returns:
            Dictionary mapping robot IDs to RobotStatus values.
        """
        statuses = {}
        for robot_id, robot in self.robots.items():
            statuses[robot_id] = robot.get_status()
        return statuses