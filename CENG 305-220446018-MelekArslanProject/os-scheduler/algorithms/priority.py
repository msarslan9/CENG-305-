# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: algorithms/priority.py
# Date: 12-12-2025
# --------------------------------------------

"""
Priority Scheduling Algorithm
Non-preemptive scheduling algorithm
Düşük sayı = yüksek öncelik
"""


def simulate_priority(processes):
    """
    Priority scheduling (non-preemptive) - düşük sayı yüksek öncelik demek.
    
    Args:
        processes: List of tuples (pid, arrival_time, burst_time, priority)
    
    Returns:
        tuple: (results_dict, gantt_chart, cpu_utilization, total_time, logs, idle_time)
    """
    procs = [list(p) for p in processes]
    procs.sort(key=lambda x: x[1])
    
    n = len(procs)
    time = 0
    gantt = []
    idle = 0
    res = {}
    completed = 0
    logs = []
    
    while completed < n:
        candidates = [p for p in procs if p[1] <= time and ('done' not in p)]
        
        if not candidates:
            next_arr = min(p[1] for p in procs if 'done' not in p)
            if time < next_arr:
                gantt.append(("idle", time, next_arr))
                idle += next_arr - time
                time = next_arr
            continue
            
        # önce prioritye göre (küçükten büyüğe), eşitse geliş sırasına göre sıraladım..
        candidates.sort(key=lambda x: (x[3], x[1]))
        p = candidates[0]
        
        pid, arr, burst, pri = p[0], p[1], p[2], p[3]
        
        gantt.append((pid, time, time + burst))
        logs.append(f"[{time:02d}] PRIORITY EXEC: {pid} (Prio: {pri})")
        time += burst
        
        res[pid] = {
            'finish': time, 
            'turnaround': time - arr, 
            'waiting': (time - arr) - burst,
            'burst': burst
        }
        p.append('done')
        completed += 1
        
    total_time = time
    cpu_util = (total_time - idle) / total_time * 100 if total_time > 0 else 0.0
    return res, gantt, cpu_util, total_time, logs, idle

