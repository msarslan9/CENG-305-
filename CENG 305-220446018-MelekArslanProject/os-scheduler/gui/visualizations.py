# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: gui/visualizations.py
# Date: 12-12-2025
# --------------------------------------------

"""
Görselleştirme fonksiyonları (Gantt chart, grafikler, vb.)
"""

import tkinter as tk
import random


class Visualizations:
    """Görselleştirme sınıfı"""
    
    def __init__(self, root, proc_colors):
        self.root = root
        self.proc_colors = proc_colors
        self.neon_cyan = "#66FCF1"
        self.neon_pink = "#ff007f"
        self.neon_green = "#50fa7b"
        self.neon_teal = "#45A29E"
        self.bg_color = "#0B0C10"
        self.panel_color = "#1F2833"
    
    def draw_gauge(self, canvas, percent):
        """CPU kullanım göstergesi çiz"""
        canvas.delete("all")
        x, y, r = 70, 70, 55
        canvas.create_oval(x-r, y-r, x+r, y+r, outline="#1F2833", width=8)
        if percent > 0:
            extent = (percent / 100) * 360
            canvas.create_arc(x-r, y-r, x+r, y+r, start=90, extent=-extent, 
                            style=tk.ARC, outline=self.neon_cyan, width=8)
        canvas.create_text(x, y-10, text="CPU Usage", fill="#888", font=("Segoe UI", 8))
        canvas.create_text(x, y+10, text=f"{percent:.0f}%", fill="white", 
                          font=("Segoe UI", 16, "bold"))
    
    def animate_gantt(self, canvas, gantt, total_time, speed_var, proc_colors, is_running_callback=None):
        """Gantt chart animasyonu"""
        canvas.delete("all")
        width = canvas.winfo_width()
        if width < 100: 
            width = 800
        margin = 10
        usable = width - 2*margin
        scale = usable / total_time if total_time > 0 else 1
        canvas.create_line(margin, 55, width-margin, 55, fill="#555", width=1)
        
        def draw(idx):
            if idx >= len(gantt):
                canvas.create_text(margin + total_time * scale, 65, text=str(total_time), 
                                  fill="#aaa", font=("Arial", 8))
                if is_running_callback:
                    is_running_callback(False)
                return
            lbl, s, e = gantt[idx]
            x1 = margin + s * scale
            x2 = margin + e * scale
            color = "#1F2833" if lbl == "idle" else proc_colors.get(lbl, "gray")
            outline = "#333" if lbl == "idle" else "white"
            rect = canvas.create_rectangle(x1, 15, x2, 45, fill=color, outline=outline, width=0)
            canvas.create_text((x1+x2)/2, 30, text=lbl, fill="white", font=("Segoe UI", 9, "bold"))
            canvas.create_text(x1, 65, text=str(s), fill="#888", font=("Arial", 8))
            self.root.update()
            delay = int(speed_var.get() * 1000)
            self.root.after(delay, draw, idx+1)
        
        if is_running_callback:
            is_running_callback(True)
        draw(0)
    
    def draw_comparison_charts(self, compare_canvas, scatter_canvas, summary, last_results):
        """Karşılaştırma grafikleri çiz"""
        c = compare_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 100: 
            w = 600
            h = 400
        bar_w = 30
        space = 60
        group_space = 100
        start_x = 50
        base_y = h - 50
        max_val = 1
        for s in summary: 
            max_val = max(max_val, s[1], s[2])
        scale = (h - 100) / max_val
        c.create_line(40, base_y, w-20, base_y, fill="#555", width=2)
        
        for i, (name, wt, tat) in enumerate(summary):
            x = start_x + i * group_space
            h_wt = wt * scale
            c.create_rectangle(x, base_y - h_wt, x + bar_w, base_y, fill=self.neon_cyan, outline="")
            c.create_text(x + bar_w/2, base_y - h_wt - 10, text=f"{wt:.1f}", 
                         fill="white", font=("Arial", 8))
            h_tat = tat * scale
            c.create_rectangle(x + bar_w, base_y - h_tat, x + 2*bar_w, base_y, 
                              fill=self.neon_pink, outline="")
            c.create_text(x + 1.5*bar_w, base_y - h_tat - 10, text=f"{tat:.1f}", 
                         fill="white", font=("Arial", 8))
            c.create_text(x + bar_w, base_y + 20, text=name, fill="#888", font=("Segoe UI", 8))
        
        c.create_rectangle(w-150, 20, w-140, 30, fill=self.neon_cyan)
        c.create_text(w-90, 25, text="Avg Waiting", fill="white", anchor="w")
        c.create_rectangle(w-150, 40, w-140, 50, fill=self.neon_pink)
        c.create_text(w-90, 45, text="Avg Turnaround", fill="white", anchor="w")

        # Scatter plot
        sc = scatter_canvas
        sc.delete("all")
        sw = sc.winfo_width()
        sh = sc.winfo_height()
        if sw < 100: 
            sw = 600
            sh = 400
        margin = 40
        sc.create_line(margin, sh-margin, sw-margin, sh-margin, fill="#555", width=2)
        sc.create_line(margin, sh-margin, margin, margin, fill="#555", width=2)
        sc.create_text(sw/2, sh-10, text="Burst Time (Job Size)", fill="#888")
        sc.create_text(15, sh/2, text="Wait\nTime", fill="#888", angle=90)
        
        if "SJF" in last_results:
            data = last_results["SJF"]
            max_burst = max(d['burst'] for d in data.values()) if data else 1
            max_wait = max(d['waiting'] for d in data.values()) if data else 1
            for pid, metric in data.items():
                b = metric['burst']
                w = metric['waiting']
                px = margin + (b / max_burst) * (sw - 2*margin)
                py = (sh - margin) - (w / max_wait) * (sh - 2*margin)
                sc.create_oval(px-4, py-4, px+4, py+4, fill=self.neon_green, outline="white")
                sc.create_text(px, py-10, text=pid, fill="white", font=("Arial", 8))
    
    def animate_monitor(self, canvas, monitor_data, is_running):
        """Sistem monitör animasyonu"""
        w, h = 200, 50
        canvas.delete("all")
        canvas.create_line(0, h/2, w, h/2, fill="#1F2833")
        if is_running: 
            val = random.randint(10, 40)
        else: 
            val = random.randint(2, 5)
        monitor_data.append(val)
        points = []
        for i, d in enumerate(monitor_data):
            points.append(i * (w / 50))
            points.append(h - d)
        if len(points) > 2:
            canvas.create_line(points, fill=self.neon_cyan, width=2, smooth=True)
    
    def celebrate_success(self, compare_canvas, root, notebook, compare_frame):
        """Başarı animasyonu (konfeti)"""
        notebook.select(compare_frame)
        root.update()
        canvas = compare_canvas
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        colors = [self.neon_cyan, self.neon_pink, self.neon_green, "#FCEE0A"]
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
                for p in particles: 
                    canvas.delete(p['id'])
                return
            for p in particles:
                canvas.move(p['id'], 0, p['speed'])
                coords = canvas.coords(p['id'])
                if coords and coords[1] > h:
                    canvas.move(p['id'], 0, -h-20)
            root.after(30, update_particles, steps-1)
        
        update_particles(100)

