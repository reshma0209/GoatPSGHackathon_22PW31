import os
import math
import time
from typing import List, Tuple, Dict, Optional

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate the Euclidean distance between two points.
    
    Args:
        x1: X-coordinate of the first point.
        y1: Y-coordinate of the first point.
        x2: X-coordinate of the second point.
        y2: Y-coordinate of the second point.
        
    Returns:
        The Euclidean distance.
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def interpolate_position(start_pos: Tuple[float, float], 
                        end_pos: Tuple[float, float], 
                        progress: float) -> Tuple[float, float]:
    """
    Interpolate between two positions based on progress.
    
    Args:
        start_pos: Starting position as (x, y).
        end_pos: Ending position as (x, y).
        progress: Progress between 0.0 and 1.0.
        
    Returns:
        Interpolated position as (x, y).
    """
    x1, y1 = start_pos
    x2, y2 = end_pos
    x = x1 + progress * (x2 - x1)
    y = y1 + progress * (y2 - y1)
    return (x, y)

def get_timestamp() -> str:
    """
    Get the current timestamp as a formatted string.
    
    Returns:
        Formatted timestamp string.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")

def format_log_entry(message: str) -> str:
    """
    Format a log entry with timestamp.
    
    Args:
        message: Log message.
        
    Returns:
        Formatted log entry.
    """
    timestamp = get_timestamp()
    return f"[{timestamp}] {message}\n"

def write_log(log_file: str, message: str) -> None:
    """
    Write a message to a log file.
    
    Args:
        log_file: Path to the log file.
        message: Message to log.
    """
    log_entry = format_log_entry(message)
    
    # Ensure the directory exists
    log_dir = os.path.dirname(log_file)
    ensure_directory_exists(log_dir)
    
    with open(log_file, 'a') as f:
        f.write(log_entry)

def read_recent_logs(log_file: str, num_entries: int = 10) -> List[str]:
    """
    Read the most recent log entries from a log file.
    
    Args:
        log_file: Path to the log file.
        num_entries: Number of recent entries to read.
        
    Returns:
        List of log entries.
    """
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            return lines[-num_entries:] if lines else []
    except FileNotFoundError:
        return []

def find_shortest_path(graph: Dict[int, List[int]], start: int, end: int) -> List[int]:
    """
    Find the shortest path between two vertices using BFS.
    
    Args:
        graph: Adjacency list representation of the graph.
        start: Starting vertex.
        end: Ending vertex.
        
    Returns:
        List of vertex indices representing the path.
    """
    # Base case
    if start == end:
        return [start]
        
    # BFS
    visited = {start}
    queue = [(start, [start])]
    
    while queue:
        (vertex, path) = queue.pop(0)
        
        for next_vertex in graph.get(vertex, []):
            if next_vertex == end:
                return path + [next_vertex]
            if next_vertex not in visited:
                visited.add(next_vertex)
                queue.append((next_vertex, path + [next_vertex]))
    
    # No path found
    return []

def parse_color(color_str: str) -> Tuple[int, int, int]:
    """
    Parse a color string in hex format to RGB.
    
    Args:
        color_str: Hex color string (e.g., "#FF5733").
        
    Returns:
        Tuple of (red, green, blue) values (0-255).
    """
    color_str = color_str.lstrip('#')
    return tuple(int(color_str[i:i+2], 16) for i in (0, 2, 4))

def generate_contrasting_color(color_str: str) -> str:
    """
    Generate a contrasting color for text on a given background color.
    
    Args:
        color_str: Hex color string for the background.
        
    Returns:
        Hex color string for contrasting text.
    """
    r, g, b = parse_color(color_str)
    # Calculate luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Choose black or white based on luminance
    return "#000000" if luminance > 0.5 else "#FFFFFF"