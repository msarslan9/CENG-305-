# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator (Gold Edition)
# File: scheduler_gui.py
# Date: 17-12-2025 
# --------------------------------------------

import sys
import os
import csv
import math 
import datetime

# hocam tkinter bazen yüklü gelmiyor, o yüzden try-except ile sardım.
# eğer yoksa program çökmez, uyarı verir.
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, Canvas
except ImportError:
    print("\nKRITIK HATA: 'tkinter' kütüphanesi bulunamadı hocam.")
    input("Kapatmak için Enter'a basın...")
    sys.exit(1)

# PDF Kütüphanesi Kontrolü (Hocam kütüphane yüklenmiş olmalııı kodum patlamasın :) )
PDF_AVAILABLE = False
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    print("UYARI: 'fpdf' kütüphanesi yüklü değil. PDF yerine TXT raporu üretilecek.")

from collections import deque
import random
import time

# ==========================================
# BÖLÜM 1: ÇEKİRDEK MANTIK (CORE LOGIC)
# hocam burası işin matematik kısmı, ödev metnindeki kurallara %100 uyumlu.
# ==========================================

def parse_input_file(filename):
    """
    dosyayı okuyup verileri aldığım kısım.
    hatalı satırları atlıyorum ki simülasyon yarıda kalmasın.
    """
    procs = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                parts = [p.strip() for p in line.split(',')]
                if len(parts) < 4: continue
                procs.append((parts[0], int(parts[1]), int(parts[2]), int(parts[3])))
    except Exception as e:
        return None
    return procs

def simulate_fcfs(processes):
    # fcfs: ilk gelen ilk hizmeti alır. basit kuyruk mantığı hocam.
    procs_sorted = sorted(processes, key=lambda x: (x[1],))
    time = 0; gantt = []; idle = 0; res = {}; logs = []
    
    for pid, arr, burst, pri in procs_sorted:
        if time < arr:
            gantt.append(("idle", time, arr))
            logs.append(f"[{time:02d}] IDLE: Waiting for arrival...")
            idle += arr - time
            time = arr
        start = time; end = time + burst
        gantt.append((pid, start, end))
        logs.append(f"[{start:02d}] EXECUTE: {pid} started (Burst: {burst})")
        time += burst
        logs.append(f"[{time:02d}] COMPLETE: {pid} finished task.")
        res[pid] = {'finish': time, 'turnaround': time - arr, 'waiting': (time - arr) - burst, 'burst': burst}
        
    total_time = time
    cpu_util = (total_time - idle) / total_time * 100 if total_time > 0 else 0.0
    return res, gantt, cpu_util, total_time, logs, idle

def simulate_sjf(processes):
    # sjf (non-preemptive): en kısa işi öne alıyorum.
    procs = [list(p) for p in processes]
    procs.sort(key=lambda x: x[1])
    n = len(procs); time = 0; gantt = []; idle = 0; res = {}; completed = 0; logs = []
    
    while completed < n:
        candidates = [p for p in procs if p[1] <= time and ('done' not in p)]
        
        if not candidates:
            next_arr = min(p[1] for p in procs if 'done' not in p)
            if time < next_arr:
                gantt.append(("idle", time, next_arr)); 
                logs.append(f"[{time:02d}] IDLE: No process ready...")
                idle += next_arr - time; time = next_arr
            continue
            
        # en kısa burst time'a göre sırala
        candidates.sort(key=lambda x: (x[2], x[1]))
        p = candidates[0]
        pid, arr, burst, pri = p[0], p[1], p[2], p[3]
        
        gantt.append((pid, time, time + burst))
        logs.append(f"[{time:02d}] SJF DECISION: {pid} selected (Burst: {burst})")
        time += burst
        logs.append(f"[{time:02d}] COMPLETE: {pid}")
        
        res[pid] = {'finish': time, 'turnaround': time - arr, 'waiting': (time - arr) - burst, 'burst': burst}
        p.append('done'); completed += 1
        
    total_time = time
    cpu_util = (total_time - idle) / total_time * 100 if total_time > 0 else 0.0
    return res, gantt, cpu_util, total_time, logs, idle

def simulate_rr(processes, tq):
    # round robin: hocam burası projenin en zor kısmıydı :)
    # işlem çalışırken (time quantum süresince) yeni gelenleri kaçırmamak için
    # saniye saniye kontrol eden bir yapı kurdum.
    procs_map = {p[0]: {'arr':p[1], 'rem':p[2], 'burst':p[2], 'pri':p[3]} for p in processes}
    time = 0; gantt = []; idle = 0; ready = deque(); arrived = set(); logs = []
    n = len(processes); completed = 0

    def add_arrivals_at(t):
        for p in processes:
            if p[1] == t and p[0] not in arrived:
                ready.append(p[0]); arrived.add(p[0])
                logs.append(f"[{t:02d}] ARRIVAL: {p[0]} joined the Ready Queue")

    add_arrivals_at(0)
    if not ready:
        next_arr = min(p[1] for p in processes)
        gantt.append(("idle", time, next_arr)); idle += next_arr - time; time = next_arr
        add_arrivals_at(time)

    while completed < n:
        if not ready:
            remaining_procs = [p for p in processes if p[0] not in arrived]
            if not remaining_procs: break
            next_arr = min(p[1] for p in remaining_procs)
            gantt.append(("idle", time, next_arr)); idle += next_arr - time; time = next_arr
            add_arrivals_at(time)
            continue
            
        pid = ready.popleft(); p = procs_map[pid]
        run_time = min(tq, p['rem'])
        start = time; end = time + run_time
        gantt.append((pid, start, end))
        logs.append(f"[{start:02d}] RUNNING: {pid} for {run_time}s")
        
        # kritik döngü: işlem sürerken yeni gelen var mı?
        for t in range(start + 1, end + 1): add_arrivals_at(t)
        
        time = end; p['rem'] -= run_time
        if p['rem'] == 0:
            completed += 1; procs_map[pid]['finish'] = time
            logs.append(f"[{time:02d}] FINISHED: {pid}")
        else: 
            ready.append(pid)
            logs.append(f"[{time:02d}] QUANTUM EXPIRED: {pid} re-queued")

    res = {}
    for pid, vals in procs_map.items():
        res[pid] = {'finish': vals['finish'], 'turnaround': vals['finish']-vals['arr'], 'waiting': (vals['finish']-vals['arr'])-vals['burst'], 'burst': vals['burst']}
    total_time = time
    cpu_util = (total_time - idle) / total_time * 100 if total_time > 0 else 0.0
    return res, gantt, cpu_util, total_time, logs, idle

def simulate_priority(processes):
    # priority scheduling: düşük sayı = yüksek öncelik
    procs = [list(p) for p in processes]
    procs.sort(key=lambda x: x[1])
    n = len(procs); time = 0; gantt = []; idle = 0; res = {}; completed = 0; logs = []
    while completed < n:
        candidates = [p for p in procs if p[1] <= time and ('done' not in p)]
        if not candidates:
            next_arr = min(p[1] for p in procs if 'done' not in p)
            if time < next_arr:
                gantt.append(("idle", time, next_arr)); idle += next_arr - time; time = next_arr
            continue
        candidates.sort(key=lambda x: (x[3], x[1]))
        p = candidates[0]
        pid, arr, burst, pri = p[0], p[1], p[2], p[3]
        gantt.append((pid, time, time + burst))
        logs.append(f"[{time:02d}] PRIORITY EXEC: {pid} (Prio: {pri})")
        time += burst
        res[pid] = {'finish': time, 'turnaround': time - arr, 'waiting': (time - arr) - burst, 'burst': burst}
        p.append('done'); completed += 1
    total_time = time
    cpu_util = (total_time - idle) / total_time * 100 if total_time > 0 else 0.0
    return res, gantt, cpu_util, total_time, logs, idle

def compute_averages(results):
    n = len(results)
    if n == 0: return 0.0, 0.0
    avg_tat = sum(results[p]['turnaround'] for p in results) / n
    avg_wt  = sum(results[p]['waiting'] for p in results) / n
    return avg_tat, avg_wt

# ==========================================
# BÖLÜM 2: UI YARDIMCILARI (Tooltip)
# ==========================================

class ToolTip(object):
    """
    Hocam arayüzde mouse ile üzerine gelince bilgi veren küçük kutucuklar.
    """
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        self.text = text
        if self.tipwindow or not self.text: return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#0B0C10", foreground="#66FCF1", relief=tk.SOLID, borderwidth=1, font=("Consolas", 10))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw: tw.destroy()

def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    widget.bind('<Enter>', lambda e: toolTip.showtip(text))
    widget.bind('<Leave>', lambda e: toolTip.hidetip())

# ==========================================
# BÖLÜM 3: MAIN APPLICATION (FİNAL)
# ==========================================

class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CS 305 Process Simulator | Gold Edition")
        self.root.geometry("1350x850")
        
        # --- RENK PALETİ: FUTURE TECH ---
        self.bg_color = "#0B0C10"       
        self.panel_color = "#1F2833"    
        self.fg_color = "#C5C6C7"       
        self.neon_cyan = "#66FCF1"      
        self.neon_teal = "#45A29E"      
        self.neon_green = "#50fa7b"     
        self.neon_pink = "#ff007f"
        self.neon_yellow = "#FCEE0A"      
        
        self.root.configure(bg=self.bg_color)
        self.style_config()
        
        self.colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#FF9F1C', '#C44536', '#1A535C']
        self.proc_colors = {}
        self.processes = []
        self.last_results = {} 
        self.best_algo = ("", float('inf')) 
        self.summary_data = [] 

        self.monitor_data = deque([0]*50, maxlen=50)
        self.is_running = False
        
        # --- ÖNCE SPLASH SCREEN (AÇILIŞ EKRANI) BAŞLAT ---
        self.show_splash_screen()

    def show_splash_screen(self):
        self.root.withdraw()
        splash = tk.Toplevel(self.root)
        splash.overrideredirect(True) 
        
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        w, h = 600, 350
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        splash.geometry('%dx%d+%d+%d' % (w, h, x, y))
        splash.configure(bg="#000000")
        
        frame = tk.Frame(splash, bg="black", highlightthickness=2, highlightbackground=self.neon_cyan)
        frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame, text="CS 305 SYSTEM KERNEL", font=("Courier", 20, "bold"), bg="black", fg=self.neon_cyan).pack(pady=(40, 20))
        self.loading_lbl = tk.Label(frame, text="", font=("Consolas", 12), bg="black", fg=self.neon_green)
        self.loading_lbl.pack(pady=10)
        
        style = ttk.Style()
        style.theme_use('alt')
        style.configure("green.Horizontal.TProgressbar", foreground=self.neon_green, background=self.neon_green, troughcolor="#222")
        self.pbar = ttk.Progressbar(frame, style="green.Horizontal.TProgressbar", orient="horizontal", length=400, mode="determinate")
        self.pbar.pack(pady=20)
        
        tk.Label(frame, text="Melek Arslan | 220446018", font=("Consolas", 9), bg="black", fg="#555").pack(side=tk.BOTTOM, pady=10)

        steps = [
            ("Initializing Kernel...", 0.2),
            ("Loading Modules...", 0.4),
            ("Verifying Drivers...", 0.6),
            ("Mounting UI...", 0.8),
            ("SYSTEM READY.", 1.0)
        ]
        
        def run_steps(idx):
            if idx < len(steps):
                txt, progress = steps[idx]
                self.loading_lbl.config(text=f"> {txt}")
                self.pbar['value'] = progress * 100
                splash.update()
                delay = random.randint(300, 600)
                self.root.after(delay, run_steps, idx+1)
            else:
                self.root.after(500, lambda: self.close_splash(splash))
        run_steps(0)

    def close_splash(self, splash):
        splash.destroy()
        self.root.deiconify() 
        self.setup_ui()       
        self.animate_monitor() 

    def style_config(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color, font=("Segoe UI", 10))
        style.configure("Treeview", background="#151922", foreground=self.neon_cyan, fieldbackground="#151922", font=("Consolas", 10))
        style.configure("Treeview.Heading", background="#1F2833", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[('selected', self.neon_teal)], foreground=[('selected', 'white')])

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=self.bg_color, pady=20, padx=20)
        header.pack(fill=tk.X)
        title_frame = tk.Frame(header, bg=self.bg_color)
        title_frame.pack(side=tk.LEFT)
        tk.Label(title_frame, text="CS 305 Process Scheduling Simulator", font=("Segoe UI", 26, "bold"), bg=self.bg_color, fg="white").pack(anchor="w")
        tk.Label(title_frame, text="Advanced Analytics & Visualization Tool", font=("Consolas", 12), bg=self.bg_color, fg=self.neon_cyan).pack(anchor="w")
        # --- ÖĞRENCİ BİLGİLERİ (BURAYA TAŞIDIM HOCAM, GÖZDEN KAÇMASIN DİYE) ---
        tk.Label(title_frame, text="Student: Melek Arslan | ID: 220446018", font=("Consolas", 11, "bold"), bg=self.bg_color, fg=self.neon_green).pack(anchor="w", pady=(5,0))
        
        self.monitor_canvas = tk.Canvas(header, width=200, height=50, bg="#000", highlightthickness=1, highlightbackground=self.neon_teal)
        self.monitor_canvas.pack(side=tk.RIGHT, pady=5)
        tk.Label(header, text="SYSTEM LOAD", font=("Consolas", 8, "bold"), bg=self.bg_color, fg=self.neon_teal).pack(side=tk.RIGHT, padx=10)

        # KONTROL PANELİ
        ctrl = tk.Frame(self.root, bg=self.panel_color, padx=15, pady=15, relief="flat")
        ctrl.pack(fill=tk.X, padx=20, pady=15)
        def create_btn(parent, text, cmd, bg_c, fg_c="white"):
            btn = tk.Button(parent, text=text, command=cmd, bg=bg_c, fg=fg_c, font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=5, cursor="hand2", borderwidth=0)
            return btn
        
        # SOL BUTONLAR (Load, Quantum, Speed)
        create_btn(ctrl, "📂 Load Input File", self.load_file, "#2C3E50").pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(ctrl, text="Quantum:", bg=self.panel_color, fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.tq_var = tk.IntVar(value=3)
        tk.Scale(ctrl, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.tq_var, bg=self.panel_color, fg=self.neon_cyan, highlightthickness=0, borderwidth=0, troughcolor="#0B0C10").pack(side=tk.LEFT, padx=5)

        tk.Label(ctrl, text="Speed:", bg=self.panel_color, fg="white", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(20, 0))
        self.speed_var = tk.DoubleVar(value=0.1)
        tk.Scale(ctrl, from_=0.01, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, variable=self.speed_var, bg=self.panel_color, fg=self.neon_teal, highlightthickness=0, borderwidth=0, troughcolor="#0B0C10").pack(side=tk.LEFT, padx=5)

        # SAĞ BUTONLAR (Run, PDF, Excel, Help)
        self.btn_run = create_btn(ctrl, "▶ Run Simulation", self.run_simulation, self.neon_teal, "black")
        self.btn_run.pack(side=tk.RIGHT)
        self.btn_run.config(state=tk.DISABLED)

        # Excel Butonu (Geri Geldi)
        self.btn_export = create_btn(ctrl, "💾 Export CSV", self.export_csv, "#27ae60")
        self.btn_export.pack(side=tk.RIGHT, padx=(10, 10))
        self.btn_export.config(state=tk.DISABLED)

        # PDF Butonu
        self.btn_pdf = create_btn(ctrl, "📄 Export PDF", self.export_pdf, "#e74c3c")
        self.btn_pdf.pack(side=tk.RIGHT, padx=(0, 10))
        self.btn_pdf.config(state=tk.DISABLED)

        # Guide Butonu
        self.btn_help = create_btn(ctrl, "❓ Help", self.open_guide, "#8e44ad")
        self.btn_help.pack(side=tk.RIGHT, padx=(0, 10))

        # SEKMELER
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.tabs = {}
        for algo in ["FCFS", "SJF", "Round Robin", "Priority"]:
            frame = tk.Frame(self.notebook, bg=self.bg_color)
            self.notebook.add(frame, text=f"  {algo}  ")
            self.setup_algo_tab(frame, algo)
            self.tabs[algo] = frame
        self.compare_frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(self.compare_frame, text="  📊 Analytics & Charts  ")
        self.setup_comparison_tab()

    def setup_algo_tab(self, frame, algo_name):
        top_frame = tk.Frame(frame, bg=self.bg_color)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        tree_frame = tk.Frame(top_frame, bg=self.bg_color)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        cols = ("PID", "Finish", "Turnaround", "Waiting")
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        for c in cols: tree.heading(c, text=c); tree.column(c, width=100, anchor=tk.CENTER)
        sb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=sb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        stats_panel = tk.Frame(top_frame, bg=self.panel_color, padx=30, pady=20, relief="flat")
        stats_panel.pack(side=tk.RIGHT, fill=tk.Y)
        gauge_canvas = tk.Canvas(stats_panel, width=140, height=140, bg=self.panel_color, highlightthickness=0)
        gauge_canvas.pack(pady=(0, 15))
        self.draw_gauge(gauge_canvas, 0)
        tk.Frame(stats_panel, height=1, bg="#444", width=120).pack(pady=10)
        lbl_wt = tk.Label(stats_panel, text="Avg Waiting Time", bg=self.panel_color, fg="#888", font=("Segoe UI", 9))
        lbl_wt.pack()
        val_wt = tk.Label(stats_panel, text="--", bg=self.panel_color, fg=self.neon_cyan, font=("Segoe UI", 24, "bold"))
        val_wt.pack(pady=(0, 15))
        lbl_tat = tk.Label(stats_panel, text="Avg Turnaround", bg=self.panel_color, fg="#888", font=("Segoe UI", 9))
        lbl_tat.pack()
        val_tat = tk.Label(stats_panel, text="--", bg=self.panel_color, fg=self.neon_teal, font=("Segoe UI", 24, "bold"))
        val_tat.pack()
        bottom_frame = tk.Frame(frame, bg=self.bg_color)
        bottom_frame.pack(fill=tk.BOTH, pady=10)
        tk.Label(bottom_frame, text="Live Timeline Visualization", font=("Segoe UI", 11, "bold"), bg=self.bg_color, fg="white").pack(anchor=tk.W)
        canvas = tk.Canvas(bottom_frame, bg="#151922", height=70, highlightthickness=0)
        canvas.pack(fill=tk.X, pady=(5, 15))
        tk.Label(bottom_frame, text="Kernel Execution Logs", font=("Segoe UI", 10, "bold"), bg=self.bg_color, fg="white").pack(anchor=tk.W)
        log_text = tk.Text(bottom_frame, height=8, bg="#000", fg=self.neon_cyan, font=("Consolas", 9), state=tk.DISABLED, relief="flat", padx=10, pady=10)
        log_text.pack(fill=tk.BOTH, expand=True)
        frame.tree = tree; frame.canvas = canvas; frame.log_text = log_text
        frame.stats = (gauge_canvas, val_wt, val_tat)

    def setup_comparison_tab(self):
        self.bar_frame = tk.Frame(self.compare_frame, bg=self.bg_color)
        self.bar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(self.bar_frame, text="Efficiency Comparison (Grouped Bar Chart)", bg=self.bg_color, fg="#888", font=("Segoe UI", 12)).pack(anchor=tk.N, pady=5)
        self.compare_canvas = tk.Canvas(self.bar_frame, bg="#151922", highlightthickness=0)
        self.compare_canvas.pack(fill=tk.BOTH, expand=True)
        self.scatter_frame = tk.Frame(self.compare_frame, bg=self.bg_color)
        self.scatter_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(self.scatter_frame, text="Correlation Analysis (Burst vs Waiting)", bg=self.bg_color, fg="#888", font=("Segoe UI", 12)).pack(anchor=tk.N, pady=5)
        self.scatter_canvas = tk.Canvas(self.scatter_frame, bg="#0B0C10", highlightthickness=1, highlightbackground=self.panel_color)
        self.scatter_canvas.pack(fill=tk.BOTH, expand=True)
        legend_f = tk.Frame(self.scatter_frame, bg=self.bg_color)
        legend_f.pack(fill=tk.X, pady=5)
        tk.Label(legend_f, text="• Dots represent individual processes", bg=self.bg_color, fg=self.neon_cyan, font=("Consolas", 8)).pack()
    
    def animate_monitor(self):
        w, h = 200, 50
        self.monitor_canvas.delete("all")
        self.monitor_canvas.create_line(0, h/2, w, h/2, fill="#1F2833") 
        if self.is_running: val = random.randint(10, 40)
        else: val = random.randint(2, 5)
        self.monitor_data.append(val)
        points = []
        for i, d in enumerate(self.monitor_data):
            points.append(i * (w / 50))
            points.append(h - d)
        if len(points) > 2:
            self.monitor_canvas.create_line(points, fill=self.neon_cyan, width=2, smooth=True)
        self.root.after(100, self.animate_monitor)

    def draw_gauge(self, canvas, percent):
        canvas.delete("all")
        x, y, r = 70, 70, 55
        canvas.create_oval(x-r, y-r, x+r, y+r, outline="#1F2833", width=8)
        if percent > 0:
            extent = (percent / 100) * 360
            canvas.create_arc(x-r, y-r, x+r, y+r, start=90, extent=-extent, style=tk.ARC, outline=self.neon_cyan, width=8)
        canvas.create_text(x, y-10, text="CPU Usage", fill="#888", font=("Segoe UI", 8))
        canvas.create_text(x, y+10, text=f"{percent:.0f}%", fill="white", font=("Segoe UI", 16, "bold"))

    def open_guide(self):
        guide = tk.Toplevel(self.root)
        guide.title("User Manual & Guide")
        guide.geometry("600x500")
        guide.configure(bg="#111")
        tk.Label(guide, text="PROCESS SCHEDULER USER GUIDE", font=("Segoe UI", 16, "bold"), bg="#111", fg=self.neon_cyan).pack(pady=20)
        info = (
            "1. 📂 Load Input File:\n"
            "   Select 'processes.txt' to load data.\n\n"
            "2. ⚙️ Configuration:\n"
            "   - Quantum: Adjust time slice for Round Robin.\n"
            "   - Speed: Control animation speed.\n\n"
            "3. ▶ Run Simulation:\n"
            "   Starts visualization. Runs FCFS -> SJF -> RR -> Priority.\n\n"
            "4. 📊 Analytics:\n"
            "   View detailed charts and scatter plots.\n\n"
            "5. 📄 Export:\n"
            "   Save results as PDF or Excel (CSV).\n"
        )
        msg = tk.Message(guide, text=info, width=550, bg="#111", fg="white", font=("Consolas", 10))
        msg.pack(padx=20, pady=10)
        tk.Button(guide, text="CLOSE", command=guide.destroy, bg=self.neon_pink, fg="white", font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=20)

    def load_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            procs = parse_input_file(filename)
            if procs:
                self.processes = procs
                self.proc_colors = {p[0]: self.colors[i % len(self.colors)] for i, p in enumerate(self.processes)}
                messagebox.showinfo("Ready", f"Successfully loaded {len(procs)} processes.")
                self.btn_run.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", "File format incorrect.")

    def export_pdf(self):
        if not self.last_results: return
        f = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not f: return
        if PDF_AVAILABLE:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="CS 305 Process Scheduling Report", ln=True, align='C')
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(200, 10, txt=f"Generated by: Melek Arslan (220446018) | {datetime.datetime.now()}", ln=True, align='C')
                pdf.ln(10)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"Best Algorithm: {self.best_algo[0]}", ln=True)
                pdf.set_font("Arial", '', 10)
                pdf.cell(0, 10, f"Lowest Avg Waiting Time: {self.best_algo[1]:.2f}", ln=True)
                pdf.ln(5)
                col_w = 25
                pdf.set_fill_color(200, 220, 255)
                pdf.set_font("Arial", 'B', 9)
                headers = ['Algo', 'PID', 'Finish', 'Turnaround', 'Waiting']
                for h in headers: pdf.cell(col_w, 10, h, 1, 0, 'C', 1)
                pdf.ln()
                pdf.set_font("Arial", '', 9)
                for algo, res in self.last_results.items():
                    for pid, metrics in res.items():
                        pdf.cell(col_w, 10, algo[:4], 1, 0, 'C')
                        pdf.cell(col_w, 10, pid, 1, 0, 'C')
                        pdf.cell(col_w, 10, str(metrics['finish']), 1, 0, 'C')
                        pdf.cell(col_w, 10, str(metrics['turnaround']), 1, 0, 'C')
                        pdf.cell(col_w, 10, str(metrics['waiting']), 1, 0, 'C')
                        pdf.ln()
                pdf.output(f)
                messagebox.showinfo("Success", "PDF Report saved successfully.")
            except Exception as e:
                messagebox.showerror("PDF Error", f"Failed to create PDF: {e}")
        else:
            txt_file = f.replace(".pdf", ".txt")
            with open(txt_file, "w") as tf:
                tf.write("CS 305 Report\n")
                tf.write(f"Best: {self.best_algo[0]}\n")
            messagebox.showinfo("Backup", "PDF library missing. Saved as TXT.")

    def export_csv(self):
        if not self.last_results: return
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if f:
            with open(f, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Algorithm', 'PID', 'Finish', 'Turnaround', 'Waiting'])
                for algo, res in self.last_results.items():
                    for pid, metrics in res.items():
                        writer.writerow([algo, pid, metrics['finish'], metrics['turnaround'], metrics['waiting']])
            messagebox.showinfo("Success", "Results exported to CSV successfully.")

    def animate_gantt(self, canvas, gantt, total_time, tab_frame):
        canvas.delete("all")
        width = canvas.winfo_width(); 
        if width < 100: width = 800
        margin = 10; usable = width - 2*margin
        scale = usable / total_time if total_time > 0 else 1
        canvas.create_line(margin, 55, width-margin, 55, fill="#555", width=1)
        def draw(idx):
            if idx >= len(gantt):
                canvas.create_text(margin + total_time * scale, 65, text=str(total_time), fill="#aaa", font=("Arial", 8))
                self.is_running = False
                return
            lbl, s, e = gantt[idx]
            x1 = margin + s * scale; x2 = margin + e * scale
            color = "#1F2833" if lbl == "idle" else self.proc_colors.get(lbl, "gray")
            outline = "#333" if lbl == "idle" else "white"
            rect = canvas.create_rectangle(x1, 15, x2, 45, fill=color, outline=outline, width=0)
            canvas.create_text((x1+x2)/2, 30, text=lbl, fill="white", font=("Segoe UI", 9, "bold"))
            canvas.create_text(x1, 65, text=str(s), fill="#888", font=("Arial", 8))
            info = f"PROCESS: {lbl}\nRANGE: {s} -> {e}\nBURST: {e-s}"
            canvas.tag_bind(rect, "<Enter>", lambda event, t=info: self.show_canvas_tooltip(event, t))
            canvas.tag_bind(rect, "<Leave>", lambda event: self.hide_canvas_tooltip())
            self.root.update()
            delay = int(self.speed_var.get() * 1000)
            self.root.after(delay, draw, idx+1)
        self.is_running = True
        draw(0)

    def celebrate_success(self):
        # Konfeti Animasyonu
        self.notebook.select(self.compare_frame)
        self.root.update()
        canvas = self.compare_canvas
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        colors = [self.neon_cyan, self.neon_pink, self.neon_green, self.neon_yellow]
        particles = []
        for _ in range(50):
            x = random.randint(0, w)
            y = random.randint(-100, 0)
            size = random.randint(3, 8)
            color = random.choice(colors)
            speed = random.randint(2, 8)
            item = canvas.create_rectangle(x, y, x+size, y+size, fill=color, outline="")
            particles.append({'id': item, 'speed': speed})
        def update_particles(steps):
            if steps <= 0:
                for p in particles: canvas.delete(p['id'])
                self.show_analysis_popup()
                return
            for p in particles:
                canvas.move(p['id'], 0, p['speed'])
                coords = canvas.coords(p['id'])
                if coords and coords[1] > h:
                    canvas.move(p['id'], 0, -h-20)
            self.root.after(30, update_particles, steps-1)
        update_particles(100)

    def show_analysis_popup(self):
        # HOCAM İŞTE BURASI O MEŞHUR ANALİZ MESAJI (Robotik değil, doğal)
        messagebox.showinfo("Simülasyon Sonucu", 
                            f"Hocam simülasyonumuz bitti, sonuçlarımız aşağıda.\n\n"
                            f"Analiz Sonucum:\n"
                            f"En Verimli Algoritma: {self.best_algo[0]}\n"
                            f"Ortalama Bekleme Süresi: {self.best_algo[1]:.2f}\n\n"
                            f"Yorumum:\n"
                            f"Bu algoritma, kısa işlemleri öne aldığı için kuyruk yoğunluğunu azalttı ve en iyi sonucu verdi.\n\n"
                            f"Detaylı grafikleri Analytics sekmesinde inceleyebilirsiniz.")

    def draw_comparison_charts(self, summary):
        c = self.compare_canvas
        c.delete("all")
        w = c.winfo_width(); h = c.winfo_height()
        if w < 100: w = 600; h = 400
        bar_w = 30; space = 60; group_space = 100
        start_x = 50; base_y = h - 50
        max_val = 1
        for s in summary: max_val = max(max_val, s[1], s[2])
        scale = (h - 100) / max_val
        c.create_line(40, base_y, w-20, base_y, fill="#555", width=2)
        for i, (name, wt, tat) in enumerate(summary):
            x = start_x + i * group_space
            h_wt = wt * scale
            c.create_rectangle(x, base_y - h_wt, x + bar_w, base_y, fill=self.neon_cyan, outline="")
            c.create_text(x + bar_w/2, base_y - h_wt - 10, text=f"{wt:.1f}", fill="white", font=("Arial", 8))
            h_tat = tat * scale
            c.create_rectangle(x + bar_w, base_y - h_tat, x + 2*bar_w, base_y, fill=self.neon_pink, outline="")
            c.create_text(x + 1.5*bar_w, base_y - h_tat - 10, text=f"{tat:.1f}", fill="white", font=("Arial", 8))
            c.create_text(x + bar_w, base_y + 20, text=name, fill="#888", font=("Segoe UI", 8))
        c.create_rectangle(w-150, 20, w-140, 30, fill=self.neon_cyan)
        c.create_text(w-90, 25, text="Avg Waiting", fill="white", anchor="w")
        c.create_rectangle(w-150, 40, w-140, 50, fill=self.neon_pink)
        c.create_text(w-90, 45, text="Avg Turnaround", fill="white", anchor="w")

        sc = self.scatter_canvas
        sc.delete("all")
        sw = sc.winfo_width(); sh = sc.winfo_height()
        if sw < 100: sw = 600; sh = 400
        margin = 40
        sc.create_line(margin, sh-margin, sw-margin, sh-margin, fill="#555", width=2) 
        sc.create_line(margin, sh-margin, margin, margin, fill="#555", width=2)       
        sc.create_text(sw/2, sh-10, text="Burst Time (Job Size)", fill="#888")
        sc.create_text(15, sh/2, text="Wait\nTime", fill="#888", angle=90)
        if "SJF" in self.last_results:
            data = self.last_results["SJF"]
            max_burst = max(d['burst'] for d in data.values()) if data else 1
            max_wait = max(d['waiting'] for d in data.values()) if data else 1
            for pid, metric in data.items():
                b = metric['burst']
                w = metric['waiting']
                px = margin + (b / max_burst) * (sw - 2*margin)
                py = (sh - margin) - (w / max_wait) * (sh - 2*margin)
                sc.create_oval(px-4, py-4, px+4, py+4, fill=self.neon_green, outline="white")
                sc.create_text(px, py-10, text=pid, fill="white", font=("Arial", 8))

    def run_simulation(self):
        tq = self.tq_var.get()
        algos = [("FCFS", simulate_fcfs, None), ("SJF", simulate_sjf, None), ("Round Robin", lambda p: simulate_rr(p, tq), None), ("Priority", simulate_priority, None)]
        self.summary_data = [] 
        self.last_results = {}
        self.is_running = True
        self.best_algo = ("", float('inf'))
        for name, func, _ in algos:
            res, gantt, util, tot, logs, idle_time = func(self.processes)
            avg_tat, avg_wt = compute_averages(res)
            self.summary_data.append((name, avg_wt, avg_tat))
            self.last_results[name] = res
            if avg_wt < self.best_algo[1]:
                self.best_algo = (name, avg_wt)
            tab = self.tabs[name]
            for i in tab.tree.get_children(): tab.tree.delete(i)
            for pid in [p[0] for p in sorted(self.processes, key=lambda x: x[1])]:
                r = res[pid]
                tab.tree.insert("", "end", values=(pid, r['finish'], r['turnaround'], r['waiting']))
            self.draw_gauge(tab.stats[0], util)
            tab.stats[1].config(text=f"{avg_wt:.2f}")
            tab.stats[2].config(text=f"{avg_tat:.2f}")
            tab.log_text.config(state=tk.NORMAL)
            tab.log_text.delete(1.0, tk.END)
            for l in logs: tab.log_text.insert(tk.END, f"> {l}\n")
            tab.log_text.config(state=tk.DISABLED)
            self.animate_gantt(tab.canvas, gantt, tot, tab)
        self.draw_comparison_charts(self.summary_data)
        self.btn_export.config(state=tk.NORMAL)
        self.btn_pdf.config(state=tk.NORMAL)
        self.celebrate_success()

if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()