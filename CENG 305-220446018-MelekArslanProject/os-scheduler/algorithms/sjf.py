# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: algorithms/sjf.py
# Date: 12-12-2025
# --------------------------------------------

"""
Shortest Job First (SJF) Scheduling Algorithm
Non-preemptive scheduling algorithm
"""


def simulate_sjf(processes):
    """
    Shortest job first (non-preemptive) scheduling algorithm.
    
    Args:
        processes: List of tuples (pid, arrival_time, burst_time, priority)
    
    Returns:
        tuple: (results_dict, gantt_chart, cpu_utilization, total_time, logs, idle_time)
    """
    # listeyi bozmamak için kopyasını aldım
    procs = [list(p) for p in processes]
    procs.sort(key=lambda x: x[1])
    
    n = len(procs)
    time = 0
    gantt = []
    idle = 0
    res = {}
    completed = 0
    logs = []
    
    # hepsi bitene kadar dönüyorum
    while completed < n:
        # şu ana kadar gelmiş ve bitmemiş olanları buluyorum
        candidates = [p for p in procs if p[1] <= time and ('done' not in p)]
        
        if not candidates:
            # kimse yoksa bir sonraki process gelene kadar zamanı ilerlettim
            next_arr = min(p[1] for p in procs if 'done' not in p)
            if time < next_arr:
                gantt.append(("idle", time, next_arr))
                logs.append(f"[{time:02d}] IDLE: No process ready...")
                idle += next_arr - time
                time = next_arr
            continue
            
        # hocam sjf mantığı: burst süresi en kısa olanı seçtim.
        # eğer süreler eşitse geliş zamanına baktım (fcfs gibi).
        candidates.sort(key=lambda x: (x[2], x[1]))
        p = candidates[0]
        
        pid, arr, burst, pri = p[0], p[1], p[2], p[3]
        
        # non-preemptive olduğu için bitene kadar çalışıyor
        gantt.append((pid, time, time + burst))
        logs.append(f"[{time:02d}] SJF DECISION: {pid} selected (Burst: {burst})")
        time += burst
        logs.append(f"[{time:02d}] COMPLETE: {pid}")
        
        res[pid] = {
            'finish': time, 
            'turnaround': time - arr, 
            'waiting': (time - arr) - burst,
            'burst': burst
        }
        p.append('done') # bitti diye işaret koydum
        completed += 1
        
    total_time = time
    cpu_util = (total_time - idle) / total_time * 100 if total_time > 0 else 0.0
    return res, gantt, cpu_util, total_time, logs, idle

