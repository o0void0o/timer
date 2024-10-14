import tkinter as tk
from tkinter import ttk
import time
from plyer import notification
import threading
import re

class Timer:
    def __init__(self, app, index):
        self.app = app
        self.index = index
        self.duration = 0
        self.remaining = 0
        self.is_running = False
        self.is_expired = False
        self.last_notification = 0
        self.name = ""

    def start(self):
        if not self.is_running and self.duration > 0:
            self.is_running = True
            self.is_expired = False
            threading.Thread(target=self.run, daemon=True).start()

    def stop(self):
        self.is_running = False

    def clear(self):
        self.stop()
        self.duration = 0
        self.remaining = 0
        self.is_expired = False
        self.app.update_display(self.index)

    def run(self):
        start_time = time.time()
        while self.is_running and self.remaining > 0:
            self.remaining = self.duration - int(time.time() - start_time)
            self.app.update_display(self.index)
            time.sleep(0.1)
        
        if self.is_running:
            self.is_expired = True
            self.is_running = False
            self.remaining = 0
            self.app.update_display(self.index)
            self.app.show_notification(self.index)

class TimerApp:
    def __init__(self, master):
        self.master = master
        master.title("Multi-Timer App")
        
        self.timers = [Timer(self, i) for i in range(10)]
        self.create_widgets()

    def create_widgets(self):
        for i, timer in enumerate(self.timers):
            frame = ttk.Frame(self.master, padding="10")
            frame.grid(row=i, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            timer.name_entry = ttk.Entry(frame, width=15)
            timer.name_entry.grid(row=0, column=0, padx=5)
            timer.name_entry.insert(0, f"Timer {i+1}")

            timer.time_var = tk.StringVar(value="00:00:00")
            timer.label = ttk.Label(frame, textvariable=timer.time_var, font=("Arial", 16))
            timer.label.grid(row=0, column=1, padx=5)

            timer.entry = ttk.Entry(frame, width=10)
            timer.entry.grid(row=0, column=2, padx=5)
            timer.entry.insert(0, "hh:mm:ss")

            timer.start_button = ttk.Button(frame, text="Start", command=lambda t=timer: self.start_timer(t))
            timer.start_button.grid(row=0, column=3, padx=5)

            timer.stop_button = ttk.Button(frame, text="Stop", command=lambda t=timer: self.stop_timer(t))
            timer.stop_button.grid(row=0, column=4, padx=5)

            timer.clear_button = ttk.Button(frame, text="Clear", command=lambda t=timer: self.clear_timer(t))
            timer.clear_button.grid(row=0, column=5, padx=5)

    def parse_time(self, time_str):
        # Remove any whitespace
        time_str = time_str.strip()
        
        # Check if it's just seconds
        if time_str.isdigit():
            return int(time_str)
        
        # Check for MM:SS or HH:MM:SS format
        time_parts = time_str.split(':')
        if len(time_parts) == 2:
            minutes, seconds = map(int, time_parts)
            return minutes * 60 + seconds
        elif len(time_parts) == 3:
            hours, minutes, seconds = map(int, time_parts)
            return hours * 3600 + minutes * 60 + seconds
        else:
            raise ValueError("Invalid time format")

    def start_timer(self, timer):
        try:
            timer.duration = self.parse_time(timer.entry.get())
            timer.remaining = timer.duration
            timer.name = timer.name_entry.get()
            timer.start()
        except ValueError:
            timer.time_var.set("Invalid input")

    def stop_timer(self, timer):
        timer.stop()

    def clear_timer(self, timer):
        timer.clear()

    def update_display(self, index):
        timer = self.timers[index]
        if timer.is_expired:
            timer.time_var.set("EXPIRED")
        else:
            hours, rem = divmod(timer.remaining, 3600)
            minutes, seconds = divmod(rem, 60)
            timer.time_var.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def show_notification(self, index):
        timer = self.timers[index]
        current_time = time.time()
        if current_time - timer.last_notification >= 60:  # Check if a minute has passed
            notification.notify(
                title=f"{timer.name} Expired!",
                message=f"{timer.name} has completed!",
                app_name="Python Multi-Timer",
                timeout=10
            )
            timer.last_notification = current_time

    def check_expired_timers(self):
        current_time = time.time()
        for timer in self.timers:
            if timer.is_expired and current_time - timer.last_notification >= 60:
                self.show_notification(timer.index)
        self.master.after(1000, self.check_expired_timers)  # Check every second

root = tk.Tk()
app = TimerApp(root)
app.check_expired_timers()  # Start checking for expired timers
root.mainloop()