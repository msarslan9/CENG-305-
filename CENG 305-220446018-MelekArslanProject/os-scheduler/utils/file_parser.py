# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: utils/file_parser.py
# Date: 12-12-2025
# --------------------------------------------

"""
Dosya okuma ve parse işlemleri
"""

import sys


def parse_input_file(filename):
    """
    hocam burada input dosyasını okuyup satır satır ayırıyorum.
    formatımız: process_id, arrival_time, burst_time, priority
    
    Args:
        filename: Okunacak dosya yolu
    
    Returns:
        list: Process listesi [(pid, arrival, burst, priority), ...]
    """
    procs = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # boş satırsa ya da '#' ile başlayan yorum satırıysa atlıyorum
                if not line or line.startswith('#'):
                    continue
                parts = [p.strip() for p in line.split(',')]
                # eğer satırda eksik bilgi varsa okumuyorum hata vermesin diye
                if len(parts) < 4:
                    continue  
                pid = parts[0]
                arrival = int(parts[1])
                burst = int(parts[2])
                priority = int(parts[3])
                procs.append((pid, arrival, burst, priority))
    except FileNotFoundError:
        print(f"hata: '{filename}' dosyayı bulamadım hocam.")
        sys.exit(1)
    except ValueError as e:
        print(f"dosya formatında sıkıntı var: {e}")
        sys.exit(1)
    return procs

