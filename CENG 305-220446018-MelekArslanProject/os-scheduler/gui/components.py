# --------------------------------------------
# Course: CS 305 - Operating Systems
# Student: Melek Arslan
# Student ID: 220446018
# Assignment: Process Scheduling Simulator
# File: gui/components.py
# Date: 12-12-2025
# --------------------------------------------

"""
UI bileşenleri (ToolTip, butonlar, vb.)
"""

import tkinter as tk


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
        if self.tipwindow or not self.text: 
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, 
                        background="#0B0C10", foreground="#66FCF1", 
                        relief=tk.SOLID, borderwidth=1, font=("Consolas", 10))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw: 
            tw.destroy()


def CreateToolTip(widget, text):
    """ToolTip oluşturma yardımcı fonksiyonu"""
    toolTip = ToolTip(widget)
    widget.bind('<Enter>', lambda e: toolTip.showtip(text))
    widget.bind('<Leave>', lambda e: toolTip.hidetip())

