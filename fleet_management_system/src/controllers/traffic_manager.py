from typing import Dict, List, Tuple, Set, Optional
from models.nav_graph import NavGraph

class TrafficManager:
    """
    Manages traffic and collision avoidance between robots.
    """
    def __init__(self, nav_graph: NavGraph):
        """
        Initialize the traffic manager.
        
        Args:
            nav_graph: NavGraph instance representing the environment.
        """
        self.nav_graph = nav_graph
        self.vertex_occupancy: Dict[int, str] = {}  # Maps vertex index to robot ID
        self.lane_wait_queue: Dict[str, List[str]] = {}  # Maps lane ID to list of waiting robot IDs
        
        # Initialize lane wait queues
        for lane in self.nav_graph.get_all_lanes():
            from_vertex, to_vertex = lane
            lane_id = self._get_lane_id(from_vertex, to_vertex)
            self.lane_wait_queue[lane_id] = []
    
    def _get_lane_id(self, from_vertex: int, to_vertex: int) -> str:
        """
        Generate a unique identifier for a lane.
        
        Args:
            from_vertex: Starting vertex index.
            to_vertex: Ending vertex index.
            
        Returns:
            String identifier for the lane.
        """
        return f"{from_vertex}->{to_vertex}"
    
    def request_lane(self, robot_id: str, from_vertex: int, to_vertex: int) -> bool:
        """
        Request permission for a robot to enter a lane.
        
        Args:
            robot_id: ID of the robot requesting permission.
            from_vertex: Starting vertex index.
            to_vertex: Ending vertex index.
            
        Returns:
            True if permission granted, False otherwise.
        """
        lane_id = self._get_lane_id(from_vertex, to_vertex)
        
        # Check if the lane exists
        if not self.nav_graph.lane_exists(from_vertex, to_vertex):
            return False
            
        # Check if the lane is free
        if self.nav_graph.is_lane_free(from_vertex, to_vertex):
            # Lane is free, grant permission
            self.nav_graph.occupy_lane(from_vertex, to_vertex, robot_id)
            return True
        else:
            # Lane is occupied, add robot to wait queue
            if robot_id not in self.lane_wait_queue[lane_id]:
                self.lane_wait_queue[lane_id].append(robot_id)
            return False
    
    def release_lane(self, robot_id: str, from_vertex: int, to_vertex: int) -> None:
        """
        Release a lane after a robot has traversed it.
        
        Args:
            robot_id: ID of the robot releasing the lane.
            from_vertex: Starting vertex index.
            to_vertex: Ending vertex index.
        """
        lane_id = self._get_lane_id(from_vertex, to_vertex)
        
        # Free the lane
        self.nav_graph.free_lane(from_vertex, to_vertex, robot_id)
        
        # Check wait queue
        if self.lane_wait_queue[lane_id]:
            next_robot_id = self.lane_wait_queue[lane_id].pop(0)
            # The next robot will request the lane on its next update
    
    def mark_vertex_occupied(self, vertex_index: int, robot_id: str) -> bool:
        """
        Mark a vertex as occupied by a robot.
        
        Args:
            vertex_index: Index of the vertex.
            robot_id: ID of the robot occupying the vertex.
            
        Returns:
            True if successful, False if vertex is already occupied.
        """
        if vertex_index in self.vertex_occupancy:
            return False
            
        self.vertex_occupancy[vertex_index] = robot_id
        return True
    
    def mark_vertex_free(self, vertex_index: int, robot_id: str) -> bool:
        """
        Mark a vertex as free.
        
        Args:
            vertex_index: Index of the vertex.
            robot_id: ID of the robot that was occupying the vertex.
            
        Returns:
            True if successful, False if vertex was not occupied by this robot.
        """
        if vertex_index in self.vertex_occupancy and self.vertex_occupancy[vertex_index] == robot_id:
            del self.vertex_occupancy[vertex_index]
            return True
        return False
    
    def is_vertex_occupied(self, vertex_index: int) -> bool:
        """
        Check if a vertex is occupied.
        
        Args:
            vertex_index: Index of the vertex.
            
        Returns:
            True if the vertex is occupied, False otherwise.
        """
        return vertex_index in self.vertex_occupancy
    
    def get_congestion_points(self) -> List[int]:
        """
        Get a list of vertices with high congestion (multiple robots waiting).
        
        Returns:
            List of vertex indices with high congestion.
        """
        congestion_count = {}
        
        # Count robots waiting for each vertex
        for lane_id, wait_queue in self.lane_wait_queue.items():
            if len(wait_queue) > 1:
                # Extract destination vertex from lane ID
                _, to_vertex = lane_id.split("->")
                to_vertex = int(to_vertex)
                
                if to_vertex not in congestion_count:
                    congestion_count[to_vertex] = 0
                congestion_count[to_vertex] += len(wait_queue)
        
        # Return vertices with high congestion
        return [vertex for vertex, count in congestion_count.items() if count > 2]
    
    def get_waiting_robots(self) -> Dict[str, Tuple[int, int]]:
        """
        Get all robots that are waiting to enter a lane.
        
        Returns:
            Dictionary mapping robot IDs to (from_vertex, to_vertex) tuples.
        """
        waiting_robots = {}
        
        for lane_id, wait_queue in self.lane_wait_queue.items():
            for robot_id in wait_queue:
                from_vertex, to_vertex = lane_id.split("->")
                waiting_robots[robot_id] = (int(from_vertex), int(to_vertex))
        
        return waiting_robots