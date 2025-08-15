
import tkinter as tk
from tkinter import ttk, messagebox
import collections

# MVC 패턴을 적용한 포모도로 애플리케이션 클래스
class PomodoroApp:
    def __init__(self, root):
        """
        애플리케이션 초기화
        - 모델(상태 변수) 설정
        - 뷰(GUI 위젯) 생성
        - 컨트롤러(이벤트 핸들러) 바인딩
        """
        self.root = root
        self.root.title("포모도로 타이머")
        self.root.protocol("WM_DELETE_WINDOW", self._quit_app) # 종료 시 확인

        # --- MODEL ---
        # 애플리케이션의 모든 상태를 관리합니다.
        self.pomodoro_state = 'stopped'  # 'work', 'break', 'stopped'
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60
        self.seconds_left = self.work_duration
        
        # 통계 데이터
        self.stats = {
            "success": 0,
            "failure": 0,
            "completed_pomodoros": 0,
            "total_focus_seconds": 0,
            "total_break_seconds": 0,
        }
        
        # 작업 목록
        self.tasks = collections.OrderedDict() # 추가된 순서를 기억하는 딕셔너리
        self.task_id_counter = 0

        # 타이머 ID
        self._timer_id = None

        # --- VIEW ---
        # Tkinter 위젯을 생성하고 배치합니다.
        self._create_widgets()

        # --- CONTROLLER ---
        # 초기 화면 업데이트
        self._update_timer_display()
        self._update_pomodoro_button()
        self._update_stats_display()

    def _create_widgets(self):
        """GUI 위젯을 생성하고 배치하는 뷰(View)의 역할"""
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # 1. 포모도로 타이머 섹션
        timer_frame = ttk.LabelFrame(main_frame, text="포모도로 타이머", padding="10")
        timer_frame.pack(fill=tk.X, pady=10)

        self.time_label = ttk.Label(timer_frame, text="", font=("Helvetica", 48, "bold"))
        self.time_label.pack(pady=10)

        control_frame = ttk.Frame(timer_frame)
        control_frame.pack()
        self.start_stop_button = ttk.Button(control_frame, text="", command=self._toggle_pomodoro)
        self.start_stop_button.pack(side=tk.LEFT, padx=5)
        reset_button = ttk.Button(control_frame, text="리셋", command=self._reset_pomodoro)
        reset_button.pack(side=tk.LEFT, padx=5)

        # 2. 작업 관리 섹션
        task_frame = ttk.LabelFrame(main_frame, text="작업 관리", padding="10")
        task_frame.pack(fill=tk.X, pady=10)
        
        add_task_frame = ttk.Frame(task_frame)
        add_task_frame.pack(fill=tk.X)
        
        self.task_name_entry = ttk.Entry(add_task_frame, width=30)
        self.task_name_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.task_hours_spinbox = tk.Spinbox(add_task_frame, from_=0, to=24, width=5)
        self.task_hours_spinbox.pack(side=tk.LEFT, padx=2)
        ttk.Label(add_task_frame, text="시간").pack(side=tk.LEFT)
        
        self.task_minutes_spinbox = tk.Spinbox(add_task_frame, from_=0, to=59, width=5)
        self.task_minutes_spinbox.pack(side=tk.LEFT, padx=2)
        ttk.Label(add_task_frame, text="분").pack(side=tk.LEFT)

        add_button = ttk.Button(add_task_frame, text="추가", command=self._add_task)
        add_button.pack(side=tk.LEFT, padx=5)

        self.task_list_frame = ttk.Frame(task_frame)
        self.task_list_frame.pack(fill=tk.X, pady=10)

        # 3. 통계 섹션
        stats_frame = ttk.LabelFrame(main_frame, text="통계", padding="10")
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_labels = {
            "completed": ttk.Label(stats_frame, text=""),
            "success_rate": ttk.Label(stats_frame, text=""),
            "focus_ratio": ttk.Label(stats_frame, text=""),
            "task_completion": ttk.Label(stats_frame, text=""),
        }
        for label in self.stats_labels.values():
            label.pack(anchor="w")

    # --- CONTROLLER ---
    # 이벤트에 반응하고 모델과 뷰를 업데이트하는 함수들입니다.

    def _toggle_pomodoro(self):
        """포모도로 시작/정지 버튼 핸들러"""
        if self.pomodoro_state in ['work', 'break']: # 실행 중 -> 정지
            if self.pomodoro_state == 'work':
                self.stats['failure'] += 1
            self.pomodoro_state = 'stopped'
            self._stop_timer()
        else: # 정지 상태 -> 실행
            if self.start_stop_button.cget('text') == "집중 시작":
                self.pomodoro_state = 'work'
                self.seconds_left = self.work_duration
            else: # 휴식 시작
                self.pomodoro_state = 'break'
                self.seconds_left = self.break_duration
            self._start_timer()
        
        self._update_pomodoro_button()
        self._update_stats_display()

    def _reset_pomodoro(self):
        """포모도로 리셋 핸들러"""
        self.pomodoro_state = 'stopped'
        self.seconds_left = self.work_duration
        self._stop_timer()
        self._update_timer_display()
        self._update_pomodoro_button()

    def _start_timer(self):
        """1초마다 _update_clocks 함수를 실행하는 타이머 시작"""
        if not self._timer_id:
            self._update_clocks()

    def _stop_timer(self):
        """타이머 중지"""
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None

    def _update_clocks(self):
        """모든 활성 타이머(포모도로, 작업)를 1초씩 업데이트"""
        # 포모도로 타이머 업데이트
        if self.pomodoro_state in ['work', 'break']:
            self.seconds_left -= 1
            if self.pomodoro_state == 'work':
                self.stats['total_focus_seconds'] += 1
            else:
                self.stats['total_break_seconds'] += 1
            
            if self.seconds_left < 0:
                self._handle_session_end()
        
        # 작업 타이머 업데이트
        for task in self.tasks.values():
            if task['is_running']:
                if task['remaining_seconds'] > 0:
                    task['remaining_seconds'] -= 1
                else:
                    task['is_running'] = False # 시간이 다 되면 자동 정지
        
        self._update_all_displays()
        self._timer_id = self.root.after(1000, self._update_clocks)

    def _handle_session_end(self):
        """포모도로 세션(작업/휴식) 종료 처리"""
        self.root.bell() # 시스템 알림음 재생
        if self.pomodoro_state == 'work':
            self.stats['success'] += 1
            self.stats['completed_pomodoros'] += 1
        
        self.pomodoro_state = 'stopped'
        self._stop_timer()
        self._update_pomodoro_button()
        self._update_stats_display()

    def _add_task(self):
        """새로운 작업을 모델과 뷰에 추가"""
        name = self.task_name_entry.get().strip()
        if not name:
            messagebox.showwarning("입력 오류", "작업 이름을 입력해주세요.")
            return
        
        try:
            hours = int(self.task_hours_spinbox.get())
            minutes = int(self.task_minutes_spinbox.get())
            total_seconds = (hours * 3600) + (minutes * 60)
        except ValueError:
            messagebox.showwarning("입력 오류", "시간과 분은 숫자여야 합니다.")
            return

        task_id = self.task_id_counter
        self.task_id_counter += 1
        
        # 모델에 데이터 추가
        self.tasks[task_id] = {
            "name": name,
            "total_seconds": total_seconds,
            "remaining_seconds": total_seconds,
            "is_running": False,
            "is_complete": tk.BooleanVar(value=False),
            "widgets": {}
        }
        
        # 뷰에 위젯 추가
        self._create_task_widgets(task_id)

        self.task_name_entry.delete(0, tk.END)
        self._update_stats_display()

    def _create_task_widgets(self, task_id):
        """특정 ID의 작업에 대한 위젯을 생성하고 뷰에 추가"""
        task = self.tasks[task_id]
        task_frame = ttk.Frame(self.task_list_frame)
        task_frame.pack(fill=tk.X, pady=2)

        cb = ttk.Checkbutton(task_frame, var=task['is_complete'], command=lambda i=task_id: self._on_task_complete_toggle(i))
        cb.pack(side=tk.LEFT)
        
        label = ttk.Label(task_frame, text="") # 텍스트는 업데이트 함수에서 설정
        label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        task_control_frame = ttk.Frame(task_frame)
        task_control_frame.pack(side=tk.RIGHT)

        start_stop_btn = ttk.Button(task_control_frame, text="시작", command=lambda i=task_id: self._toggle_task_running(i))
        start_stop_btn.pack(side=tk.LEFT, padx=(0, 2))

        delete_btn = ttk.Button(task_control_frame, text="삭제", command=lambda i=task_id: self._delete_task(i))
        delete_btn.pack(side=tk.LEFT)
        
        # 위젯 참조를 모델에 저장
        task['widgets'] = {'frame': task_frame, 'label': label, 'button': start_stop_btn, 'checkbox': cb}
        self._update_task_display(task_id) # 초기 표시 업데이트

    def _toggle_task_running(self, task_id):
        """작업 타이머 시작/정지 토글"""
        task = self.tasks[task_id]
        if not task['is_complete'].get():
            task['is_running'] = not task['is_running']
            if task['is_running']:
                self._start_timer()
            self._update_task_display(task_id)

    def _on_task_complete_toggle(self, task_id):
        """작업 완료 체크박스 핸들러"""
        task = self.tasks[task_id]
        if task['is_complete'].get():
            task['is_running'] = False # 완료 시 타이머 정지
        self._update_task_display(task_id)
        self._update_stats_display()

    def _delete_task(self, task_id):
        """작업 삭제 핸들러"""
        task = self.tasks.get(task_id)
        if task and messagebox.askyesno("작업 삭제", f"'{task['name']}' 작업을 삭제하시겠습니까?"):
            task['widgets']['frame'].destroy()
            del self.tasks[task_id]
            self._update_stats_display()

    def _quit_app(self):
        """애플리케이션 종료 확인"""
        if messagebox.askokcancel("종료", "정말로 종료하시겠습니까?"):
            self._stop_timer()
            self.root.destroy()

    # --- VIEW-UPDATE ---
    # 모델의 변경사항을 GUI에 반영하는 함수들입니다.

    def _update_all_displays(self):
        """모든 디스플레이를 최신 상태로 업데이트"""
        self._update_timer_display()
        self._update_task_list_display() # 새 함수 호출
        self._update_stats_display()

    def _update_timer_display(self):
        """포모도로 타이머 텍스트 업데이트"""
        mins, secs = divmod(self.seconds_left, 60)
        self.time_label.config(text=f"{mins:02d}:{secs:02d}")

    def _update_pomodoro_button(self):
        """포모도로 버튼 텍스트 상태에 따라 업데이트"""
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

    def _update_task_list_display(self):
        """모든 작업의 표시를 업데이트 (깜박임 없음)"""
        for task_id in self.tasks.keys():
            self._update_task_display(task_id)

    def _update_task_display(self, task_id):
        """특정 작업의 표시를 업데이트"""
        task = self.tasks[task_id]
        widgets = task['widgets']

        mins, secs = divmod(task['remaining_seconds'], 60)
        hours, mins = divmod(mins, 60)
        time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
        label_text = f"{task['name']} ({time_str})"
        widgets['label'].config(text=label_text)

        style = "Completed.TLabel" if task['is_complete'].get() else "TLabel"
        widgets['label'].config(style=style)
        
        widgets['button'].config(text="정지" if task['is_running'] else "시작")
        self.root.style = ttk.Style()
        self.root.style.configure("Completed.TLabel", font=('Helvetica', 10, 'overstrike'))

    def _update_stats_display(self):
        """통계 대시보드 텍스트 업데이트"""
        s = self.stats
        total_sessions = s['success'] + s['failure']
        success_rate = (s['success'] / total_sessions * 100) if total_sessions > 0 else 0
        
        total_focus = s['total_focus_seconds']
        total_break = s['total_break_seconds']
        total_time = total_focus + total_break
        
        if total_time == 0:
            focus_ratio_text = "N/A"
        else:
            focus_ratio = (total_focus / total_time * 100)
            focus_ratio_text = f"{focus_ratio:.1f}%"
        
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t['is_complete'].get())
        task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        self.stats_labels['completed'].config(text=f"완료한 뽀모도로: {s['completed_pomodoros']}회")
        self.stats_labels['success_rate'].config(text=f"뽀모도로 성공률: {success_rate:.1f}% ({s['success']}/{total_sessions})")
        self.stats_labels['focus_ratio'].config(text=f"집중도: {focus_ratio_text}")
        self.stats_labels['task_completion'].config(text=f"작업 완료율: {task_completion_rate:.1f}% ({completed_tasks}/{total_tasks})")


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
