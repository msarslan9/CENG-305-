# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: main.py
# Date: 12-12-2025
# --------------------------------------------

"""
Ana giriş noktası - GUI uygulamasını başlatır
"""

import sys

try:
    import tkinter as tk
except ImportError:
    print("\nKRITIK HATA: 'tkinter' kütüphanesi bulunamadı hocam.")
    input("Kapatmak için Enter'a basın...")
    sys.exit(1)

from gui import SchedulerApp


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()

