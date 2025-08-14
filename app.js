document.addEventListener('DOMContentLoaded', () => {

    // --- MODEL ---
    const model = {
        pomodoro: {
            state: 'stopped', // 'work', 'break', 'stopped'
            workDuration: 25 * 60,
            breakDuration: 5 * 60,
            secondsLeft: 25 * 60,
            successCount: 0,
            failureCount: 0,
            completedCount: 0,
            totalFocusSeconds: 0,
            totalBreakSeconds: 0,
        },
        tasks: [],
        mainInterval: null,
        audio: document.getElementById('notification-sound'),
    };

    // --- VIEW ---
    const view = {
        timeDisplay: document.getElementById('time-display'),
        startStopButton: document.getElementById('start-stop-button'),
        resetButton: document.getElementById('reset-button'),
        taskList: document.getElementById('task-list'),
        taskForm: document.getElementById('add-task-form'),
        
        // Stats
        pomodoroCompletionCount: document.getElementById('pomodoro-completion-count'),
        pomodoroSuccessRate: document.getElementById('pomodoro-success-rate'),
        focusRatio: document.getElementById('focus-ratio'),
        taskCompletionRate: document.getElementById('task-completion-rate'),

        updateTimerDisplay(seconds) {
            const mins = Math.floor(seconds / 60);
            const secs = seconds % 60;
            this.timeDisplay.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        },

        updatePomodoroButton() {
            const { state } = model.pomodoro;
            if (state === 'work' || state === 'break') {
                this.startStopButton.textContent = '정지';
            } else { // stopped
                const lastState = this.startStopButton.dataset.lastState || 'break';
                this.startStopButton.textContent = lastState === 'break' ? '집중 시작' : '휴식 시작';
            }
        },

        renderTasks() {
            this.taskList.innerHTML = '';
            model.tasks.forEach(task => {
                const li = document.createElement('li');
                li.dataset.id = task.id;
                if (task.isComplete) {
                    li.classList.add('completed');
                }

                const remainingTime = new Date(task.remainingSeconds * 1000).toISOString().substr(11, 8);

                li.innerHTML = `
                    <input type="checkbox" class="task-checkbox" ${task.isComplete ? 'checked' : ''}>
                    <span class="task-name">${task.name}</span>
                    <span class="task-timer">${remainingTime}</span>
                    <div class="task-controls">
                        <button class="task-start-stop">${task.isRunning ? '정지' : '시작'}</button>
                    </div>
                `;
                this.taskList.appendChild(li);
            });
        },

        updateStats() {
            const { successCount, failureCount, completedCount, totalFocusSeconds, totalBreakSeconds } = model.pomodoro;
            const totalTasks = model.tasks.length;
            const completedTasks = model.tasks.filter(t => t.isComplete).length;

            this.pomodoroCompletionCount.textContent = `완료한 뽀모도로: ${completedCount}회`;

            const totalSessions = successCount + failureCount;
            this.pomodoroSuccessRate.textContent = `뽀모도로 성공률: ${totalSessions > 0 ? Math.round((successCount / totalSessions) * 100) + '%' : 'N/A'}`;

            const totalTime = totalFocusSeconds + totalBreakSeconds;
            this.focusRatio.textContent = `집중도: ${totalTime > 0 ? Math.round((totalFocusSeconds / totalTime) * 100) + '%' : 'N/A'}`;
            
            this.taskCompletionRate.textContent = `작업 완료율: ${totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) + '%'} (${completedTasks}/${totalTasks})`;
        },

        playNotification() {
            model.audio.currentTime = 0;
            model.audio.play();
        }
    };

    // --- CONTROLLER ---
    const controller = {
        init() {
            view.updateTimerDisplay(model.pomodoro.secondsLeft);
            view.updatePomodoroButton();
            view.updateStats();
            this.setupEventListeners();
        },

        setupEventListeners() {
            view.startStopButton.addEventListener('click', () => this.handlePomodoroStartStop());
            view.resetButton.addEventListener('click', () => this.handlePomodoroReset());
            view.taskForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAddTask();
            });
            view.taskList.addEventListener('click', (e) => {
                if (e.target.classList.contains('task-checkbox')) {
                    this.handleTaskCheckbox(e.target.closest('li').dataset.id);
                }
                if (e.target.classList.contains('task-start-stop')) {
                    this.handleTaskStartStop(e.target.closest('li').dataset.id);
                }
            });
        },

        startMainInterval() {
            if (model.mainInterval) return;
            model.mainInterval = setInterval(() => this.mainTick(), 1000);
        },

        stopMainInterval() {
            clearInterval(model.mainInterval);
            model.mainInterval = null;
        },

        mainTick() {
            let isAnyTimerRunning = false;

            // Pomodoro Timer
            if (model.pomodoro.state === 'work' || model.pomodoro.state === 'break') {
                isAnyTimerRunning = true;
                model.pomodoro.secondsLeft--;
                
                if (model.pomodoro.state === 'work') model.pomodoro.totalFocusSeconds++;
                else model.pomodoro.totalBreakSeconds++;

                if (model.pomodoro.secondsLeft < 0) {
                    this.handlePomodoroSessionEnd();
                }
            }

            // Task Timers
            model.tasks.forEach(task => {
                if (task.isRunning && !task.isComplete) {
                    isAnyTimerRunning = true;
                    if (task.remainingSeconds > 0) {
                        task.remainingSeconds--;
                    } else {
                        task.isRunning = false; // Stop timer if it reaches zero
                    }
                }
            });
            
            this.updateAllViews();

            if (!isAnyTimerRunning) {
                this.stopMainInterval();
            }
        },

        handlePomodoroStartStop() {
            const { pomodoro } = model;
            if (pomodoro.state === 'work' || pomodoro.state === 'break') { // Running -> Stop
                if (pomodoro.state === 'work') {
                    pomodoro.failureCount++;
                }
                pomodoro.state = 'stopped';
                view.startStopButton.dataset.lastState = pomodoro.state === 'work' ? 'work' : 'break';
            } else { // Stopped -> Running
                const lastState = view.startStopButton.dataset.lastState || 'break';
                if (lastState === 'break') {
                    pomodoro.state = 'work';
                    pomodoro.secondsLeft = pomodoro.workDuration;
                } else {
                    pomodoro.state = 'break';
                    pomodoro.secondsLeft = pomodoro.breakDuration;
                }
            }
            this.startMainInterval();
            this.updateAllViews();
        },

        handlePomodoroSessionEnd() {
            const { pomodoro } = model;
            if (pomodoro.state === 'work') {
                pomodoro.successCount++;
                pomodoro.completedCount++;
            }
            view.startStopButton.dataset.lastState = pomodoro.state;
            pomodoro.state = 'stopped';
            view.playNotification();
        },
        
        handlePomodoroReset() {
            model.pomodoro.state = 'stopped';
            model.pomodoro.secondsLeft = model.pomodoro.workDuration;
            view.startStopButton.dataset.lastState = 'break';
            this.updateAllViews();
        },

        handleAddTask() {
            const nameInput = document.getElementById('task-name-input');
            const hoursInput = document.getElementById('task-hours-input');
            const minutesInput = document.getElementById('task-minutes-input');
            
            const name = nameInput.value.trim();
            if (!name) return;

            const hours = parseInt(hoursInput.value) || 0;
            const minutes = parseInt(minutesInput.value) || 0;
            const totalSeconds = (hours * 3600) + (minutes * 60);

            const newTask = {
                id: Date.now().toString(),
                name,
                totalSeconds,
                remainingSeconds: totalSeconds,
                isRunning: false,
                isComplete: false,
            };
            model.tasks.push(newTask);
            
            nameInput.value = '';
            hoursInput.value = '0';
            minutesInput.value = '25';

            this.updateAllViews();
        },

        handleTaskCheckbox(taskId) {
            const task = model.tasks.find(t => t.id === taskId);
            if (task) {
                task.isComplete = !task.isComplete;
                if (task.isComplete) {
                    task.isRunning = false; // Stop timer when completed
                }
                this.updateAllViews();
            }
        },

        handleTaskStartStop(taskId) {
            const task = model.tasks.find(t => t.id === taskId);
            if (task && !task.isComplete) {
                task.isRunning = !task.isRunning;
                if (task.isRunning) {
                    this.startMainInterval();
                }
                this.updateAllViews();
            }
        },

        updateAllViews() {
            view.updateTimerDisplay(model.pomodoro.secondsLeft);
            view.updatePomodoroButton();
            view.renderTasks();
            view.updateStats();
        }
    };

    controller.init();
});
