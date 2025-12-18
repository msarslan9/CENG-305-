# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: algorithms/fcfs.py
# Date: 12-12-2025
# --------------------------------------------

"""
First-Come, First-Served (FCFS) Scheduling Algorithm
Non-preemptive scheduling algorithm
"""


def simulate_fcfs(processes):
    """
    First-come, first-served (non-preemptive) scheduling algorithm.
    
    Args:
        processes: List of tuples (pid, arrival_time, burst_time, priority)
    
    Returns:
        tuple: (results_dict, gantt_chart, cpu_utilization, total_time, logs, idle_time)
    """
    # hocam fcfs olduğu için geliş zamanına (arrival) göre sıraladım
    procs_sorted = sorted(processes, key=lambda x: (x[1],))
    time = 0
    gantt = []
    idle = 0
    res = {}
    logs = []
    
    for pid, arr, burst, pri in procs_sorted:
        # eğer process gelmediyse cpu boş beklesin (idle)
        if time < arr:
            gantt.append(("idle", time, arr))
            logs.append(f"[{time:02d}] IDLE: Waiting for arrival...")
            idle += arr - time
            time = arr
        
        # işlemi çalıştırıyorum
        start = time
        end = time + burst
        gantt.append((pid, start, end))
        logs.append(f"[{start:02d}] EXECUTE: {pid} started (Burst: {burst})")
        time += burst
        logs.append(f"[{time:02d}] COMPLETE: {pid} finished task.")
        
        # değerleri hesaplayıp sözlüğe atıyorum
        res[pid] = {
            'finish': time, 
            'turnaround': time - arr, 
            'waiting': (time - arr) - burst,
            'burst': burst
        }
        
    total_time = time
    # cpu kullanım yüzdesi hesabı
    cpu_util = (total_time - idle) / total_time * 100 if total_time > 0 else 0.0
    return res, gantt, cpu_util, total_time, logs, idle

