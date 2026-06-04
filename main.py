import tkinter as tk
from tkinter import ttk
import json
import os
import winsound

COLORS = {
    "bg": "#0F0F1A",
    "card": "#1A1A2E",
    "primary": "#E94560",
    "work": "#FF6B6B",
    "break": "#4ECDC4",
    "text": "#FFFFFF",
    "text_dim": "#8888AA",
    "accent": "#F5F5F5",
    "track": "#2A2A4E",
}


class PomodoroTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("番茄钟")
        self.root.geometry("400x600")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        self.work_duration = 25 * 60
        self.short_break = 5 * 60
        self.long_break = 15 * 60
        self.long_break_interval = 4
        self.load_settings()

        self.is_running = False
        self.is_work = True
        self.remaining = self.work_duration
        self.pomodoro_count = 0
        self.current_in_interval = 0
        self.timer_job = None

        self.setup_ui()
        self.update_display()

    def load_settings(self):
        try:
            path = os.path.join(os.path.dirname(__file__), "settings.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.work_duration = data.get("work_duration", 25 * 60)
                    self.short_break = data.get("short_break", 5 * 60)
                    self.long_break = data.get("long_break", 15 * 60)
                    self.long_break_interval = data.get("long_break_interval", 4)
        except:
            pass

    def save_settings(self):
        try:
            path = os.path.join(os.path.dirname(__file__), "settings.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({
                    "work_duration": self.work_duration,
                    "short_break": self.short_break,
                    "long_break": self.long_break,
                    "long_break_interval": self.long_break_interval
                }, f, ensure_ascii=False)
        except:
            pass

    def setup_ui(self):
        # 标题
        title = tk.Label(self.root, text="🍅 番茄钟", font=("Microsoft YaHei", 26, "bold"),
                        bg=COLORS["bg"], fg=COLORS["text"])
        title.pack(pady=18)

        # 模式切换
        mode_frame = tk.Frame(self.root, bg=COLORS["card"])
        mode_frame.pack(pady=8, fill=tk.X, padx=30)

        mode_inner = tk.Frame(mode_frame, bg=COLORS["card"])
        mode_inner.pack(pady=10, padx=15)

        self.work_tab = tk.Label(mode_inner, text="专注", font=("Microsoft YaHei", 14, "bold"),
                                bg=COLORS["card"], fg=COLORS["work"], width=8)
        self.work_tab.pack(side=tk.LEFT, padx=10)
        self.break_tab = tk.Label(mode_inner, text="休息", font=("Microsoft YaHei", 14),
                                  bg=COLORS["card"], fg=COLORS["text_dim"], width=8)
        self.break_tab.pack(side=tk.LEFT, padx=10)

        # 圆形计时器
        self.canvas = tk.Canvas(self.root, width=280, height=280, bg=COLORS["bg"],
                                highlightthickness=0)
        self.canvas.pack(pady=16)
        self.draw_timer_circle()

        self.timer_label = tk.Label(self.canvas, text="25:00",
                                    font=("Microsoft YaHei", 56, "bold"),
                                    bg=COLORS["bg"], fg=COLORS["text"])
        self.timer_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # 统计
        self.stats_label = tk.Label(self.root, text=f"🍅 已完成 {self.pomodoro_count}",
                                    font=("Microsoft YaHei", 13),
                                    bg=COLORS["bg"], fg=COLORS["text_dim"])
        self.stats_label.pack(pady=6)

        # 控制按钮
        btn_frame = tk.Frame(self.root, bg=COLORS["bg"])
        btn_frame.pack(pady=14)

        self.start_btn = tk.Button(btn_frame, text="▶ 开始", font=("Microsoft YaHei", 14, "bold"),
                                   width=9, bg=COLORS["primary"], fg="white",
                                   command=self.start_timer, relief=tk.FLAT, cursor="hand2")
        self.start_btn.grid(row=0, column=0, padx=8)

        tk.Button(btn_frame, text="⟳ 重置", font=("Microsoft YaHei", 13),
                  width=7, bg=COLORS["track"], fg="white",
                  command=self.reset_timer, relief=tk.FLAT, cursor="hand2").grid(row=0, column=1, padx=8)

        tk.Button(btn_frame, text="⏭ 跳过", font=("Microsoft YaHei", 13),
                  width=7, bg=COLORS["track"], fg="white",
                  command=self.skip_phase, relief=tk.FLAT, cursor="hand2").grid(row=0, column=2, padx=8)

        # 设置面板
        settings_frame = tk.LabelFrame(self.root, text="设置", font=("Microsoft YaHei", 11),
                                       bg=COLORS["card"], fg=COLORS["text"], padx=12, pady=8)
        settings_frame.pack(pady=10, fill=tk.X, padx=30)

        row1 = tk.Frame(settings_frame, bg=COLORS["card"])
        row1.pack(fill=tk.X, pady=3)
        tk.Label(row1, text="工作", font=("Microsoft YaHei", 10), bg=COLORS["card"],
                fg=COLORS["text"]).pack(side=tk.LEFT)
        self.work_var = tk.IntVar(value=self.work_duration // 60)
        ttk.Spinbox(row1, from_=1, to=60, width=4, textvariable=self.work_var,
                    font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=2)
        tk.Label(row1, text="分   休息", font=("Microsoft YaHei", 10), bg=COLORS["card"],
                fg=COLORS["text"]).pack(side=tk.LEFT, padx=(4, 2))
        self.short_var = tk.IntVar(value=self.short_break // 60)
        ttk.Spinbox(row1, from_=1, to=30, width=4, textvariable=self.short_var,
                    font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=2)
        tk.Label(row1, text="分", font=("Microsoft YaHei", 10), bg=COLORS["card"],
                fg=COLORS["text"]).pack(side=tk.LEFT)

        row2 = tk.Frame(settings_frame, bg=COLORS["card"])
        row2.pack(fill=tk.X, pady=3)
        tk.Label(row2, text="长休息", font=("Microsoft YaHei", 10), bg=COLORS["card"],
                fg=COLORS["text"]).pack(side=tk.LEFT)
        self.long_var = tk.IntVar(value=self.long_break // 60)
        ttk.Spinbox(row2, from_=1, to=60, width=4, textvariable=self.long_var,
                    font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=2)
        tk.Label(row2, text="分   间隔", font=("Microsoft YaHei", 10), bg=COLORS["card"],
                fg=COLORS["text"]).pack(side=tk.LEFT, padx=(4, 2))
        self.interval_var = tk.IntVar(value=self.long_break_interval)
        ttk.Spinbox(row2, from_=2, to=10, width=4, textvariable=self.interval_var,
                    font=("Microsoft YaHei", 10)).pack(side=tk.LEFT, padx=2)
        tk.Label(row2, text="个番茄", font=("Microsoft YaHei", 10), bg=COLORS["card"],
                fg=COLORS["text"]).pack(side=tk.LEFT)

        tk.Button(self.root, text="✓ 应用设置", font=("Microsoft YaHei", 11, "bold"),
                 bg="#27AE60", fg="white", command=self.apply_settings,
                 relief=tk.FLAT, cursor="hand2", padx=15, pady=6).pack(pady=10)

        self.root.bind('<space>', lambda e: self.start_timer())
        self.root.bind('<r>', lambda e: self.reset_timer())
        self.root.bind('<s>', lambda e: self.skip_phase())

    def draw_timer_circle(self):
        self.canvas.delete("all")
        cx, cy, r = 140, 140, 115

        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                width=10, outline=COLORS["track"], fill="")

        if self.is_work:
            total, color = self.work_duration, COLORS["work"]
        else:
            total = self.short_break if self.current_in_interval < self.long_break_interval else self.long_break
            color = COLORS["break"]

        progress = self.remaining / total if total > 0 else 0
        extent = progress * 360

        if extent > 0:
            self.canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                    start=270, extent=-extent,
                                    width=10, outline=color, style=tk.ARC)

        self.canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill=color, outline="")

    def apply_settings(self):
        self.work_duration = self.work_var.get() * 60
        self.short_break = self.short_var.get() * 60
        self.long_break = self.long_var.get() * 60
        self.long_break_interval = self.interval_var.get()
        self.save_settings()

        if not self.is_running:
            self.remaining = self.work_duration if self.is_work else \
                (self.short_break if self.current_in_interval < self.long_break_interval else self.long_break)
            self.update_display()

    def start_timer(self):
        if self.is_running:
            self.pause_timer()
        else:
            self.is_running = True
            self.start_btn.config(text="⏸ 暂停")
            self.play_start_chime()
            self.countdown()

    def pause_timer(self):
        self.is_running = False
        self.start_btn.config(text="▶ 开始")
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    def reset_timer(self):
        self.pause_timer()
        self.remaining = self.work_duration if self.is_work else \
            (self.short_break if self.current_in_interval < self.long_break_interval else self.long_break)
        self.update_display()

    def skip_phase(self):
        self.pause_timer()
        self.transition_to_next()

    def countdown(self):
        if self.is_running and self.remaining > 0:
            self.remaining -= 1
            self.update_display()
            self.timer_job = self.root.after(1000, self.countdown)
        elif self.remaining <= 0:
            self.on_timer_complete()

    def on_timer_complete(self):
        self.pause_timer()
        self.play_chime()
        if self.is_work:
            self.pomodoro_count += 1
            self.current_in_interval += 1
            self.stats_label.config(text=f"🍅 已完成 {self.pomodoro_count}")
        self.transition_to_next()

    def transition_to_next(self):
        if self.is_work:
            self.remaining = self.long_break if self.current_in_interval >= self.long_break_interval \
                else self.short_break
            self.current_in_interval = 0 if self.current_in_interval >= self.long_break_interval \
                else self.current_in_interval
            self.is_work = False
        else:
            self.remaining = self.work_duration
            self.is_work = True
        self.update_display()

    def update_display(self):
        m, s = self.remaining // 60, self.remaining % 60
        self.timer_label.config(text=f"{m:02d}:{s:02d}")

        if self.is_work:
            self.timer_label.config(fg=COLORS["text"])
            self.work_tab.config(fg=COLORS["work"], font=("Microsoft YaHei", 14, "bold"))
            self.break_tab.config(fg=COLORS["text_dim"], font=("Microsoft YaHei", 14))
        else:
            self.timer_label.config(fg=COLORS["break"])
            self.work_tab.config(fg=COLORS["text_dim"], font=("Microsoft YaHei", 14))
            self.break_tab.config(fg=COLORS["break"], font=("Microsoft YaHei", 14, "bold"))

        self.draw_timer_circle()

    def play_chime(self):
        try:
            winsound.Beep(880, 200)
            winsound.Beep(1047, 200)
            winsound.Beep(1319, 300)
        except:
            pass

    def play_start_chime(self):
        try:
            winsound.Beep(523, 100)
            winsound.Beep(659, 100)
        except:
            pass

    def run(self):
        self.root.mainloop()

def main():
    app = PomodoroTimer()
    app.run()

if __name__ == "__main__":
    main()