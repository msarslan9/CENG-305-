# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: algorithms/round_robin.py
# Date: 12-12-2025
# --------------------------------------------

"""
Round Robin (RR) Scheduling Algorithm
Preemptive scheduling algorithm with time quantum
"""

from collections import deque


def simulate_rr(processes, tq):
    """
    Round robin (preemptive) scheduling algorithm - tq parametresi önemli.
    
    Args:
        processes: List of tuples (pid, arrival_time, burst_time, priority)
        tq: Time quantum (zaman dilimi)
    
    Returns:
        tuple: (results_dict, gantt_chart, cpu_utilization, total_time, logs, idle_time)
    """
    # her processin ne kadar süresi kaldı (rem) onu takip ediyorum
    procs_map = {p[0]: {'arr':p[1], 'rem':p[2], 'burst':p[2], 'pri':p[3]} for p in processes}
    
    time = 0
    gantt = []
    idle = 0
    ready = deque() # kuyruk yapısı için deque kullandım, daha pratik
    arrived = set() # kuyruğa girenleri not ediyorum
    n = len(processes)
    completed = 0
    logs = []

    # belli bir t anında gelenleri kuyruğa ekleyen fonksiyonum
    def add_arrivals_at(t):
        for p in processes:
            if p[1] == t and p[0] not in arrived:
                ready.append(p[0])
                arrived.add(p[0])
                logs.append(f"[{t:02d}] ARRIVAL: {p[0]} joined the Ready Queue")

    # t=0 da gelen var mı diye baktım
    add_arrivals_at(0)
    
    # kimse yoksa ilk gelene kadar bekle
    if not ready:
        next_arr = min(p[1] for p in processes)
        gantt.append(("idle", time, next_arr))
        idle += next_arr - time
        time = next_arr
        add_arrivals_at(time)

    while completed < n:
        if not ready:
            # kuyruk boş ama bitmeyen işler varsa idle bekledim
            remaining_procs = [p for p in processes if p[0] not in arrived]
            if not remaining_procs: 
                break 
            
            next_arr = min(p[1] for p in remaining_procs)
            gantt.append(("idle", time, next_arr))
            idle += next_arr - time
            time = next_arr
            add_arrivals_at(time)
            continue
            
        pid = ready.popleft() # sıradakini aldım
        p = procs_map[pid]
        
        # tq kadar mı çalışacak yoksa daha az mı kaldı?
        run_time = min(tq, p['rem'])
        start = time
        end = time + run_time
        
        gantt.append((pid, start, end))
        logs.append(f"[{start:02d}] RUNNING: {pid} for {run_time}s")
        
        # hocam burası kritik: işlem çalışırken (start -> end arası) yeni gelenleri kaçırmamak için
        # saniye saniye kontrol edip kuyruğa ekledim
        for t in range(start + 1, end + 1):
            add_arrivals_at(t)
            
        time = end
        p['rem'] -= run_time # çalışılan süreyi düştüm
        
        if p['rem'] == 0:
            completed += 1
            procs_map[pid]['finish'] = time
            logs.append(f"[{time:02d}] FINISHED: {pid}")
        else:
            # bitmediyse kuyruğun en arkasına geri gönderdim
            ready.append(pid)
            logs.append(f"[{time:02d}] QUANTUM EXPIRED: {pid} re-queued")
            
    # sonuçları toparlıyorum
    res = {}
    for pid, vals in procs_map.items():
        res[pid] = {
            'finish': vals['finish'], 
            'turnaround': vals['finish'] - vals['arr'], 
            'waiting': (vals['finish'] - vals['arr']) - vals['burst'],
            'burst': vals['burst']
        }
        
    total_time = time
    cpu_util = (total_time - idle) / total_time * 100 if total_time > 0 else 0.0
    return res, gantt, cpu_util, total_time, logs, idle

