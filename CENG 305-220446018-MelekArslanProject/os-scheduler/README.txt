========================================================================
CS 305 - OPERATING SYSTEMS PROJECT
Process Scheduling Simulator (Grand Final Edition)
Student: Melek Arslan
ID: 220446018
Date: 17.12.2025
========================================================================

PROJECT OVERVIEW
-----------------
This project implements a CPU Scheduling Simulator with a "Future Tech" GUI. 
It simulates FCFS, SJF (Non-preemptive), Round Robin, and Priority algorithms.
Beyond standard simulation, it features advanced data analytics, scatter plots, 
and automated performance evaluation.

KEY FEATURES
------------
1. Algorithms: FCFS, SJF, Round Robin, Priority.
2. Analytics Dashboard: 
   - Grouped Bar Charts (Waiting vs Turnaround).
   - Scatter Plot (Burst Time vs Waiting Time correlation analysis).
3. Smart Analysis: Automatically detects and reports the most efficient algorithm.
4. Export Options: 
   - CSV (Excel) Export.
   - PDF Report Generation (Requires 'fpdf' library).
5. Visuals: Live Gantt Chart, CPU Gauge, System Load Monitor, and Matrix-style boot sequence.

INSTALLATION & REQUIREMENTS
---------------------------
The project uses standard Python libraries + 'tkinter'.
**OPTIONAL:** For PDF export functionality, please install 'fpdf':

   pip install fpdf

(Note: If fpdf is not installed, the system will automatically fallback to .txt export mode. The simulation will still work perfectly.)

HOW TO RUN
----------
1. Open terminal in the project folder.
2. Run the GUI version (Recommended):
   
   python scheduler_gui.py

3. (Optional) Run the CLI version:
   
   python scheduler.py processes.txt

USAGE GUIDE
-----------
- Click " Load Input File" to select 'processes.txt'.
- Adjust "Quantum" and "Speed" sliders as needed.
- Click " Run Simulation" to start the visualization.
- Check the "Analytics" tab for charts and the "Help" button for a user manual.

FILES INCLUDED
--------------
- scheduler_gui.py (Main Application)
- scheduler.py (Command Line Version)
- processes.txt (Sample Input)
- CS305_Report_MelekArslan.pdf (Project Report)
- README.txt (This file)

========================================================================