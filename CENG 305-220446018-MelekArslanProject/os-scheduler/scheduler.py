# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: scheduler.py
# Date: 12-12-2025
# --------------------------------------------

"""
Komut satırı arayüzü için scheduler
Modüler yapıya uygun olarak güncellendi
"""

import sys

# Modüler importlar
from algorithms import simulate_fcfs, simulate_sjf, simulate_rr, simulate_priority
from utils import parse_input_file, format_gantt, print_table, compute_averages


def run_all(processes, rr_tq):
    """
    Tüm algoritmaları çalıştır ve sonuçları göster
    
    Args:
        processes: Process listesi
        rr_tq: Round Robin için time quantum
    """
    # çıktı tablosunda karışıklık olmasın diye arrival time'a göre sıralı basıyorum.
    print_order = [p[0] for p in sorted(processes, key=lambda x: x[1])]
    
    algos = [
        ("FCFS", simulate_fcfs, None),
        ("SJF", simulate_sjf, None),
        (f"Round Robin (tq={rr_tq})", lambda p: simulate_rr(p, rr_tq), None),
        ("Priority", simulate_priority, None)
    ]
    
    for name, func, _ in algos:
        results, gantt, cpu_util, total_time, logs, idle = func(processes)
        print(f"\n--- scheduling algorithm: {name} ---")
        print("gantt chart:", format_gantt(gantt))
        print()
        print_table(results, print_order)
        
        avg_tat, avg_wt = compute_averages(results)
        print()
        print(f"average turnaround time: {avg_tat:.2f}")
        print(f"average waiting time: {avg_wt:.2f}")
        print(f"cpu utilization: {cpu_util:.1f}%")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("kullanım: python scheduler.py <girdi_dosyasi> [time_quantum]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    # time quantum girilmezse varsayılan 3 olsun dedim ve rr_tq=3
    rr_tq = 3
    if len(sys.argv) >= 3:
        try:
            rr_tq = int(sys.argv[2])
        except ValueError:
            print("uyarı: time quantum hatalı, varsayılan (3) kullanıyorum.")

    procs = parse_input_file(input_file)
    run_all(procs, rr_tq)
