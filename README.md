# Fleet Management System

## Overview
This is a Python-based fleet management system with an interactive GUI. It allows users to dynamically manage robots navigating through an environment, avoiding collisions, and performing assigned tasks in real time. The system leverages modular components and effective algorithms to ensure dynamic interaction, traffic management, and efficient navigation.

---

## Features
### 1. **Visual Representation**
- Displays vertices (locations) and lanes (connections) from the navigation graph.
- Special locations like charging stations are highlighted in green, while regular vertices are shown in blue.
- Robots are visually distinct with unique colors, statuses (e.g., moving, waiting), and real-time animation as they navigate the graph.

### 2. **Robot Spawning**
- Allows users to spawn robots interactively by clicking on vertices.
- Each robot is assigned a unique identifier (e.g., `Robot_1`, `Robot_2`) upon creation.

### 3. **Task Assignment**
- Enables users to select a robot and assign it a destination vertex by clicking on the GUI.
- Robots dynamically compute their paths using BFS and begin navigating immediately.

### 4. **Traffic Management & Collision Avoidance**
- Implements real-time traffic negotiation, ensuring robots do not collide in lanes or intersections.
- Robots wait or queue at busy intersections or lanes and proceed when paths become clear.

### 5. **Real-Time Visualization**
- Robots are animated as they move along lanes, with their statuses (e.g., idle, moving, waiting) clearly indicated.

### 6. **Conflict Notifications**
- The GUI provides visual alerts when paths or vertices are blocked, assisting the user in managing traffic dynamically.

### 7. **Logging & Monitoring**
- Continuously logs robot actions (e.g., spawning, path navigation, task completion) in `fleet_logs.txt`.
- Optionally displays real-time logs in the GUI for immediate user feedback.

---

## Algorithms Used
### 1. **Breadth-First Search (BFS)**
- **Purpose:** Finds the shortest path between vertices in the navigation graph. This ensures robots take the most efficient route to their destination.

### Logical Workflows and Utilities:
These are not formal algorithms but are vital for system functionality:
- **Euclidean Distance Calculation:** Computes the distance between two points, useful for navigation.
- **Interpolation:** Animates robots smoothly during navigation.
- **Lane Management Logic:** Ensures robots avoid collisions and manage waiting queues.
- **Color Parsing and Contrast Calculation:** Enhances GUI readability.
- **Dynamic GUI Scaling:** Adjusts graph layout based on screen size.

---

## Demo
Check out the live demo of the Fleet Management System:
[Demo Link](https://drive.google.com/file/d/13t_3SDzz0yTfHeB1xopSoRsTgSeTtcSK/view?usp=sharing)
