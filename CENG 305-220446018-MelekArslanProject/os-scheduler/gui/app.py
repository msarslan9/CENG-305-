# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator (Gold Edition)
# File: gui/app.py
# Date: 17-12-2025 
# --------------------------------------------

import sys
import csv
import datetime
from collections import deque
import random

# tkinter import kontrolü
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except ImportError:
    print("\nKRITIK HATA: 'tkinter' kütüphanesi bulunamadı hocam.")
    input("Kapatmak için Enter'a basın...")
    sys.exit(1)

# PDF kütüphanesi kontrolü
PDF_AVAILABLE = False
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    print("UYARI: 'fpdf' kütüphanesi yüklü değil. PDF yerine TXT raporu üretilecek.")

# Modüler importlar
from algorithms import simulate_fcfs, simulate_sjf, simulate_rr, simulate_priority
from utils import parse_input_file, compute_averages
from .components import CreateToolTip
from .visualizations import Visualizations


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
        
        # Görselleştirme sınıfı
        self.viz = Visualizations(self.root, self.proc_colors)
        
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
        tk.Label(frame, text="CS 305 SYSTEM KERNEL", font=("Courier", 20, "bold"), 
                bg="black", fg=self.neon_cyan).pack(pady=(40, 20))
        self.loading_lbl = tk.Label(frame, text="", font=("Consolas", 12), bg="black", fg=self.neon_green)
        self.loading_lbl.pack(pady=10)
        
        style = ttk.Style()
        style.theme_use('alt')
        style.configure("green.Horizontal.TProgressbar", foreground=self.neon_green, 
                       background=self.neon_green, troughcolor="#222")
        self.pbar = ttk.Progressbar(frame, style="green.Horizontal.TProgressbar", 
                                   orient="horizontal", length=400, mode="determinate")
        self.pbar.pack(pady=20)
        
        tk.Label(frame, text="Melek Arslan | 220446018", font=("Consolas", 9), 
                bg="black", fg="#555").pack(side=tk.BOTTOM, pady=10)

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
        style.configure("TLabel", background=self.bg_color, foreground=self.fg_color, 
                       font=("Segoe UI", 10))
        style.configure("Treeview", background="#151922", foreground=self.neon_cyan, 
                      fieldbackground="#151922", font=("Consolas", 10))
        style.configure("Treeview.Heading", background="#1F2833", foreground="white", 
                       font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[('selected', self.neon_teal)], 
                 foreground=[('selected', 'white')])

    def setup_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=self.bg_color, pady=20, padx=20)
        header.pack(fill=tk.X)
        title_frame = tk.Frame(header, bg=self.bg_color)
        title_frame.pack(side=tk.LEFT)
        tk.Label(title_frame, text="CS 305 Process Scheduling Simulator", 
                font=("Segoe UI", 26, "bold"), bg=self.bg_color, fg="white").pack(anchor="w")
        tk.Label(title_frame, text="Advanced Analytics & Visualization Tool", 
                font=("Consolas", 12), bg=self.bg_color, fg=self.neon_cyan).pack(anchor="w")
        tk.Label(title_frame, text="Student: Melek Arslan | ID: 220446018", 
                font=("Consolas", 11, "bold"), bg=self.bg_color, fg=self.neon_green).pack(anchor="w", pady=(5,0))
        
        self.monitor_canvas = tk.Canvas(header, width=200, height=50, bg="#000", 
                                       highlightthickness=1, highlightbackground=self.neon_teal)
        self.monitor_canvas.pack(side=tk.RIGHT, pady=5)
        tk.Label(header, text="SYSTEM LOAD", font=("Consolas", 8, "bold"), 
                bg=self.bg_color, fg=self.neon_teal).pack(side=tk.RIGHT, padx=10)

        # KONTROL PANELİ
        ctrl = tk.Frame(self.root, bg=self.panel_color, padx=15, pady=15, relief="flat")
        ctrl.pack(fill=tk.X, padx=20, pady=15)
        
        def create_btn(parent, text, cmd, bg_c, fg_c="white"):
            btn = tk.Button(parent, text=text, command=cmd, bg=bg_c, fg=fg_c, 
                           font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=5, 
                           cursor="hand2", borderwidth=0)
            return btn
        
        # SOL BUTONLAR (Load, Quantum, Speed)
        create_btn(ctrl, "📂 Load Input File", self.load_file, "#2C3E50").pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(ctrl, text="Quantum:", bg=self.panel_color, fg="white", 
                font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.tq_var = tk.IntVar(value=3)
        tk.Scale(ctrl, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.tq_var, 
                bg=self.panel_color, fg=self.neon_cyan, highlightthickness=0, 
                borderwidth=0, troughcolor="#0B0C10").pack(side=tk.LEFT, padx=5)

        tk.Label(ctrl, text="Speed:", bg=self.panel_color, fg="white", 
                font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(20, 0))
        self.speed_var = tk.DoubleVar(value=0.1)
        tk.Scale(ctrl, from_=0.01, to=0.5, resolution=0.01, orient=tk.HORIZONTAL, 
                variable=self.speed_var, bg=self.panel_color, fg=self.neon_teal, 
                highlightthickness=0, borderwidth=0, troughcolor="#0B0C10").pack(side=tk.LEFT, padx=5)

        # SAĞ BUTONLAR (Run, PDF, Excel, Help)
        self.btn_run = create_btn(ctrl, "▶ Run Simulation", self.run_simulation, self.neon_teal, "black")
        self.btn_run.pack(side=tk.RIGHT)
        self.btn_run.config(state=tk.DISABLED)

        self.btn_export = create_btn(ctrl, "💾 Export CSV", self.export_csv, "#27ae60")
        self.btn_export.pack(side=tk.RIGHT, padx=(10, 10))
        self.btn_export.config(state=tk.DISABLED)

        self.btn_pdf = create_btn(ctrl, "📄 Export PDF", self.export_pdf, "#e74c3c")
        self.btn_pdf.pack(side=tk.RIGHT, padx=(0, 10))
        self.btn_pdf.config(state=tk.DISABLED)

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
        for c in cols: 
            tree.heading(c, text=c)
            tree.column(c, width=100, anchor=tk.CENTER)
        sb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=sb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        stats_panel = tk.Frame(top_frame, bg=self.panel_color, padx=30, pady=20, relief="flat")
        stats_panel.pack(side=tk.RIGHT, fill=tk.Y)
        gauge_canvas = tk.Canvas(stats_panel, width=140, height=140, bg=self.panel_color, highlightthickness=0)
        gauge_canvas.pack(pady=(0, 15))
        self.viz.draw_gauge(gauge_canvas, 0)
        tk.Frame(stats_panel, height=1, bg="#444", width=120).pack(pady=10)
        lbl_wt = tk.Label(stats_panel, text="Avg Waiting Time", bg=self.panel_color, 
                         fg="#888", font=("Segoe UI", 9))
        lbl_wt.pack()
        val_wt = tk.Label(stats_panel, text="--", bg=self.panel_color, fg=self.neon_cyan, 
                         font=("Segoe UI", 24, "bold"))
        val_wt.pack(pady=(0, 15))
        lbl_tat = tk.Label(stats_panel, text="Avg Turnaround", bg=self.panel_color, 
                          fg="#888", font=("Segoe UI", 9))
        lbl_tat.pack()
        val_tat = tk.Label(stats_panel, text="--", bg=self.panel_color, fg=self.neon_teal, 
                          font=("Segoe UI", 24, "bold"))
        val_tat.pack()
        bottom_frame = tk.Frame(frame, bg=self.bg_color)
        bottom_frame.pack(fill=tk.BOTH, pady=10)
        tk.Label(bottom_frame, text="Live Timeline Visualization", 
                font=("Segoe UI", 11, "bold"), bg=self.bg_color, fg="white").pack(anchor=tk.W)
        canvas = tk.Canvas(bottom_frame, bg="#151922", height=70, highlightthickness=0)
        canvas.pack(fill=tk.X, pady=(5, 15))
        tk.Label(bottom_frame, text="Kernel Execution Logs", 
                font=("Segoe UI", 10, "bold"), bg=self.bg_color, fg="white").pack(anchor=tk.W)
        log_text = tk.Text(bottom_frame, height=8, bg="#000", fg=self.neon_cyan, 
                          font=("Consolas", 9), state=tk.DISABLED, relief="flat", padx=10, pady=10)
        log_text.pack(fill=tk.BOTH, expand=True)
        frame.tree = tree
        frame.canvas = canvas
        frame.log_text = log_text
        frame.stats = (gauge_canvas, val_wt, val_tat)

    def setup_comparison_tab(self):
        self.bar_frame = tk.Frame(self.compare_frame, bg=self.bg_color)
        self.bar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(self.bar_frame, text="Efficiency Comparison (Grouped Bar Chart)", 
                bg=self.bg_color, fg="#888", font=("Segoe UI", 12)).pack(anchor=tk.N, pady=5)
        self.compare_canvas = tk.Canvas(self.bar_frame, bg="#151922", highlightthickness=0)
        self.compare_canvas.pack(fill=tk.BOTH, expand=True)
        self.scatter_frame = tk.Frame(self.compare_frame, bg=self.bg_color)
        self.scatter_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tk.Label(self.scatter_frame, text="Correlation Analysis (Burst vs Waiting)", 
                bg=self.bg_color, fg="#888", font=("Segoe UI", 12)).pack(anchor=tk.N, pady=5)
        self.scatter_canvas = tk.Canvas(self.scatter_frame, bg="#0B0C10", highlightthickness=1, 
                                       highlightbackground=self.panel_color)
        self.scatter_canvas.pack(fill=tk.BOTH, expand=True)
        legend_f = tk.Frame(self.scatter_frame, bg=self.bg_color)
        legend_f.pack(fill=tk.X, pady=5)
        tk.Label(legend_f, text="• Dots represent individual processes", 
                bg=self.bg_color, fg=self.neon_cyan, font=("Consolas", 8)).pack()
    
    def animate_monitor(self):
        self.viz.animate_monitor(self.monitor_canvas, self.monitor_data, self.is_running)
        self.root.after(100, self.animate_monitor)

    def open_guide(self):
        guide = tk.Toplevel(self.root)
        guide.title("User Manual & Guide")
        guide.geometry("600x500")
        guide.configure(bg="#111")
        tk.Label(guide, text="PROCESS SCHEDULER USER GUIDE", 
                font=("Segoe UI", 16, "bold"), bg="#111", fg=self.neon_cyan).pack(pady=20)
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
        msg = tk.Message(guide, text=info, width=550, bg="#111", fg="white", 
                        font=("Consolas", 10))
        msg.pack(padx=20, pady=10)
        tk.Button(guide, text="CLOSE", command=guide.destroy, bg=self.neon_pink, 
                 fg="white", font=("Segoe UI", 10, "bold"), relief="flat").pack(pady=20)

    def load_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            procs = parse_input_file(filename)
            if procs:
                self.processes = procs
                self.proc_colors = {p[0]: self.colors[i % len(self.colors)] 
                                  for i, p in enumerate(self.processes)}
                messagebox.showinfo("Ready", f"Successfully loaded {len(procs)} processes.")
                self.btn_run.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", "File format incorrect.")

    def export_pdf(self):
        if not self.last_results: 
            return
        f = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                        filetypes=[("PDF Files", "*.pdf")])
        if not f: 
            return
        if PDF_AVAILABLE:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 16)
                pdf.cell(200, 10, txt="CS 305 Process Scheduling Report", ln=True, align='C')
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(200, 10, txt=f"Generated by: Melek Arslan (220446018) | {datetime.datetime.now()}", 
                        ln=True, align='C')
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
                for h in headers: 
                    pdf.cell(col_w, 10, h, 1, 0, 'C', 1)
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
        if not self.last_results: 
            return
        f = filedialog.asksaveasfilename(defaultextension=".csv", 
                                         filetypes=[("CSV Files", "*.csv")])
        if f:
            with open(f, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Algorithm', 'PID', 'Finish', 'Turnaround', 'Waiting'])
                for algo, res in self.last_results.items():
                    for pid, metrics in res.items():
                        writer.writerow([algo, pid, metrics['finish'], 
                                        metrics['turnaround'], metrics['waiting']])
            messagebox.showinfo("Success", "Results exported to CSV successfully.")

    def animate_gantt(self, canvas, gantt, total_time, tab_frame):
        """Gantt chart animasyonu"""
        def set_running(value):
            self.is_running = value
        self.viz.animate_gantt(canvas, gantt, total_time, self.speed_var, self.proc_colors, set_running)

    def celebrate_success(self):
        """Başarı animasyonu"""
        self.viz.celebrate_success(self.compare_canvas, self.root, self.notebook, self.compare_frame)
        self.show_analysis_popup()

    def show_analysis_popup(self):
        messagebox.showinfo("Simülasyon Sonucu", 
                            f"Hocam simülasyonumuz bitti, sonuçlarımız aşağıda.\n\n"
                            f"Analiz Sonucum:\n"
                            f"En Verimli Algoritma: {self.best_algo[0]}\n"
                            f"Ortalama Bekleme Süresi: {self.best_algo[1]:.2f}\n\n"
                            f"Yorumum:\n"
                            f"Bu algoritma, kısa işlemleri öne aldığı için kuyruk yoğunluğunu azalttı ve en iyi sonucu verdi.\n\n"
                            f"Detaylı grafikleri Analytics sekmesinde inceleyebilirsiniz.")

    def run_simulation(self):
        tq = self.tq_var.get()
        algos = [
            ("FCFS", simulate_fcfs, None), 
            ("SJF", simulate_sjf, None), 
            ("Round Robin", lambda p: simulate_rr(p, tq), None), 
            ("Priority", simulate_priority, None)
        ]
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
            for i in tab.tree.get_children(): 
                tab.tree.delete(i)
            for pid in [p[0] for p in sorted(self.processes, key=lambda x: x[1])]:
                r = res[pid]
                tab.tree.insert("", "end", values=(pid, r['finish'], r['turnaround'], r['waiting']))
            self.viz.draw_gauge(tab.stats[0], util)
            tab.stats[1].config(text=f"{avg_wt:.2f}")
            tab.stats[2].config(text=f"{avg_tat:.2f}")
            tab.log_text.config(state=tk.NORMAL)
            tab.log_text.delete(1.0, tk.END)
            for l in logs: 
                tab.log_text.insert(tk.END, f"> {l}\n")
            tab.log_text.config(state=tk.DISABLED)
            self.animate_gantt(tab.canvas, gantt, tot, tab)
        
        self.viz.draw_comparison_charts(self.compare_canvas, self.scatter_canvas, 
                                       self.summary_data, self.last_results)
        self.btn_export.config(state=tk.NORMAL)
        self.btn_pdf.config(state=tk.NORMAL)
        self.celebrate_success()

