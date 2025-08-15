
import tkinter as tk
from tkinter import ttk, messagebox
import collections
from datetime import time, datetime, timedelta

class PomodoroPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("포모도로 데일리 플래너")
        self.root.geometry("1200x750") # Quarter-screen friendly size
        self.root.protocol("WM_DELETE_WINDOW", self._quit_app)

        # --- MODEL ---
        self.pomodoro_state = 'stopped'
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60
        self.seconds_left = self.work_duration
        self.stats = collections.defaultdict(int)
        self.tasks = collections.OrderedDict()
        self.task_id_counter = 0
        self._timer_id = None

        # Calendar-specific model properties
        self.cal_start_hour = 0 # 24시간 전체를 표시하기 위해 0시부터 시작
        self.cal_end_hour = 24
        self.hour_height = 60

        self._setup_styles()
        self._create_widgets()

        self._update_timer_display()
        self._update_pomodoro_button()
        self._update_stats_display()
        self.root.after(100, self._draw_calendar_background) # Ensure canvas has size
        self._start_timer()

    def _setup_styles(self):
        style = ttk.Style()
        style.configure("OnTime.TLabel", foreground="green", font=('Helvetica', 10, 'overstrike'))
        style.configure("Delayed.TLabel", foreground="#E69B00", font=('Helvetica', 10, 'overstrike'))
        style.configure("Failed.TLabel", foreground="red", font=('Helvetica', 10, 'overstrike'))
        style.configure("Pending.TLabel", font=('Helvetica', 10))

    def _create_widgets(self):
        paned_window = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned_window.pack(expand=True, fill=tk.BOTH)

        left_pane = ttk.Frame(paned_window, width=450)
        paned_window.add(left_pane, weight=2)
        self._create_left_pane_widgets(left_pane)

        right_pane = ttk.Frame(paned_window)
        paned_window.add(right_pane, weight=3)
        self._create_right_pane_widgets(right_pane)

    def _create_left_pane_widgets(self, parent):
        left_frame = ttk.Frame(parent, padding="10")
        left_frame.pack(expand=True, fill=tk.BOTH)

        # Pomodoro Timer
        timer_frame = ttk.LabelFrame(left_frame, text="포모도로 타이머", padding="10")
        timer_frame.pack(fill=tk.X, pady=5)
        self.time_label = ttk.Label(timer_frame, font=("Helvetica", 36, "bold"))
        self.time_label.pack(pady=5)
        control_frame = ttk.Frame(timer_frame)
        control_frame.pack()
        self.start_stop_button = ttk.Button(control_frame, text="", command=self._toggle_pomodoro)
        self.start_stop_button.pack(side=tk.LEFT, padx=5)
        reset_button = ttk.Button(control_frame, text="리셋", command=self._reset_pomodoro)
        reset_button.pack(side=tk.LEFT, padx=5)

        # Task Management
        task_manager_frame = ttk.LabelFrame(left_frame, text="작업 관리", padding="10")
        task_manager_frame.pack(fill=tk.BOTH, pady=5, expand=True)
        
        add_task_frame = ttk.Frame(task_manager_frame)
        add_task_frame.pack(fill=tk.X, pady=5)
        self.task_name_entry = ttk.Entry(add_task_frame, width=30)
        self.task_name_entry.pack(fill=tk.X, expand=True, pady=2)
        
        time_input_frame = ttk.Frame(add_task_frame)
        time_input_frame.pack(fill=tk.X, pady=2)
        ttk.Label(time_input_frame, text="시작:").pack(side=tk.LEFT)
        self.start_hour = tk.Spinbox(time_input_frame, from_=0, to=23, width=3, format="%02.f")
        self.start_hour.pack(side=tk.LEFT)
        ttk.Label(time_input_frame, text=":").pack(side=tk.LEFT)
        self.start_minute = tk.Spinbox(time_input_frame, from_=0, to=59, width=3, format="%02.f")
        self.start_minute.pack(side=tk.LEFT)
        ttk.Label(time_input_frame, text="   종료:").pack(side=tk.LEFT)
        self.end_hour = tk.Spinbox(time_input_frame, from_=0, to=23, width=3, format="%02.f")
        self.end_hour.pack(side=tk.LEFT)
        ttk.Label(time_input_frame, text=":").pack(side=tk.LEFT)
        self.end_minute = tk.Spinbox(time_input_frame, from_=0, to=59, width=3, format="%02.f")
        self.end_minute.pack(side=tk.LEFT)

        add_button = ttk.Button(add_task_frame, text="작업 추가", command=self._add_task)
        add_button.pack(pady=5)

        self.task_list_frame = ttk.Frame(task_manager_frame)
        self.task_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Stats
        stats_frame = ttk.LabelFrame(left_frame, text="통계", padding="10")
        stats_frame.pack(fill=tk.X, pady=5)
        self.stats_labels = {k: ttk.Label(stats_frame, text="") for k in ["completed", "success_rate", "focus_ratio", "task_completion"]}
        for label in self.stats_labels.values(): label.pack(anchor="w")

    def _create_right_pane_widgets(self, parent):
        container = ttk.Frame(parent)
        container.pack(expand=True, fill=tk.BOTH)
        self.calendar_canvas = tk.Canvas(container, bg='white')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.calendar_canvas.yview)
        self.calendar_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.calendar_canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def _draw_calendar_background(self):
        self.calendar_canvas.delete("background")
        width = self.calendar_canvas.winfo_width()
        height = self.hour_height * (self.cal_end_hour - self.cal_start_hour + 1)
        self.calendar_canvas.configure(scrollregion=(0, 0, width, height))

        for hour in range(self.cal_start_hour, self.cal_end_hour + 1):
            y = (hour - self.cal_start_hour) * self.hour_height
            self.calendar_canvas.create_line(50, y, width, y, fill="#e0e0e0", tags="background")
            self.calendar_canvas.create_text(25, y, text=f"{hour:02d}:00", anchor=tk.W, tags="background")

    def _draw_tasks_on_calendar(self):
        self.calendar_canvas.delete("task")
        
        layouts = self._calculate_task_layouts()

        for task_id, task in self.tasks.items():
            layout = layouts[task_id]
            start_y = self._time_to_y(task['start_time'])
            end_y = self._time_to_y(task['end_time'])
            
            total_width = self.calendar_canvas.winfo_width() - 70 # Drawable width
            if total_width < 100: total_width = 330

            col_width = total_width / layout['total_cols']
            x0 = 60 + layout['col'] * col_width
            x1 = x0 + col_width - 2 #-2 for padding

            color_map = {'pending': "#a1c4fd", 'on-time': "#a6e3a1", 'delayed': "#f9e2af", 'failed': "#f38ba8"}
            color = color_map.get(task['status'], "#dcdcdc")

            self.calendar_canvas.create_rectangle(x0, start_y, x1, end_y, fill=color, outline="#6699ff", tags="task")
            self.calendar_canvas.create_text(x0 + 5, start_y + 5, text=task['name'], anchor=tk.NW, tags="task", width=int(col_width-10))

    def _calculate_task_layouts(self):
        layouts = {}
        sorted_tasks = sorted(self.tasks.items(), key=lambda item: item[1]['start_time'])

        for i in range(len(sorted_tasks)):
            task_id, task = sorted_tasks[i]
            
            # Find collisions with tasks that have already been placed
            collisions = []
            for j in range(i):
                prev_task_id, prev_task = sorted_tasks[j]
                # Check for time overlap
                if task['start_time'] < prev_task['end_time'] and task['end_time'] > prev_task['start_time']:
                    collisions.append(layouts[prev_task_id])
            
            # Find the first available column
            col = 0
            while any(c['col'] == col for c in collisions):
                col += 1
            
            layouts[task_id] = {'col': col, 'total_cols': 1} # Start with 1 total col

        # Second pass to determine total_cols for each task
        for task_id, layout in layouts.items():
            task = self.tasks[task_id]
            overlapping_cols = {layout['col']}
            for other_id, other_layout in layouts.items():
                if task_id == other_id: continue
                other_task = self.tasks[other_id]
                if task['start_time'] < other_task['end_time'] and task['end_time'] > other_task['start_time']:
                    overlapping_cols.add(other_layout['col'])
            layout['total_cols'] = max(layout['total_cols'], len(overlapping_cols))

        return layouts

    def _time_to_y(self, t):
        return (t.hour - self.cal_start_hour + t.minute / 60) * self.hour_height

    def _update_current_time_indicator(self):
        self.calendar_canvas.delete("time_indicator")
        now = datetime.now().time()
        if self.cal_start_hour <= now.hour < self.cal_end_hour:
            y = self._time_to_y(now)
            width = self.calendar_canvas.winfo_width()
            self.calendar_canvas.create_line(50, y, width, y, fill="red", width=2, tags="time_indicator")

    def _add_task(self):
        name = self.task_name_entry.get().strip()
        if not name: return messagebox.showwarning("Input Error", "Task name is required.")
        try:
            start_t = time(int(self.start_hour.get()), int(self.start_minute.get()))
            end_t = time(int(self.end_hour.get()), int(self.end_minute.get()))
            if start_t >= end_t: return messagebox.showwarning("Time Error", "End time must be after start time.")
        except ValueError: return messagebox.showwarning("Input Error", "Hours and minutes must be numbers.")

        task_id = self.task_id_counter
        self.task_id_counter += 1
        self.tasks[task_id] = {
            "name": name, "start_time": start_t, "end_time": end_t,
            "is_complete": tk.BooleanVar(value=False), "status": "pending", "delay_info": None, "widgets": {}
        }
        self._create_task_list_item(task_id)
        self._draw_tasks_on_calendar()
        self._update_stats_display()
        self.task_name_entry.delete(0, tk.END)

    def _create_task_list_item(self, task_id):
        task = self.tasks[task_id]
        task_frame = ttk.Frame(self.task_list_frame)
        task_frame.pack(fill=tk.X, pady=2)
        cb = ttk.Checkbutton(task_frame, var=task['is_complete'], command=lambda i=task_id: self._on_task_complete_toggle(i))
        cb.pack(side=tk.LEFT)
        label = ttk.Label(task_frame, text="")
        label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        delete_btn = ttk.Button(task_frame, text="삭제", command=lambda i=task_id: self._delete_task(i))
        delete_btn.pack(side=tk.RIGHT)
        task['widgets'] = {'frame': task_frame, 'label': label, 'checkbox': cb}
        self._update_task_list_item_display(task_id)

    def _on_task_complete_toggle(self, task_id):
        task = self.tasks[task_id]
        is_now_complete = task['is_complete'].get()

        if is_now_complete:
            now_dt = datetime.now()
            end_dt = datetime.combine(now_dt.date(), task['end_time'])
            start_dt = datetime.combine(now_dt.date(), task['start_time'])
            scheduled_duration = end_dt - start_dt

            if now_dt <= end_dt:
                task['status'] = 'on-time'
            else:
                delay = now_dt - end_dt
                delay_percentage = (delay.total_seconds() / scheduled_duration.total_seconds()) * 100
                if delay_percentage <= 25:
                    task['status'] = 'delayed'
                    task['delay_info'] = f"{delay_percentage:.1f}% 지연"
                else:
                    task['status'] = 'failed'
        else:
            task['status'] = 'pending'
            task['delay_info'] = None

        self._update_task_list_item_display(task_id)
        self._draw_tasks_on_calendar()
        self._update_stats_display()

    def _delete_task(self, task_id):
        task = self.tasks.get(task_id)
        if task and messagebox.askyesno("Delete Task", f"Delete '{task['name']}'?"):
            task['widgets']['frame'].destroy()
            del self.tasks[task_id]
            self._draw_tasks_on_calendar()
            self._update_stats_display()

    def _update_task_list_item_display(self, task_id):
        task = self.tasks[task_id]
        now = datetime.now().time()
        remaining_text = ""
        if not task['is_complete'].get() and task['start_time'] <= now <= task['end_time']:
            end_dt = datetime.combine(datetime.now().date(), task['end_time'])
            now_dt = datetime.now()
            remaining_delta = end_dt - now_dt
            if remaining_delta.total_seconds() > 0:
                mins, secs = divmod(int(remaining_delta.total_seconds()), 60)
                hours, mins = divmod(mins, 60)
                remaining_text = f" (남음: {hours:02d}:{mins:02d}:{secs:02d})"

        time_str = f"{task['start_time'].strftime('%H:%M')}-{task['end_time'].strftime('%H:%M')}"
        base_text = f"{task['name']} [{time_str}]"
        delay_text = f" - {task['delay_info']}" if task['delay_info'] else ""
        
        full_text = base_text + remaining_text + delay_text
        task['widgets']['label'].config(text=full_text)
        
        style_map = {'pending': "Pending.TLabel", 'on-time': "OnTime.TLabel", 'delayed': "Delayed.TLabel", 'failed': "Failed.TLabel"}
        task['widgets']['label'].config(style=style_map.get(task['status'], "Pending.TLabel"))

    def _update_clocks(self):
        if self.pomodoro_state in ['work', 'break']:
            self.seconds_left -= 1
            if self.pomodoro_state == 'work': self.stats['total_focus_seconds'] += 1
            else: self.stats['total_break_seconds'] += 1
            if self.seconds_left < 0: self._handle_session_end()
        
        # 자동 상태 업데이트 로직 추가
        self._check_and_update_task_statuses()

        for task_id in self.tasks:
            self._update_task_list_item_display(task_id)

        self._update_timer_display()
        self._update_current_time_indicator()
        self._timer_id = self.root.after(1000, self._update_clocks)

    def _check_and_update_task_statuses(self):
        """현재 시간에 따라 완료되지 않은 작업의 상태를 자동으로 업데이트"""
        now_dt = datetime.now()
        
        for task in self.tasks.values():
            if task['is_complete'].get():
                continue # 이미 완료된 작업은 건너뜀

            end_dt = datetime.combine(now_dt.date(), task['end_time'])
            if now_dt > end_dt:
                start_dt = datetime.combine(now_dt.date(), task['start_time'])
                scheduled_duration = end_dt - start_dt
                if scheduled_duration.total_seconds() <= 0: continue

                delay = now_dt - end_dt
                delay_percentage = (delay.total_seconds() / scheduled_duration.total_seconds()) * 100
                
                new_status = task['status']
                if delay_percentage > 25:
                    new_status = 'failed'
                else:
                    new_status = 'delayed'
                
                if task['status'] != new_status:
                    task['status'] = new_status
                    self._draw_tasks_on_calendar() # 상태 변경 시 캘린더 업데이트
                
                if new_status == 'delayed':
                    task['delay_info'] = f"{delay_percentage:.1f}% 지연"

    def _toggle_pomodoro(self):
        if self.pomodoro_state in ['work', 'break']: 
            if self.pomodoro_state == 'work': self.stats['failure'] += 1
            self.pomodoro_state = 'stopped'
        else: 
            if self.start_stop_button.cget('text') == "집중 시작": self.pomodoro_state = 'work'
            else: self.pomodoro_state = 'break'
        self._update_pomodoro_button()
        self._update_stats_display()

    def _reset_pomodoro(self):
        self.pomodoro_state = 'stopped'
        self.seconds_left = self.work_duration
        self._update_timer_display()
        self._update_pomodoro_button()

    def _handle_session_end(self):
        self.root.bell()
        if self.pomodoro_state == 'work':
            self.stats['success'] += 1
            self.stats['completed_pomodoros'] += 1
        self.pomodoro_state = 'stopped'
        self._update_pomodoro_button()
        self._update_stats_display()

    def _update_timer_display(self):
        mins, secs = divmod(self.seconds_left, 60)
        self.time_label.config(text=f"{mins:02d}:{secs:02d}")

    def _update_pomodoro_button(self):
        if self.pomodoro_state == 'stopped':
            prev_state_was_work = self.start_stop_button.cget('text') == "정지" and self.seconds_left < 1
            if prev_state_was_work:
                 self.start_stop_button.config(text="휴식 시작")
                 self.seconds_left = self.break_duration
            else:
                 self.start_stop_button.config(text="집중 시작")
                 self.seconds_left = self.work_duration
            self._update_timer_display()
        else:
            self.start_stop_button.config(text="정지")

    def _update_stats_display(self):
        s = self.stats
        total_sessions = s['success'] + s['failure']
        success_rate = (s['success'] / total_sessions * 100) if total_sessions > 0 else 0
        
        # 총 집중 시간을 HH:MM:SS 형식으로 변환
        total_focus_seconds = s['total_focus_seconds']
        h, rem = divmod(total_focus_seconds, 3600)
        m, s_rem = divmod(rem, 60)
        total_focus_time_str = f"{int(h):02d}:{int(m):02d}:{int(s_rem):02d}"

        # 가중치 기반 작업 완료율 계산
        total_tasks = len(self.tasks)
        weighted_score = 0
        for task in self.tasks.values():
            if task['status'] == 'on-time':
                weighted_score += 1
            elif task['status'] == 'delayed':
                weighted_score += 0.5
        
        task_completion_rate = (weighted_score / total_tasks * 100) if total_tasks > 0 else 0

        self.stats_labels['completed'].config(text=f"완료한 뽀모도로: {s['completed_pomodoros']}회")
        self.stats_labels['success_rate'].config(text=f"뽀모도로 성공률: {success_rate:.1f}% ({s['success']}/{total_sessions})")
        self.stats_labels['focus_ratio'].config(text=f"총 집중 시간: {total_focus_time_str}") # 레이블 텍스트 변경
        self.stats_labels['task_completion'].config(text=f"작업 달성도: {task_completion_rate:.1f}%") # 이름 변경

    def _start_timer(self):
        if not self._timer_id:
            self._update_clocks()

    def _quit_app(self):
        if messagebox.askokcancel("종료", "정말로 종료하시겠습니까?"):
            if self._timer_id: self.root.after_cancel(self._timer_id)
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroPlannerApp(root)
    root.mainloop()
