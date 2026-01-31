# Banker's Algorithm Performance Analysis Tool
A hybrid Operating Systems project that combines a high-performance C Backend for deadlock avoidance logic with a modern Python Flask Frontend for real-time visualization and performance benchmarking.

# Features
- Core Algorithm : Full implementation of the Banker's Algorithm (Safety Check) in C.
- Interactive Web UI : Configure processes (P) and resources (R) via a clean, responsive interface.
- Resource Allocation Graph (RAG) : Live visualization of assignment and request edges using Mermaid.js .
- Performance Benchmarking : Real-time tracking of CPU time (seconds) and memory usage (bytes) using Chart.js .
- Auto-Compilation : The Flask server detects changes in the C source code and recompiles the binary automatically.
- Historical Tracking : Keep track of previous runs to compare how the algorithm scales with system load.

# Tech Stack
- Backend Engine : C (GCC)
- Web Framework : Python 3, Flask
- Visualizations : Mermaid.js (Graphs), Chart.js (Analytics)
- Styling : Modern CSS3 with a focus on readability and UX.

## Architecture
- bankers.c : The core logic. It uses dynamic memory allocation to simulate system states and determines if a request is safe. It outputs raw data and RAG edge definitions.
- server.py : The bridge. It manages the lifecycle of the C binary, parses the output using Regex, and serves the web interface.
- history.json : A lightweight persistent storage for benchmarking data.

# How the Algorithm Works
The safety check follows these steps:

1. Work/Finish Initialization : Copies available resources to a temporary 'Work' vector.
2. Scan for Progress : Searches for a process whose Need <= Work .
3. Resource Release : If found, the process "finishes," and its allocated resources are added back to Work .
4. Safety Determination : If all processes are marked as finished, the system is in a Safe State . Otherwise, it is Unsafe .


## Visualizations
# Resource Allocation Graph
The tool generates a live RAG where:
- Solid Lines (Resource → Process) : Represent currently allocated resources.
- Dashed Lines (Process → Resource) : Represent pending requests.

Analytics
- CPU Time : Measured using clock() in C to provide microsecond precision for algorithm execution.
- Memory Footprint : Calculated based on the size of the matrices ( Allocation , Max , Need ) and the Available vector.
