# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: utils/calculations.py
# Date: 12-12-2025
# --------------------------------------------

"""
Hesaplama fonksiyonları
"""


def compute_averages(results):
    """
    ortalamaları burada alıyorum
    
    Args:
        results: Sonuç sözlüğü {pid: {'turnaround': ..., 'waiting': ...}}
    
    Returns:
        tuple: (avg_turnaround_time, avg_waiting_time)
    """
    n = len(results)
    if n == 0: 
        return 0.0, 0.0
    avg_tat = sum(results[p]['turnaround'] for p in results) / n
    avg_wt  = sum(results[p]['waiting'] for p in results) / n
    return avg_tat, avg_wt

