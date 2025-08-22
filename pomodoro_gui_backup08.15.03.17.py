import tkinter as tk
from tkinter import ttk, messagebox
import collections
from datetime import time, datetime, timedelta
import sqlite3
import os
from tkcalendar import Calendar

# Matplotlib and Pandas are required for graphing
try:
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

class PomodoroPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("포모도로 데일리 플래너")
        self.root.geometry("1200x750")
        self.db_path = 'pomodoro_data.db'

        # --- MODEL ---
        self.selected_date = datetime.now().date()
        self.pomodoro_state = 'stopped'
        self.paused_from_state = None
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60
        self.pause_duration = 60
        self.seconds_left = self.work_duration
        self.pause_seconds_left = self.pause_duration
        
        # 'today_stats' for live tracking, 'displayed_stats' for UI
        self.today_stats = collections.defaultdict(int)
        self.displayed_stats = self.today_stats 

        # 'today_tasks' for live tasks, 'displayed_tasks_data' for UI tasks
        self.today_tasks = collections.OrderedDict()
        self.displayed_tasks_data = self.today_tasks # Initially points to today's tasks
        self.task_id_counter = 0 # This counter should probably be global for all tasks, not just displayed ones.
                                 # But for now, it's used for the currently displayed tasks.
        self._timer_id = None
        self.cal_start_hour = 0
        self.cal_end_hour = 24
        self.hour_height = 60

        self._init_database()
        self._load_today_stats() # Load today's stats on startup
        self._load_today_tasks() # Load today's tasks on startup
        # Initialize global next task id to avoid UNIQUE constraint conflicts
        self.next_task_id = self._get_next_task_id()
        self._setup_styles()
        self._create_widgets()

        self._update_date_view()
        self._update_timer_display()
        self._update_pomodoro_button() # Set initial button text
        self.root.after(100, self._draw_calendar_background)
        self._start_timer()
        
        self.root.protocol("WM_DELETE_WINDOW", self._quit_app)

    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_summary (
                date TEXT PRIMARY KEY,
                completed_pomodoros INTEGER,
                pomodoro_success INTEGER,
                pomodoro_failure INTEGER,
                total_focus_seconds INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_date TEXT,
                name TEXT,
                start_time TEXT,
                end_time TEXT,
                status TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _get_next_task_id(self):
        """Returns a globally unique next task id across the whole tasks table and today's in-memory tasks."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT IFNULL(MAX(id), 0) FROM tasks")
            row = cursor.fetchone()
            conn.close()
            max_existing_id = row[0] if row and row[0] is not None else 0
        except Exception:
            max_existing_id = 0
        max_today_id = max(self.today_tasks.keys()) if self.today_tasks else 0
        return max(max_existing_id, max_today_id) + 1

    def _load_today_stats(self):
        """Loads stats for the current day from the DB into today_stats."""
        date_str = datetime.now().date().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_summary WHERE date = ?", (date_str,))
        stats_data = cursor.fetchone()
        if stats_data:
            self.today_stats['completed_pomodoros'] = stats_data[1]
            self.today_stats['success'] = stats_data[2]
            self.today_stats['failure'] = stats_data[3]
            self.today_stats['total_focus_seconds'] = stats_data[4]
        conn.close()

    def _load_today_tasks(self):
        """Loads tasks for the current day from the DB into today_tasks."""
        self.today_tasks.clear() # Clear existing in-memory tasks for today
        date_str = datetime.now().date().strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, start_time, end_time, status FROM tasks WHERE task_date = ?", (date_str,))
        tasks_data = cursor.fetchall()
        for row in tasks_data:
            task_id, name, start_t_str, end_t_str, status = row
            self.today_tasks[task_id] = {
                "name": name,
                "start_time": datetime.strptime(start_t_str, '%H:%M:%S').time(),
                "end_time": datetime.strptime(end_t_str, '%H:%M:%S').time(),
                "is_complete": tk.BooleanVar(value=(status != 'pending')),
                "status": status,
                "delay_info": None, 
                "widgets": {} # Widgets will be created when displayed
            }
        conn.close()

    def _load_data_for_selected_date(self):
        # Clear current task list widgets from UI
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
        
        # NEW: Reset widget references for all tasks in today_tasks
        # This ensures that if we return to today, widgets are recreated.
        for task in self.today_tasks.values():
            task['widgets'] = {}

        date_str = self.selected_date.strftime("%Y-%m-%d")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        is_today = (self.selected_date == datetime.now().date())

        if is_today:
            self.displayed_tasks_data = self.today_tasks
            self.displayed_stats = self.today_stats
        else:
            # Load historical tasks for the selected date
            self.displayed_tasks_data = collections.OrderedDict()
            cursor.execute("SELECT id, name, start_time, end_time, status FROM tasks WHERE task_date = ?", (date_str,))
            tasks_data = cursor.fetchall()
            for row in tasks_data:
                task_id, name, start_t_str, end_t_str, status = row
                self.displayed_tasks_data[task_id] = {
                    "name": name,
                    "start_time": datetime.strptime(start_t_str, '%H:%M:%S').time(),
                    "end_time": datetime.strptime(end_t_str, '%H:%M:%S').time(),
                    "is_complete": tk.BooleanVar(value=(status != 'pending')),
                    "status": status,
                    "delay_info": None, 
                    "widgets": {} 
                }
            
            # Load historical stats for the selected date
            self.displayed_stats = collections.defaultdict(int)
            cursor.execute("SELECT * FROM daily_summary WHERE date = ?", (date_str,))
            stats_data = cursor.fetchone()
            if stats_data:
                self.displayed_stats['completed_pomodoros'] = stats_data[1]
                self.displayed_stats['success'] = stats_data[2]
                self.displayed_stats['failure'] = stats_data[3]
                self.displayed_stats['total_focus_seconds'] = stats_data[4]
        
        # Now, populate UI based on self.displayed_tasks_data
        for task_id, task in self.displayed_tasks_data.items():
            self._create_task_list_item(task_id) 
            
        # Update task_id_counter based on the currently displayed tasks (legacy counter, kept for UI logic)
        self.task_id_counter = max(self.displayed_tasks_data.keys()) + 1 if self.displayed_tasks_data else 0
        # Also ensure global next_task_id never goes backwards
        if self.displayed_tasks_data:
            self.next_task_id = max(self.next_task_id, max(self.displayed_tasks_data.keys()) + 1)
        self._draw_tasks_on_calendar()
        conn.close()
        self._update_stats_display()

    def _save_data(self):
        # This should only save data for the day the work was actually done.
        date_str = datetime.now().date().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            # Wait up to 3s if the DB is temporarily locked
            conn.execute("PRAGMA busy_timeout = 3000")
            cursor = conn.cursor()

            # Always save the live 'today_stats'
            cursor.execute(
                "INSERT OR REPLACE INTO daily_summary VALUES (?, ?, ?, ?, ?)",
                (
                    date_str,
                    self.today_stats.get('completed_pomodoros', 0),
                    self.today_stats.get('success', 0),
                    self.today_stats.get('failure', 0),
                    self.today_stats.get('total_focus_seconds', 0),
                ),
            )

            # Save 'today_tasks' to the database.
            cursor.execute("DELETE FROM tasks WHERE task_date = ?", (date_str,))
            for task_id, task in self.today_tasks.items(): # Use task_id from items()
                cursor.execute(
                    "INSERT INTO tasks (id, task_date, name, start_time, end_time, status) VALUES (?, ?, ?, ?, ?, ?)", # Added id column
                    (
                        task_id, # Added task_id
                        date_str,
                        task['name'],
                        task['start_time'].strftime('%H:%M:%S'),
                        task['end_time'].strftime('%H:%M:%S'),
                        task['status'],
                    ),
                )
            conn.commit()

    def _setup_styles(self):
        style = ttk.Style()
        style.configure("OnTime.TLabel", foreground="green", font=('Helvetica', 10, 'overstrike'))
        style.configure("Delayed.TLabel", foreground="#E69B00", font=('Helvetica', 10, 'overstrike'))
        style.configure("Failed.TLabel", foreground="red", font=('Helvetica', 10, 'overstrike'))
        style.configure("Pending.TLabel", font=('Helvetica', 10))
        style.configure("Timer.TLabel", font=("Helvetica", 36, "bold"))
        style.configure("Paused.Timer.TLabel", foreground='red', font=("Helvetica", 36, "bold"))
        style.configure("Date.TButton", font=("Helvetica", 12, "bold"))

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

        # --- Date Navigation ---
        date_nav_frame = ttk.Frame(left_frame)
        date_nav_frame.pack(pady=(0, 10), fill=tk.X)
        self.prev_day_button = ttk.Button(date_nav_frame, text="◀", command=self._go_to_previous_day, width=3)
        self.prev_day_button.pack(side=tk.LEFT, padx=(0, 5))
        self.date_button = ttk.Button(date_nav_frame, text="", 
                                     command=self._show_calendar_popup, style="Date.TButton")
        self.date_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.next_day_button = ttk.Button(date_nav_frame, text="▶", command=self._go_to_next_day, width=3)
        self.next_day_button.pack(side=tk.LEFT, padx=(5, 0))

        # --- Pomodoro Timer ---
        self.timer_frame = ttk.LabelFrame(left_frame, text="포모도로 타이머", padding="10")
        self.timer_frame.pack(fill=tk.X, pady=5)
        self.time_label = ttk.Label(self.timer_frame, style="Timer.TLabel")
        self.time_label.pack(pady=5)
        control_frame = ttk.Frame(self.timer_frame)
        control_frame.pack()
        self.start_pause_button = ttk.Button(control_frame, text="", command=self._toggle_pomodoro_state)
        self.start_pause_button.pack(side=tk.LEFT, padx=5)
        self.reset_button = ttk.Button(control_frame, text="리셋", command=self._reset_pomodoro)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # --- Task Management ---
        self.task_manager_frame = ttk.LabelFrame(left_frame, text="작업 관리", padding="10")
        self.task_manager_frame.pack(fill=tk.BOTH, pady=5, expand=True)
        
        add_task_frame = ttk.Frame(self.task_manager_frame)
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

        self.add_task_button = ttk.Button(add_task_frame, text="작업 추가", command=self._add_task)
        self.add_task_button.pack(pady=5)

        self.task_list_frame = ttk.Frame(self.task_manager_frame)
        self.task_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # --- Stats ---
        self.stats_frame = ttk.LabelFrame(left_frame, text="통계", padding="10")
        self.stats_frame.pack(fill=tk.X, pady=5)
        self.stats_labels = {k: ttk.Label(self.stats_frame, text="") for k in ["completed", "success_rate", "focus_time", "task_completion"]}
        for label in self.stats_labels.values(): label.pack(anchor="w")
        analytics_button = ttk.Button(self.stats_frame, text="통계 분석 보기", command=self._open_analytics_window)
        analytics_button.pack(pady=5)

    def _create_right_pane_widgets(self, parent):
        container = ttk.Frame(parent)
        container.pack(expand=True, fill=tk.BOTH)
        self.calendar_canvas = tk.Canvas(container, bg='white')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.calendar_canvas.yview)
        self.calendar_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.calendar_canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def _go_to_previous_day(self):
        self.selected_date -= timedelta(days=1)
        self._update_date_view()

    def _go_to_next_day(self):
        if self.selected_date < datetime.now().date():
            self.selected_date += timedelta(days=1)
            self._update_date_view()
        else:
            messagebox.showinfo("알림", "미래 날짜로는 이동할 수 없습니다.")

    def _show_calendar_popup(self):
        """달력 팝업을 표시하여 날짜를 선택할 수 있게 합니다."""
        popup = tk.Toplevel(self.root)
        popup.title("날짜 선택")
        popup.geometry("300x250")
        popup.transient(self.root)
        popup.grab_set()
        
        cal = Calendar(popup, selectmode='day', date_pattern='y-mm-dd',
                      year=self.selected_date.year, month=self.selected_date.month, day=self.selected_date.day)
        cal.pack(pady=20)
        
        def on_date_select():
            selected = cal.get_date()
            try:
                new_date = datetime.strptime(selected, '%Y-%m-%d').date()
                if new_date <= datetime.now().date():
                    self.selected_date = new_date
                    self._update_date_view()
                    popup.destroy()
                else:
                    messagebox.showwarning("경고", "미래 날짜는 선택할 수 없습니다.")
            except ValueError:
                messagebox.showerror("오류", "날짜 형식이 올바르지 않습니다.")
        
        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="선택", command=on_date_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=popup.destroy).pack(side=tk.LEFT, padx=5)
        
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

    def _update_date_view(self):
        """Handles all UI updates when the selected date changes."""
        date_text = self.selected_date.strftime('%Y-%m-%d')
        is_today = (self.selected_date == datetime.now().date())

        if is_today:
            date_text += " (오늘)"
            self.displayed_stats = self.today_stats
            self.stats_frame.config(text="통계 (오늘)")
        else:
            self.stats_frame.config(text=f"통계 ({self.selected_date.strftime('%Y-%m-%d')})")
        
        self.date_button.config(text=date_text)
        
        self.next_day_button.config(state=tk.NORMAL if not is_today else tk.DISABLED)
        self.add_task_button.config(state=tk.NORMAL if is_today else tk.DISABLED)
        
        self._load_data_for_selected_date()

    def _open_analytics_window(self):
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showerror("라이브러리 오류", "통계 그래프를 표시하려면 Matplotlib와 Pandas가 필요합니다.\n\n터미널에서 아래 명령어를 실행해주세요:\npip install matplotlib pandas")
            return
        analytics_win = tk.Toplevel(self.root)
        analytics_win.title("Analytics")
        analytics_win.geometry("800x600")
        graph_frame = ttk.Frame(analytics_win)
        graph_frame.pack(expand=True, fill=tk.BOTH, side=tk.BOTTOM)
        button_frame = ttk.Frame(analytics_win, padding=5)
        button_frame.pack(fill=tk.X, side=tk.TOP)
        btn1 = ttk.Button(button_frame, text="주간 집중량 추이", command=lambda: self._plot_weekly_focus(graph_frame))
        btn1.pack(side=tk.LEFT, padx=5)
        btn2 = ttk.Button(button_frame, text="시간대별 생산성", command=lambda: self._plot_hourly_productivity(graph_frame))
        btn2.pack(side=tk.LEFT, padx=5)
        btn3 = ttk.Button(button_frame, text="작업 상태 비율", command=lambda: self._plot_task_status_pie(graph_frame))
        btn3.pack(side=tk.LEFT, padx=5)
        self._plot_weekly_focus(graph_frame)

    def _clear_graph_frame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def _plot_weekly_focus(self, frame):
        self._clear_graph_frame(frame)
        conn = sqlite3.connect(self.db_path)
        today = datetime.now().date()
        start_date = today - timedelta(days=6)
        query = f"SELECT date, total_focus_seconds FROM daily_summary WHERE date BETWEEN '{start_date}' AND '{today}'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            ttk.Label(frame, text="표시할 데이터가 없습니다.").pack()
            return
        df['date'] = pd.to_datetime(df['date'])
        df['hours'] = df['total_focus_seconds'] / 3600
        df.set_index('date', inplace=True)
        fig, ax = plt.subplots(figsize=(8, 5))
        df['hours'].plot(kind='bar', ax=ax, color='#a1c4fd')
        ax.set_title('Weekly Focus Time (Hours)')
        ax.set_xlabel('Date')
        ax.set_ylabel('Focus Time (Hours)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def _plot_hourly_productivity(self, frame):
        self._clear_graph_frame(frame)
        conn = sqlite3.connect(self.db_path)
        query = "SELECT start_time, end_time FROM tasks WHERE status IN ('on-time', 'delayed')"
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            ttk.Label(frame, text="표시할 데이터가 없습니다.").pack()
            return
        hourly_focus = collections.defaultdict(float)
        for _, row in df.iterrows():
            start = datetime.strptime(row['start_time'], '%H:%M:%S').hour
            end = datetime.strptime(row['end_time'], '%H:%M:%S').hour
            for hour in range(start, end + 1):
                hourly_focus[hour] += 1
        if not hourly_focus:
            ttk.Label(frame, text="표시할 데이터가 없습니다.").pack()
            return
        s = pd.Series(hourly_focus).sort_index()
        fig, ax = plt.subplots(figsize=(8, 5))
        s.plot(kind='bar', ax=ax, color='#f9e2af')
        ax.set_title('Hourly Productivity (Completed Tasks)')
        ax.set_xlabel('Hour')
        ax.set_ylabel('Number of Tasks')
        plt.xticks(rotation=0)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def _plot_task_status_pie(self, frame):
        self._clear_graph_frame(frame)
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT status FROM tasks WHERE task_date = '{self.selected_date.strftime('%Y-%m-%d')}'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            ttk.Label(frame, text="표시할 데이터가 없습니다.").pack()
            return
        status_counts = df['status'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, colors=['#a6e3a1', '#f9e2af', '#f38ba8', '#a1c4fd'])
        ax.axis('equal')
        ax.set_title(f'{self.selected_date.strftime("%Y-%m-%d")} Task Status')
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

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
        for task_id, task in self.displayed_tasks_data.items(): # Use displayed_tasks_data
            layout = layouts.get(task_id)
            if not layout: continue
            start_y = self._time_to_y(task['start_time'])
            end_y = self._time_to_y(task['end_time'])
            total_width = self.calendar_canvas.winfo_width() - 70
            if total_width < 100: total_width = 330
            col_width = total_width / layout['total_cols']
            x0 = 60 + layout['col'] * col_width
            x1 = x0 + col_width - 2
            color_map = {'pending': "#a1c4fd", 'on-time': "#a6e3a1", 'delayed': "#f9e2af", 'failed': "#f38ba8"}
            color = color_map.get(task['status'], "#dcdcdc")
            self.calendar_canvas.create_rectangle(x0, start_y, x1, end_y, fill=color, outline="#6699ff", tags="task")
            self.calendar_canvas.create_text(x0 + 5, start_y + 5, text=task['name'], anchor=tk.NW, tags="task", width=int(col_width-10))

    def _calculate_task_layouts(self):
        layouts = {}
        sorted_tasks = sorted(self.displayed_tasks_data.items(), key=lambda item: item[1]['start_time']) # Use displayed_tasks_data
        for i in range(len(sorted_tasks)):
            task_id, task = sorted_tasks[i]
            collisions = []
            for j in range(i):
                prev_task_id, prev_task = sorted_tasks[j]
                if task['start_time'] < prev_task['end_time'] and task['end_time'] > prev_task['start_time']:
                    collisions.append(layouts[prev_task_id])
            col = 0
            while any(c['col'] == col for c in collisions):
                col += 1
            layouts[task_id] = {'col': col, 'total_cols': 1}
        for task_id, layout in layouts.items():
            task = self.displayed_tasks_data[task_id] # Use displayed_tasks_data
            overlapping_cols = {layout['col']}
            for other_id, other_layout in layouts.items():
                if task_id == other_id: continue
                other_task = self.displayed_tasks_data[other_id] # Use displayed_tasks_data
                if task['start_time'] < other_task['end_time'] and task['end_time'] > other_task['start_time']:
                    overlapping_cols.add(other_layout['col'])
            layout['total_cols'] = max(layout['total_cols'], len(overlapping_cols))
        return layouts

    def _time_to_y(self, t):
        return (t.hour - self.cal_start_hour + t.minute / 60) * self.hour_height

    def _update_current_time_indicator(self):
        self.calendar_canvas.delete("time_indicator")
        if self.selected_date == datetime.now().date():
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
        
        # Add task to today_tasks
        task_id = self.next_task_id
        self.next_task_id += 1
        self.today_tasks[task_id] = { # Add to today_tasks
            "name": name, "start_time": start_t, "end_time": end_t,
            "is_complete": tk.BooleanVar(value=False), "status": "pending", "delay_info": None, "widgets": {}
        }
        
        # If viewing today, update UI directly
        if self.selected_date == datetime.now().date():
            self._create_task_list_item(task_id) # Create UI for the new task
            self._draw_tasks_on_calendar()
            self._update_stats_display()
        self.task_name_entry.delete(0, tk.END)

    def _create_task_list_item(self, task_id):
        # This function now takes task_id and gets task data from displayed_tasks_data
        task = self.displayed_tasks_data.get(task_id) # Get task from displayed_tasks_data
        if not task: return
        
        task_frame = ttk.Frame(self.task_list_frame)
        task_frame.pack(fill=tk.X, pady=2)
        cb = ttk.Checkbutton(task_frame, var=task['is_complete'], command=lambda i=task_id: self._on_task_complete_toggle(i))
        cb.pack(side=tk.LEFT)
        label = ttk.Label(task_frame, text="")
        label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        delete_btn = ttk.Button(task_frame, text="삭제", command=lambda i=task_id: self._delete_task(i))
        delete_btn.pack(side=tk.RIGHT)
        task['widgets'] = {'frame': task_frame, 'label': label, 'checkbox': cb, 'delete_btn': delete_btn}
        is_today = (self.selected_date == datetime.now().date())
        cb.config(state=tk.NORMAL if is_today else tk.DISABLED)
        delete_btn.config(state=tk.NORMAL if is_today else tk.DISABLED)
        self._update_task_list_item_display(task_id)

    def _on_task_complete_toggle(self, task_id):
        # This function should modify today_tasks if viewing today
        if self.selected_date == datetime.now().date():
            task = self.today_tasks[task_id] # Modify today_tasks
            is_now_complete = task['is_complete'].get()
            if is_now_complete:
                now_dt = datetime.now()
                end_dt = datetime.combine(self.selected_date, task['end_time'])
                start_dt = datetime.combine(self.selected_date, task['start_time'])
                scheduled_duration = end_dt - start_dt
                # NEW CHECK: Handle zero or negative scheduled_duration
                if scheduled_duration.total_seconds() <= 0:
                    task['status'] = 'failed' # Mark as failed if duration is invalid
                    task['delay_info'] = "Invalid duration"
                elif now_dt <= end_dt:
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
        else:
            messagebox.showwarning("경고", "과거 날짜의 작업은 수정할 수 없습니다.")

    def _delete_task(self, task_id):
        # This function should modify today_tasks if viewing today
        if self.selected_date == datetime.now().date():
            task = self.today_tasks.get(task_id) # Get from today_tasks
            if task and messagebox.askyesno("Delete Task", f"Delete '{task['name']}'?"):
                task['widgets']['frame'].destroy()
                del self.today_tasks[task_id] # Delete from today_tasks
                self._draw_tasks_on_calendar()
                self._update_stats_display()
        else:
            messagebox.showwarning("경고", "과거 날짜의 작업은 삭제할 수 없습니다.")

    def _update_task_list_item_display(self, task_id):
        # This function now gets task data from displayed_tasks_data
        task = self.displayed_tasks_data.get(task_id) # Get task from displayed_tasks_data
        if not task: return
        
        now = datetime.now()
        remaining_text = ""
        is_today = (self.selected_date == datetime.now().date())
        
        if is_today and not task['is_complete'].get():
            task_start = datetime.combine(self.selected_date, task['start_time'])
            task_end = datetime.combine(self.selected_date, task['end_time'])
            
            if task_start <= now <= task_end:
                remaining_delta = task_end - now
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
            if self.pomodoro_state == 'work':
                self.today_stats['total_focus_seconds'] += 1
            if self.seconds_left < 0:
                self._handle_session_end()
        elif self.pomodoro_state == 'paused':
            self.pause_seconds_left -= 1
            if self.pause_seconds_left < 0:
                if self.paused_from_state == 'work':
                    self.today_stats['failure'] += 1
                self._reset_pomodoro()
        
        if self.selected_date == datetime.now().date():
            self._check_and_update_task_statuses()
            for task_id in list(self.displayed_tasks_data.keys()): # Use displayed_tasks_data
                if task_id in self.displayed_tasks_data: # Use displayed_tasks_data
                     self._update_task_list_item_display(task_id)
            self._update_stats_display()
        
        self._update_timer_display()
        self._update_current_time_indicator()
        self._timer_id = self.root.after(1000, self._update_clocks)

    def _handle_day_change(self):
        # This function is no longer called from _update_clocks.
        # It's kept for potential future use if day rollover logic is re-introduced.
        self._save_data()
        self.selected_date = datetime.now().date()
        self.today_stats = collections.defaultdict(int)
        self._load_today_stats()
        self.today_tasks = collections.OrderedDict() # Clear today_tasks on day change
        self._load_today_tasks() # Load new day's tasks
        self._update_date_view()

    def _check_and_update_task_statuses(self):
        now_dt = datetime.now()
        for task_id, task in list(self.displayed_tasks_data.items()): # Use displayed_tasks_data
            if task['is_complete'].get():
                continue
            end_dt = datetime.combine(self.selected_date, task['end_time'])
            if now_dt > end_dt:
                start_dt = datetime.combine(self.selected_date, task['start_time'])
                scheduled_duration = end_dt - start_dt
                if scheduled_duration.total_seconds() <= 0: continue
                delay = now_dt - end_dt
                delay_percentage = (delay.total_seconds() / scheduled_duration.total_seconds()) * 100
                new_status = task['status'] # Keep current status as base
                if delay_percentage > 25:
                    new_status = 'failed'
                elif task['status'] != 'failed': # Only set to delayed if not already failed
                    new_status = 'delayed'
                
                # Update status if it has changed
                if task['status'] != new_status:
                    task['status'] = new_status
                    self._draw_tasks_on_calendar() # Update calendar on status change
                
                # Update delay_info if status is delayed
                if new_status == 'delayed':
                    task['delay_info'] = f"{delay_percentage:.1f}% 지연"
                else: # Clear delay_info if not delayed
                    task['delay_info'] = None
                
                # Always update display for the task if its status or delay_info might have changed
                self._update_task_list_item_display(task_id)

    def _toggle_pomodoro_state(self):
        if self.pomodoro_state in ['work', 'break']:
            self.paused_from_state = self.pomodoro_state
            self.pomodoro_state = 'paused'
            self.pause_seconds_left = self.pause_duration
        elif self.pomodoro_state == 'paused':
            self.pomodoro_state = self.paused_from_state
            self.paused_from_state = None
        elif self.pomodoro_state == 'stopped':
            is_starting_break = (self.start_pause_button.cget('text') == "휴식 시작")
            if is_starting_break:
                self.pomodoro_state = 'break'
                self.seconds_left = self.break_duration
            else:
                self.pomodoro_state = 'work'
                self.seconds_left = self.work_duration
        self._update_pomodoro_button()
        self._update_timer_display()

    def _reset_pomodoro(self):
        if self.pomodoro_state == 'work' or (self.pomodoro_state == 'paused' and self.paused_from_state == 'work'):
            if self.seconds_left < self.work_duration:
                self.today_stats['failure'] += 1
        self.pomodoro_state = 'stopped'
        self.paused_from_state = None
        self.seconds_left = self.work_duration
        self._update_pomodoro_button()
        self._update_timer_display()
        if self.selected_date == datetime.now().date():
            self._update_stats_display()

    def _handle_session_end(self):
        self.root.bell()
        if self.pomodoro_state == 'work':
            self.today_stats['success'] += 1
            self.today_stats['completed_pomodoros'] += 1
        self.pomodoro_state = 'stopped'
        self._update_pomodoro_button()
        if self.selected_date == datetime.now().date():
            self._update_stats_display()

    def _update_timer_display(self):
        if self.pomodoro_state == 'paused':
            mins, secs = divmod(self.pause_seconds_left, 60)
            self.time_label.config(text=f"{mins:02d}:{secs:02d}", style="Paused.Timer.TLabel")
        else:
            mins, secs = divmod(self.seconds_left, 60)
            self.time_label.config(text=f"{mins:02d}:{secs:02d}", style="Timer.TLabel")

    def _update_pomodoro_button(self):
        if self.pomodoro_state == 'stopped':
            prev_session_was_work = (self.seconds_left < 1)
            if prev_session_was_work:
                 self.start_pause_button.config(text="휴식 시작")
                 self.seconds_left = self.break_duration
            else:
                 self.start_pause_button.config(text="집중 시작")
                 self.seconds_left = self.work_duration
            self._update_timer_display()
        elif self.pomodoro_state in ['work', 'break']:
            self.start_pause_button.config(text="일시 정지")
        elif self.pomodoro_state == 'paused':
            self.start_pause_button.config(text="계속하기")

    def _update_stats_display(self):
        s = self.displayed_stats
        total_sessions = s.get('success', 0) + s.get('failure', 0)
        success_rate = (s.get('success', 0) / total_sessions * 100) if total_sessions > 0 else 0
        total_focus_seconds = s.get('total_focus_seconds', 0)
        h, rem = divmod(total_focus_seconds, 3600)
        m, s_rem = divmod(rem, 60)
        total_focus_time_str = f"{int(h):02d}:{int(m):02d}:{int(s_rem):02d}"
        
        total_tasks = len(self.displayed_tasks_data) # Use displayed_tasks_data
        weighted_score = 0
        for task in self.displayed_tasks_data.values(): # Use displayed_tasks_data
            if task['status'] == 'on-time':
                weighted_score += 1
            elif task['status'] == 'delayed':
                weighted_score += 0.5
        task_completion_rate = (weighted_score / total_tasks * 100) if total_tasks > 0 else 0

        self.stats_labels['completed'].config(text=f"완료한 뽀모도로: {s.get('completed_pomodoros', 0)}회")
        self.stats_labels['success_rate'].config(text=f"뽀모도로 성공률: {success_rate:.1f}% ({s.get('success',0)}/{total_sessions})")
        self.stats_labels['focus_time'].config(text=f"총 집중 시간: {total_focus_time_str}")
        self.stats_labels['task_completion'].config(text=f"작업 달성도: {task_completion_rate:.1f}%")

    def _start_timer(self):
        if not self._timer_id:
            self._update_clocks()

    def _quit_app(self):
        self._save_data()
        if messagebox.askokcancel("종료", "정말로 종료하시겠습니까?"):
            if self._timer_id: self.root.after_cancel(self._timer_id)
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroPlannerApp(root)
    root.mainloop()
