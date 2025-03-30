import json
from typing import Dict, List, Tuple, Any, Optional

class NavGraph:
    """
    Class to represent and manage the navigation graph.
    Parses the JSON graph representation and provides methods to access
    vertices, lanes, and navigate between them.
    """
    def __init__(self, graph_file: str):
        """
        Initialize the navigation graph from a JSON file.
        
        Args:
            graph_file: Path to the JSON file containing the navigation graph.
        """
        self.vertices = []  # List of vertices (locations)
        self.lanes = []  # List of lanes (paths between locations)
        self.vertex_name_to_index = {}  # Dictionary mapping vertex names to indices
        self.lane_occupancy = {}  # Dictionary tracking which lanes are currently occupied
        
        self.load_graph(graph_file)
    
    def load_graph(self, graph_file: str) -> None:
        """
        Load the navigation graph from a JSON file.
        
        Args:
            graph_file: Path to the JSON file.
        """
        try:
            with open(graph_file, 'r') as f:
                data = json.load(f)
                
            # In the provided JSON, the graph is in levels > level1 > vertices/lanes
            level_data = next(iter(data.get('levels', {}).values()))
            
            self.vertices = level_data.get('vertices', [])
            self.lanes = level_data.get('lanes', [])
            
            # Create a mapping of vertex names to indices for easier lookup
            for i, vertex in enumerate(self.vertices):
                attributes = vertex[2] if len(vertex) > 2 else {}
                name = attributes.get('name', f"Vertex_{i}")
                self.vertex_name_to_index[name] = i
                
            # Initialize lane occupancy
            for lane in self.lanes:
                lane_id = self._get_lane_id(lane[0], lane[1])
                self.lane_occupancy[lane_id] = None  # None means lane is free
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading navigation graph: {e}")
            raise
    
    def get_vertex_coordinates(self, vertex_index: int) -> Tuple[float, float]:
        """
        Get the x, y coordinates of a vertex.
        
        Args:
            vertex_index: Index of the vertex.
            
        Returns:
            Tuple of (x, y) coordinates.
        """
        if 0 <= vertex_index < len(self.vertices):
            return self.vertices[vertex_index][0], self.vertices[vertex_index][1]
        return 0, 0
    
    def get_vertex_attributes(self, vertex_index: int) -> Dict[str, Any]:
        """
        Get the attributes of a vertex.
        
        Args:
            vertex_index: Index of the vertex.
            
        Returns:
            Dictionary of vertex attributes.
        """
        if 0 <= vertex_index < len(self.vertices):
            attributes = self.vertices[vertex_index][2] if len(self.vertices[vertex_index]) > 2 else {}
            return attributes
        return {}
    
    def is_vertex_charger(self, vertex_index: int) -> bool:
        """
        Check if a vertex is a charging station.
        
        Args:
            vertex_index: Index of the vertex.
            
        Returns:
            True if the vertex is a charger, False otherwise.
        """
        attributes = self.get_vertex_attributes(vertex_index)
        return attributes.get('is_charger', False)
    
    def get_vertex_name(self, vertex_index: int) -> str:
        """
        Get the name of a vertex.
        
        Args:
            vertex_index: Index of the vertex.
            
        Returns:
            Name of the vertex.
        """
        attributes = self.get_vertex_attributes(vertex_index)
        return attributes.get('name', f"Vertex_{vertex_index}")
    
    def get_vertex_index_by_name(self, name: str) -> Optional[int]:
        """
        Get the index of a vertex by its name.
        
        Args:
            name: Name of the vertex.
            
        Returns:
            Index of the vertex, or None if not found.
        """
        return self.vertex_name_to_index.get(name)
    
    def get_connected_vertices(self, vertex_index: int) -> List[int]:
        """
        Get all vertices that can be reached from a given vertex.
        
        Args:
            vertex_index: Index of the source vertex.
            
        Returns:
            List of connected vertex indices.
        """
        connected = []
        for lane in self.lanes:
            if lane[0] == vertex_index:
                connected.append(lane[1])
        return connected
    
    def is_lane_free(self, from_vertex: int, to_vertex: int) -> bool:
        """
        Check if a lane is free (not occupied by any robot).
        
        Args:
            from_vertex: Starting vertex index.
            to_vertex: Ending vertex index.
            
        Returns:
            True if the lane is free, False otherwise.
        """
        lane_id = self._get_lane_id(from_vertex, to_vertex)
        return self.lane_occupancy.get(lane_id) is None
    
    def occupy_lane(self, from_vertex: int, to_vertex: int, robot_id: str) -> bool:
        """
        Mark a lane as occupied by a robot.
        
        Args:
            from_vertex: Starting vertex index.
            to_vertex: Ending vertex index.
            robot_id: ID of the robot occupying the lane.
            
        Returns:
            True if the lane was successfully occupied, False otherwise.
        """
        lane_id = self._get_lane_id(from_vertex, to_vertex)
        if lane_id in self.lane_occupancy and self.lane_occupancy[lane_id] is None:
            self.lane_occupancy[lane_id] = robot_id
            return True
        return False
    
    def free_lane(self, from_vertex: int, to_vertex: int, robot_id: str) -> bool:
        """
        Mark a lane as free.
        
        Args:
            from_vertex: Starting vertex index.
            to_vertex: Ending vertex index.
            robot_id: ID of the robot that was occupying the lane.
            
        Returns:
            True if the lane was successfully freed, False otherwise.
        """
        lane_id = self._get_lane_id(from_vertex, to_vertex)
        if lane_id in self.lane_occupancy and self.lane_occupancy[lane_id] == robot_id:
            self.lane_occupancy[lane_id] = None
            return True
        return False
    
    def lane_exists(self, from_vertex: int, to_vertex: int) -> bool:
        """
        Check if a lane exists between two vertices.
        
        Args:
            from_vertex: Starting vertex index.
            to_vertex: Ending vertex index.
            
        Returns:
            True if the lane exists, False otherwise.
        """
        for lane in self.lanes:
            if lane[0] == from_vertex and lane[1] == to_vertex:
                return True
        return False
    
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
    
    def get_all_vertices(self) -> List[Tuple[int, float, float, Dict[str, Any]]]:
        """
        Get all vertices with their indices, coordinates, and attributes.
        
        Returns:
            List of tuples (index, x, y, attributes).
        """
        result = []
        for i, vertex in enumerate(self.vertices):
            x, y = vertex[0], vertex[1]
            attributes = vertex[2] if len(vertex) > 2 else {}
            result.append((i, x, y, attributes))
        return result
    
    def get_all_lanes(self) -> List[Tuple[int, int]]:
        """
        Get all lanes as pairs of vertex indices.
        
        Returns:
            List of tuples (from_vertex, to_vertex).
        """
        result = []
        for lane in self.lanes:
            result.append((lane[0], lane[1]))
        return result
    
    def find_path(self, start_vertex: int, end_vertex: int) -> List[int]:
        """
        Find a path from start_vertex to end_vertex using BFS.
        
        Args:
            start_vertex: Starting vertex index.
            end_vertex: Ending vertex index.
            
        Returns:
            List of vertex indices representing the path (including start and end).
        """
        if start_vertex == end_vertex:
            return [start_vertex]
            
        # BFS to find the shortest path
        queue = [(start_vertex, [start_vertex])]
        visited = set([start_vertex])
        
        while queue:
            (vertex, path) = queue.pop(0)
            
            # Get all adjacent vertices
            for next_vertex in self.get_connected_vertices(vertex):
                if next_vertex == end_vertex:
                    return path + [next_vertex]
                if next_vertex not in visited:
                    visited.add(next_vertex)
                    queue.append((next_vertex, path + [next_vertex]))
        
        # No path found
        return []