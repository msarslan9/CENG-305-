# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: algorithms/__init__.py
# Date: 12-12-2025
# --------------------------------------------

"""
Scheduling algoritmaları modülü
"""

from .fcfs import simulate_fcfs
from .sjf import simulate_sjf
from .round_robin import simulate_rr
from .priority import simulate_priority

__all__ = ['simulate_fcfs', 'simulate_sjf', 'simulate_rr', 'simulate_priority']

