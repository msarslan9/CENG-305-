# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: utils/formatters.py
# Date: 12-12-2025
# --------------------------------------------

"""
Formatlama ve çıktı fonksiyonları
"""


def format_gantt(gantt):
    """
    gantt şemasını string olarak birleştiriyorum çıktı güzel görünsün diye.
    örnek: [0]--P1--[5]--P2--[10]
    
    Args:
        gantt: Gantt chart listesi [(label, start, end), ...]
    
    Returns:
        str: Formatlanmış Gantt chart string'i
    """
    pieces = []
    for label, s, e in gantt:
        pieces.append(f"[{s}]--{label}--[{e}]")
    return ''.join(pieces)


def print_table(results, order):
    """
    hesapladığım metrikleri (finish, turnaround, waiting) tablo yapıp basıyorum.
    
    Args:
        results: Sonuç sözlüğü {pid: {'finish': ..., 'turnaround': ..., 'waiting': ...}}
        order: Process ID'lerin sırası
    """
    print(" Process   | Finish Time | Turnaround Time | Waiting Time")
    print(" -----------------------------------------------------")
    for pid in order:
        r = results[pid]
        # sayıları ortaladım ki tablo kaymasın
        print(f" {pid:<10}| {r['finish']:^11} | {r['turnaround']:^15} | {r['waiting']:^12}")

