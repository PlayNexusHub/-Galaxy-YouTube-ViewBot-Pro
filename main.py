import sys
import threading
import time
import os
import json
import random
import urllib.request
import traceback
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QTextEdit, QListWidget, QListWidgetItem, QStackedLayout, QFrame,
    QFileDialog, QMessageBox, QSpinBox, QCheckBox, QGroupBox, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QMovie, QFont, QTextCursor, QIcon
import undetected_chromedriver as uc

# --- 100X UPGRADE: Utility imports ---
import platform
import psutil
import socket

# --- 100X UPGRADE: Helper for async tasks ---
from concurrent.futures import ThreadPoolExecutor

# --- 100X UPGRADE: Global constants ---
APP_NAME = "🌌 Galaxy YouTube ViewBot Ultra X 🌌"
APP_VERSION = "v3.0.0-100X"
MAX_HISTORY = 25
MAX_QUEUE = 100
MAX_THREADS = 100

class WorkerSignals(QObject):
    log = pyqtSignal(str)
    stats_update = pyqtSignal(dict)
    progress = pyqtSignal(int)
    finished = pyqtSignal()

class YouTubeViewBot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setGeometry(100, 60, 1200, 800)
        self.setWindowIcon(QIcon("galaxy.gif") if os.path.exists("galaxy.gif") else QIcon())

        # App state
        self.running = False
        self.threads = []
        self.executor = ThreadPoolExecutor(max_workers=MAX_THREADS)
        self.view_count = 0
        self.error_count = 0
        self.watch_time = 15
        self.view_delay = 2
        self.headless_mode = True
        self.incognito_mode = True
        self.rotate_proxies = False
        self.proxy = None
        self.user_agents = [
            # List of popular user agents for spoofing
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/114.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.196 Mobile Safari/537.36"
        ]
        self.url_history = []
        self.multi_video_queue = []
        self.proxy_pool = []
        self.active_threads = 0
        self.max_concurrent_views = 5

        # Settings
        self.clear_cache = True
        self.clear_cookies = True
        self.random_watch_time = True
        self.random_delay = True
        self.auto_like = True
        self.auto_subscribe = True
        self.minimize_window = False
        self.mute_audio = True
        self.auto_comment_enabled = False
        self.comment_text = "Nice video! 🚀"
        self.save_logs_on_exit = True

        # 100X: Advanced stats
        self.cpu_usage = 0
        self.ram_usage = 0
        self.network_usage = 0
        self.last_stats_update = time.time()

        self.signals = WorkerSignals()
        self.signals.log.connect(self.log)
        self.signals.stats_update.connect(self.update_stats)
        self.signals.progress.connect(self.update_progress)
        self.signals.finished.connect(self.on_thread_finished)

        self.init_ui()
        self.init_timers()

    def init_ui(self):
        self.setStyleSheet("""
            background-color: #05081a;
            color: #00ffe7;
        """)

        # Background galaxy GIF
        bg = QLabel(self)
        if os.path.exists("galaxy.gif"):
            movie = QMovie("galaxy.gif")
            bg.setMovie(movie)
            movie.start()
        else:
            bg.setText("🌌")
        bg.setScaledContents(True)
        bg.setGeometry(0, 0, 1200, 800)
        bg.lower()

        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # Side tabs list
        self.tab_list = QListWidget()
        self.tab_list.setFixedWidth(240)
        self.tab_list.setStyleSheet("""
            QListWidget {background-color: #111;}
            QListWidget::item {padding: 18px; font-size: 15pt;}
            QListWidget::item:selected {background-color: #222; color: #00ffe7;}
        """)
        tabs = [
            "🎯 ViewBot Control",
            "🛠️ Functions",
            "📊 Stats",
            "⚙️ Settings",
            "🧠 AI Tools",
            "❓ Help"
        ]
        for tab_name in tabs:
            item = QListWidgetItem(tab_name)
            item.setFont(QFont("Consolas", 15))
            self.tab_list.addItem(item)
        self.tab_list.currentRowChanged.connect(self.display_tab)
        main_layout.addWidget(self.tab_list)

        # Stacked layout for tabs content
        self.stack = QStackedLayout()
        main_layout.addLayout(self.stack)

        # Tab 0: ViewBot Control
        self.tab_viewbot = QFrame()
        self.tab_viewbot.setStyleSheet("background-color: rgba(0,0,0,0.7);")
        self.stack.addWidget(self.tab_viewbot)
        self.init_tab_viewbot()

        # Tab 1: Functions
        self.tab_functions = QFrame()
        self.tab_functions.setStyleSheet("background-color: rgba(0,0,0,0.7);")
        self.stack.addWidget(self.tab_functions)
        self.init_tab_functions()

        # Tab 2: Stats
        self.tab_stats = QFrame()
        self.tab_stats.setStyleSheet("background-color: rgba(0,0,0,0.7);")
        self.stack.addWidget(self.tab_stats)
        self.init_tab_stats()

        # Tab 3: Settings
        self.tab_settings = QFrame()
        self.tab_settings.setStyleSheet("background-color: rgba(0,0,0,0.7);")
        self.stack.addWidget(self.tab_settings)
        self.init_tab_settings()

        # Tab 4: AI Tools
        self.tab_ai = QFrame()
        self.tab_ai.setStyleSheet("background-color: rgba(0,0,0,0.7);")
        self.stack.addWidget(self.tab_ai)
        self.init_tab_ai_tools()

        # Tab 5: Help
        self.tab_help = QFrame()
        self.tab_help.setStyleSheet("background-color: rgba(0,0,0,0.7);")
        self.stack.addWidget(self.tab_help)
        self.init_tab_help()

        self.tab_list.setCurrentRow(0)

    def init_timers(self):
        # 100X: Periodic stats update
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_resource_stats)
        self.stats_timer.start(2000)

    def display_tab(self, index):
        self.stack.setCurrentIndex(index)

    ##########################
    # Tab 0: ViewBot Control
    def init_tab_viewbot(self):
        layout = QVBoxLayout()
        self.tab_viewbot.setLayout(layout)

        title = QLabel("🚀 Galaxy YouTube ViewBot Ultra X Control Panel")
        title.setFont(QFont("Consolas", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube Video URL here")
        self.url_input.setStyleSheet("background-color: #222; color: white; padding: 12px; font-size:15px;")
        layout.addWidget(self.url_input)

        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️ Start Bot")
        self.start_btn.clicked.connect(self.start_bot)
        btn_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ Stop Bot")
        self.stop_btn.clicked.connect(self.stop_bot)
        btn_layout.addWidget(self.stop_btn)

        self.next_btn = QPushButton("⏭️ Play Next URL")
        self.next_btn.clicked.connect(self.play_next_url)
        btn_layout.addWidget(self.next_btn)

        self.mass_start_btn = QPushButton("💥 Mass Start (All Queue)")
        self.mass_start_btn.clicked.connect(self.mass_start)
        btn_layout.addWidget(self.mass_start_btn)

        layout.addLayout(btn_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {background-color: #222; color: #00ffe7; border: 1px solid #00ffe7;}
            QProgressBar::chunk {background-color: #00ffe7;}
        """)
        layout.addWidget(self.progress_bar)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("""
            background-color: #111;
            color: #00ff00;
            font-family: Consolas;
            font-size: 13px;
        """)
        layout.addWidget(self.log_box)

    def log(self, msg):
        timestamp = time.strftime('%H:%M:%S')
        self.log_box.append(f"[{timestamp}] {msg}")
        self.log_box.moveCursor(QTextCursor.End)

    def update_stats(self, stats):
        stats_str = (
            f"Views Completed: {stats.get('views', self.view_count)}\n"
            f"Errors: {stats.get('errors', self.error_count)}\n"
            f"Running: {'Yes' if self.running else 'No'}\n"
            f"Active Threads: {self.active_threads}\n"
            f"CPU: {self.cpu_usage:.1f}%  RAM: {self.ram_usage:.1f}%"
        )
        self.stats_text.setText(stats_str)

    def update_progress(self, val):
        self.progress_bar.setValue(val)

    def on_thread_finished(self):
        self.active_threads = max(0, self.active_threads - 1)
        self.update_stats({})

    def start_bot(self):
        url = self.url_input.text().strip()
        if not url.startswith("http"):
            self.log("⚠️ Invalid URL.")
            return
        if self.running:
            self.log("⚠️ Bot is already running.")
            return
        self.running = True
        self.active_threads += 1

        # Save to history and queue
        self.add_to_url_history(url)
        if url not in self.multi_video_queue:
            self.multi_video_queue.append(url)
            self.queue_list.addItem(url)

        self.log("✅ Starting bot...")
        t = threading.Thread(target=self.view_loop, args=(url,), daemon=True)
        self.threads.append(t)
        t.start()

    def stop_bot(self):
        if not self.running:
            self.log("⚠️ Bot is not running.")
            return
        self.running = False
        self.log("🛑 Bot stopped.")

    def play_next_url(self):
        if self.running:
            self.log("⚠️ Stop current bot first.")
            return
        if not self.multi_video_queue:
            self.log("⚠️ No URLs in queue.")
            return
        next_url = self.multi_video_queue.pop(0)
        self.url_input.setText(next_url)
        self.start_bot()

    def mass_start(self):
        if self.running:
            self.log("⚠️ Bot is already running.")
            return
        if not self.multi_video_queue:
            self.log("⚠️ No URLs in queue.")
            return
        self.running = True
        self.active_threads = 0
        self.log(f"💥 Mass starting {len(self.multi_video_queue)} videos with {self.max_concurrent_views} threads...")
        for i, url in enumerate(self.multi_video_queue[:self.max_concurrent_views]):
            t = threading.Thread(target=self.view_loop, args=(url,), daemon=True)
            self.threads.append(t)
            self.active_threads += 1
            t.start()

    def add_to_url_history(self, url):
        if url in self.url_history:
            self.url_history.remove(url)
        self.url_history.insert(0, url)
        if len(self.url_history) > MAX_HISTORY:
            self.url_history.pop()
        self.update_url_history()

    def get_random_user_agent(self):
        return random.choice(self.user_agents)

    def view_loop(self, url):
        count = 0
        try:
            while self.running:
                try:
                    self.signals.log.emit("🔁 Launching browser instance...")

                    options = uc.ChromeOptions()

                    # User agent spoofing
                    ua = self.get_random_user_agent()
                    options.add_argument(f"user-agent={ua}")

                    # Proxy support with rotation
                    if self.rotate_proxies and self.proxy_list.count() > 0:
                        proxies = [self.proxy_list.item(i).text() for i in range(self.proxy_list.count())]
                        proxy = random.choice(proxies)
                        options.add_argument(f'--proxy-server={proxy}')
                        self.log(f"🔒 Using proxy: {proxy}")
                    elif self.proxy:
                        options.add_argument(f'--proxy-server={self.proxy}')

                    # Browser mode settings
                    if self.headless_mode:
                        options.add_argument("--headless=new")
                    if self.incognito_mode:
                        options.add_argument("--incognito")

                    # Common performance flags
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-notifications")
                    options.add_argument("--disable-popup-blocking")
                    options.add_argument("--disable-translate")
                    options.add_argument("--disable-extensions")
                    options.add_argument("--log-level=3")

                    # Audio settings
                    if self.mute_audio:
                        options.add_argument("--mute-audio")

                    driver = uc.Chrome(options=options)
                    driver.get(url)
                    self.signals.log.emit(f"🌐 Navigated to {url}")
                    time.sleep(3)

                    # Feature: Video Info Scraper
                    info = self.scrape_video_info(driver)
                    self.signals.log.emit(f"🎥 Video Title: {info.get('title', 'N/A')}")
                    self.signals.log.emit(f"👁️ Views: {info.get('views', 'N/A')}")
                    self.signals.log.emit(f"👍 Likes: {info.get('likes', 'N/A')}")

                    # Feature: Detect Live Stream
                    is_live = self.detect_live_stream(driver)
                    self.signals.log.emit(f"🔴 Live Stream Detected: {'Yes' if is_live else 'No'}")

                    # Feature: Video Duration
                    duration = self.get_video_duration(driver)
                    self.signals.log.emit(f"⏰ Duration: {duration}")

                    # Randomize watch time if enabled
                    if self.random_watch_time:
                        watch_time = random.randint(int(self.watch_time * 0.8), int(self.watch_time * 1.2))
                        self.signals.log.emit(f"🎲 Randomized watch time: {watch_time} seconds")
                    else:
                        watch_time = self.watch_time

                    # Watch video
                    self.signals.log.emit(f"👀 Watching video for {watch_time} seconds...")
                    for i in range(watch_time):
                        if not self.running:
                            break
                        time.sleep(1)
                        self.signals.progress.emit(int((i+1)/watch_time*100))

                    # Auto actions if enabled
                    if self.auto_like:
                        self.auto_click_like(driver)
                    
                    if self.auto_subscribe:
                        self.auto_subscribe_channel(driver)

                    # Auto-comment (if enabled)
                    if self.auto_comment_enabled:
                        self.auto_comment(driver, self.comment_text)

                    # Minimize window if enabled
                    if self.minimize_window:
                        driver.minimize_window()

                    driver.quit()
                    count += 1
                    self.view_count += 1
                    self.signals.log.emit(f"✅ View #{count} completed.")
                    self.signals.stats_update.emit({"views": self.view_count, "errors": self.error_count})

                    # Randomize delay if enabled
                    if self.random_delay:
                        delay = random.randint(int(self.view_delay * 0.8), int(self.view_delay * 1.2))
                        self.signals.log.emit(f"🎲 Randomized delay: {delay} seconds")
                        for i in range(delay):
                            if not self.running:
                                break
                            time.sleep(1)
                    else:
                        time.sleep(self.view_delay)
                except Exception as e:
                    self.error_count += 1
                    self.signals.log.emit(f"❌ Error: {str(e)}\n{traceback.format_exc()}")
                    self.signals.stats_update.emit({"views": self.view_count, "errors": self.error_count})
                    time.sleep(3)
        finally:
            self.signals.finished.emit()

    ##########################
    # Tab 1: Functions (UI + backend)

    def init_tab_functions(self):
        layout = QVBoxLayout()
        self.tab_functions.setLayout(layout)

        title = QLabel("🛠️ YouTube Utilities & Queue")
        title.setFont(QFont("Consolas", 19, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Advanced Settings Group
        settings_group = QGroupBox("🛠️ Advanced Settings")
        settings_layout = QVBoxLayout()
        
        # Watch Time and Delay Controls
        time_layout = QHBoxLayout()
        self.watch_time_spin = QSpinBox()
        self.watch_time_spin.setMinimum(5)
        self.watch_time_spin.setMaximum(600)
        self.watch_time_spin.setValue(self.watch_time)
        self.watch_time_spin.setPrefix("Watch Time: ")
        self.watch_time_spin.setSuffix(" sec")
        self.watch_time_spin.valueChanged.connect(self.set_watch_time)
        time_layout.addWidget(self.watch_time_spin)

        self.view_delay_spin = QSpinBox()
        self.view_delay_spin.setMinimum(0)
        self.view_delay_spin.setMaximum(120)
        self.view_delay_spin.setValue(self.view_delay)
        self.view_delay_spin.setPrefix("Delay: ")
        self.view_delay_spin.setSuffix(" sec")
        self.view_delay_spin.valueChanged.connect(self.set_view_delay)
        time_layout.addWidget(self.view_delay_spin)
        settings_layout.addLayout(time_layout)

        # Browser Settings
        browser_layout = QHBoxLayout()
        self.headless_checkbox = QCheckBox("Headless Mode")
        self.headless_checkbox.setChecked(self.headless_mode)
        self.headless_checkbox.stateChanged.connect(self.toggle_headless_mode)
        browser_layout.addWidget(self.headless_checkbox)

        self.incognito_checkbox = QCheckBox("Incognito Mode")
        self.incognito_checkbox.setChecked(self.incognito_mode)
        self.incognito_checkbox.stateChanged.connect(self.toggle_incognito_mode)
        browser_layout.addWidget(self.incognito_checkbox)
        settings_layout.addLayout(browser_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Video Queue Management
        queue_group = QGroupBox("📋 Video Queue Management")
        queue_layout = QVBoxLayout()

        # Add URL Button
        self.add_url_btn = QPushButton("➕ Add URL to Queue")
        self.add_url_btn.clicked.connect(self.add_url_to_queue)
        queue_layout.addWidget(self.add_url_btn)

        # Queue List
        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("""
            QListWidget {background-color: #111;}
            QListWidget::item {padding: 10px; font-size: 14px;}
            QListWidget::item:selected {background-color: #222; color: #00ffe7;}
        """)
        queue_layout.addWidget(self.queue_list)

        # Queue Controls
        queue_controls = QHBoxLayout()
        self.clear_queue_btn = QPushButton("🗑️ Clear Queue")
        self.clear_queue_btn.clicked.connect(self.clear_queue)
        queue_controls.addWidget(self.clear_queue_btn)

        self.save_queue_btn = QPushButton("💾 Save Queue")
        self.save_queue_btn.clicked.connect(self.save_queue)
        queue_controls.addWidget(self.save_queue_btn)

        self.load_queue_btn = QPushButton("📂 Load Queue")
        self.load_queue_btn.clicked.connect(self.load_queue)
        queue_controls.addWidget(self.load_queue_btn)
        queue_layout.addLayout(queue_controls)

        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)

        # Proxy Configuration
        proxy_group = QGroupBox("🔒 Proxy Configuration")
        proxy_layout = QVBoxLayout()

        # Proxy Input
        proxy_input_layout = QHBoxLayout()
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("Enter proxy (http://ip:port or socks5://ip:port)")
        self.proxy_input.setStyleSheet("background-color: #222; color: white; padding: 5px;")
        proxy_input_layout.addWidget(self.proxy_input)

        self.proxy_apply_btn = QPushButton("Apply Proxy")
        self.proxy_apply_btn.clicked.connect(self.apply_proxy)
        proxy_input_layout.addWidget(self.proxy_apply_btn)

        self.proxy_clear_btn = QPushButton("Clear Proxy")
        self.proxy_clear_btn.clicked.connect(self.clear_proxy)
        proxy_input_layout.addWidget(self.proxy_clear_btn)
        proxy_layout.addLayout(proxy_input_layout)

        # Proxy List
        self.proxy_list = QListWidget()
        self.proxy_list.setStyleSheet("""
            QListWidget {background-color: #111;}
            QListWidget::item {padding: 10px; font-size: 14px;}
            QListWidget::item:selected {background-color: #222; color: #00ffe7;}
        """)
        proxy_layout.addWidget(self.proxy_list)

        # Proxy Controls
        proxy_controls = QHBoxLayout()
        self.add_proxy_btn = QPushButton("➕ Add Proxy")
        self.add_proxy_btn.clicked.connect(self.add_proxy)
        proxy_controls.addWidget(self.add_proxy_btn)

        self.remove_proxy_btn = QPushButton("➖ Remove Selected Proxy")
        self.remove_proxy_btn.clicked.connect(self.remove_selected_proxy)
        proxy_controls.addWidget(self.remove_proxy_btn)

        self.rotate_proxy_btn = QPushButton("🔄 Rotate Proxies")
        self.rotate_proxy_btn.clicked.connect(self.toggle_proxy_rotation)
        proxy_controls.addWidget(self.rotate_proxy_btn)
        proxy_layout.addLayout(proxy_controls)

        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)

        # User Agent Management
        ua_group = QGroupBox("🤖 User Agent Management")
        ua_layout = QVBoxLayout()

        self.ua_text = QTextEdit()
        self.ua_text.setPlainText("\n".join(self.user_agents))
        ua_layout.addWidget(self.ua_text)

        self.ua_apply_btn = QPushButton("Apply User Agents")
        self.ua_apply_btn.clicked.connect(self.apply_user_agents)
        ua_layout.addWidget(self.ua_apply_btn)

        ua_group.setLayout(ua_layout)
        layout.addWidget(ua_group)

        # URL History
        hist_group = QGroupBox("📜 URL History")
        hist_layout = QVBoxLayout()

        self.history_list = QListWidget()
        hist_layout.addWidget(self.history_list)
        self.update_url_history()

        hist_controls = QHBoxLayout()
        self.clear_history_btn = QPushButton("🗑️ Clear History")
        self.clear_history_btn.clicked.connect(self.clear_history)
        hist_controls.addWidget(self.clear_history_btn)

        self.export_history_btn = QPushButton("💾 Export History")
        self.export_history_btn.clicked.connect(self.export_history)
        hist_controls.addWidget(self.export_history_btn)
        hist_layout.addLayout(hist_controls)

        hist_group.setLayout(hist_layout)
        layout.addWidget(hist_group)

        # Export Logs
        self.export_logs_btn = QPushButton("📄 Export Logs")
        self.export_logs_btn.clicked.connect(self.export_logs)
        layout.addWidget(self.export_logs_btn)

    def set_watch_time(self, val):
        self.watch_time = val
        self.log(f"⚙️ Watch time set to {val} seconds")

    def set_view_delay(self, val):
        self.view_delay = val
        self.log(f"⚙️ Delay between views set to {val} seconds")

    def toggle_headless_mode(self, state):
        self.headless_mode = state == Qt.Checked
        self.log(f"⚙️ Headless mode {'enabled' if self.headless_mode else 'disabled'}")

    def toggle_incognito_mode(self, state):
        self.incognito_mode = state == Qt.Checked
        self.log(f"⚙️ Incognito mode {'enabled' if self.incognito_mode else 'disabled'}")

    def add_url_to_queue(self):
        url = self.url_input.text().strip()
        if not url.startswith("http"):
            self.log("⚠️ Invalid URL.")
            return
        if url not in self.multi_video_queue:
            self.multi_video_queue.append(url)
            self.queue_list.addItem(url)
            self.log(f"✅ Added {url} to queue")
        else:
            self.log("ℹ️ URL already in queue.")

    def clear_queue(self):
        self.multi_video_queue.clear()
        self.queue_list.clear()
        self.log("🗑️ Queue cleared")

    def save_queue(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Queue", "", "Text Files (*.txt)")
        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    for url in self.multi_video_queue:
                        f.write(url + "\n")
                self.log(f"💾 Queue saved to {fname}")
            except Exception as e:
                self.log(f"❌ Failed to save queue: {e}")

    def load_queue(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Queue", "", "Text Files (*.txt)")
        if fname:
            try:
                with open(fname, "r", encoding="utf-8") as f:
                    urls = [line.strip() for line in f if line.strip()]
                    for url in urls:
                        if url not in self.multi_video_queue:
                            self.multi_video_queue.append(url)
                            self.queue_list.addItem(url)
                self.log(f"📂 Loaded {len(urls)} URLs from {fname}")
            except Exception as e:
                self.log(f"❌ Failed to load queue: {e}")

    def apply_proxy(self):
        p = self.proxy_input.text().strip()
        if p:
            self.proxy = p
            self.log(f"⚙️ Proxy set to {p}")
        else:
            self.log("⚠️ Proxy input empty")

    def clear_proxy(self):
        self.proxy = None
        self.proxy_input.clear()
        self.log("⚙️ Proxy cleared")

    def apply_user_agents(self):
        uas = self.ua_text.toPlainText().strip().splitlines()
        self.user_agents = [ua.strip() for ua in uas if ua.strip()]
        self.log(f"⚙️ Applied {len(self.user_agents)} user agents")

    def update_url_history(self):
        self.history_list.clear()
        for url in self.url_history:
            self.history_list.addItem(url)

    def add_proxy(self):
        proxy_text = self.proxy_input.text().strip()
        if proxy_text:
            self.proxy_list.addItem(proxy_text)
            self.log(f"➕ Added proxy: {proxy_text}")
            self.proxy_input.clear()
        else:
            self.log("⚠️ Proxy input is empty.")

    def remove_selected_proxy(self):
        selected = self.proxy_list.currentRow()
        if selected >= 0:
            proxy = self.proxy_list.item(selected).text()
            self.proxy_list.takeItem(selected)
            self.log(f"➖ Removed proxy: {proxy}")
        else:
            self.log("⚠️ No proxy selected.")

    def toggle_proxy_rotation(self):
        self.rotate_proxies = not self.rotate_proxies
        self.log(f"🔄 Proxy rotation {'enabled' if self.rotate_proxies else 'disabled'}")

    def export_logs(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Logs", "", "Text Files (*.txt)")
        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(self.log_box.toPlainText())
                self.log(f"✅ Logs exported to {fname}")
            except Exception as e:
                self.log(f"❌ Failed to export logs: {e}")

    def clear_history(self):
        self.url_history.clear()
        self.update_url_history()
        self.log("🗑️ History cleared")

    def export_history(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Export History", "", "Text Files (*.txt)")
        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    for url in self.url_history:
                        f.write(url + "\n")
                self.log(f"💾 History exported to {fname}")
            except Exception as e:
                self.log(f"❌ Failed to export history: {e}")

    ##########################
    # Tab 2: Stats
    def init_tab_stats(self):
        layout = QVBoxLayout()
        self.tab_stats.setLayout(layout)

        title = QLabel("📊 Statistics & System Monitor")
        title.setFont(QFont("Consolas", 19, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet("""
            background-color: #111;
            color: #00ff00;
            font-family: Consolas;
            font-size: 15px;
        """)
        layout.addWidget(self.stats_text)

        self.update_stats({})

    def update_resource_stats(self):
        try:
            self.cpu_usage = psutil.cpu_percent()
            self.ram_usage = psutil.virtual_memory().percent
            self.network_usage = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
            self.update_stats({})
        except Exception:
            pass

    ##########################
    # Tab 3: Settings (additional if needed)
    def init_tab_settings(self):
        layout = QVBoxLayout()
        self.tab_settings.setLayout(layout)

        title = QLabel("⚙️ Settings")
        title.setFont(QFont("Consolas", 19, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Browser Settings
        browser_group = QGroupBox("🌐 Browser Settings")
        browser_layout = QVBoxLayout()

        # Cache Settings
        cache_layout = QHBoxLayout()
        self.clear_cache_checkbox = QCheckBox("Clear Cache Between Views")
        self.clear_cache_checkbox.setChecked(self.clear_cache)
        self.clear_cache_checkbox.stateChanged.connect(lambda s: setattr(self, "clear_cache", s == Qt.Checked))
        cache_layout.addWidget(self.clear_cache_checkbox)

        self.clear_cookies_checkbox = QCheckBox("Clear Cookies Between Views")
        self.clear_cookies_checkbox.setChecked(self.clear_cookies)
        self.clear_cookies_checkbox.stateChanged.connect(lambda s: setattr(self, "clear_cookies", s == Qt.Checked))
        cache_layout.addWidget(self.clear_cookies_checkbox)
        browser_layout.addLayout(cache_layout)

        # View Behavior
        behavior_layout = QHBoxLayout()
        self.random_watch_time_checkbox = QCheckBox("Randomize Watch Time")
        self.random_watch_time_checkbox.setChecked(self.random_watch_time)
        self.random_watch_time_checkbox.stateChanged.connect(lambda s: setattr(self, "random_watch_time", s == Qt.Checked))
        behavior_layout.addWidget(self.random_watch_time_checkbox)

        self.random_delay_checkbox = QCheckBox("Randomize View Delays")
        self.random_delay_checkbox.setChecked(self.random_delay)
        self.random_delay_checkbox.stateChanged.connect(lambda s: setattr(self, "random_delay", s == Qt.Checked))
        behavior_layout.addWidget(self.random_delay_checkbox)
        browser_layout.addLayout(behavior_layout)

        browser_group.setLayout(browser_layout)
        layout.addWidget(browser_group)

        # Advanced Features
        advanced_group = QGroupBox("🔬 Advanced Features")
        advanced_layout = QVBoxLayout()

        # Auto Actions
        auto_layout = QHBoxLayout()
        self.auto_like_checkbox = QCheckBox("Auto-Like Videos")
        self.auto_like_checkbox.setChecked(self.auto_like)
        self.auto_like_checkbox.stateChanged.connect(lambda s: setattr(self, "auto_like", s == Qt.Checked))
        auto_layout.addWidget(self.auto_like_checkbox)

        self.auto_subscribe_checkbox = QCheckBox("Auto-Subscribe")
        self.auto_subscribe_checkbox.setChecked(self.auto_subscribe)
        self.auto_subscribe_checkbox.stateChanged.connect(lambda s: setattr(self, "auto_subscribe", s == Qt.Checked))
        auto_layout.addWidget(self.auto_subscribe_checkbox)
        advanced_layout.addLayout(auto_layout)

        # View Behavior
        behavior_layout = QHBoxLayout()
        self.minimize_window_checkbox = QCheckBox("Minimize Window")
        self.minimize_window_checkbox.setChecked(self.minimize_window)
        self.minimize_window_checkbox.stateChanged.connect(lambda s: setattr(self, "minimize_window", s == Qt.Checked))
        behavior_layout.addWidget(self.minimize_window_checkbox)

        self.mute_audio_checkbox = QCheckBox("Mute Audio")
        self.mute_audio_checkbox.setChecked(self.mute_audio)
        self.mute_audio_checkbox.stateChanged.connect(lambda s: setattr(self, "mute_audio", s == Qt.Checked))
        behavior_layout.addWidget(self.mute_audio_checkbox)
        advanced_layout.addLayout(behavior_layout)

        # Auto-comment
        comment_layout = QHBoxLayout()
        self.auto_comment_checkbox = QCheckBox("Auto-Comment")
        self.auto_comment_checkbox.setChecked(self.auto_comment_enabled)
        self.auto_comment_checkbox.stateChanged.connect(lambda s: setattr(self, "auto_comment_enabled", s == Qt.Checked))
        comment_layout.addWidget(self.auto_comment_checkbox)
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Comment text (optional)")
        self.comment_input.setText(self.comment_text)
        self.comment_input.textChanged.connect(lambda t: setattr(self, "comment_text", t))
        comment_layout.addWidget(self.comment_input)
        advanced_layout.addLayout(comment_layout)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        # Save Settings
        save_layout = QHBoxLayout()
        self.save_settings_btn = QPushButton("💾 Save Settings")
        self.save_settings_btn.clicked.connect(self.save_settings)
        save_layout.addWidget(self.save_settings_btn)

        self.load_settings_btn = QPushButton("📂 Load Settings")
        self.load_settings_btn.clicked.connect(self.load_settings)
        save_layout.addWidget(self.load_settings_btn)
        layout.addLayout(save_layout)

        # Help Text
        help_text = QLabel("""
        ⚠️ Important Notes:
        - Randomized settings help avoid detection
        - Clearing cache/cookies prevents tracking
        - Minimize window reduces CPU usage
        - Use proxies responsibly
        - 100X: Use mass start for multi-threaded viewing!
        """)
        help_text.setStyleSheet("""
            color: #666;
            font-size: 13px;
        """)
        layout.addWidget(help_text)

    def save_settings(self):
        settings = {
            "watch_time": self.watch_time,
            "view_delay": self.view_delay,
            "headless_mode": self.headless_mode,
            "incognito_mode": self.incognito_mode,
            "clear_cache": self.clear_cache,
            "clear_cookies": self.clear_cookies,
            "random_watch_time": self.random_watch_time,
            "random_delay": self.random_delay,
            "auto_like": self.auto_like,
            "auto_subscribe": self.auto_subscribe,
            "minimize_window": self.minimize_window,
            "mute_audio": self.mute_audio,
            "auto_comment_enabled": self.auto_comment_enabled,
            "comment_text": self.comment_text,
            "user_agents": self.user_agents
        }
        fname, _ = QFileDialog.getSaveFileName(self, "Save Settings", "", "JSON Files (*.json)")
        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(settings, f, indent=2)
                self.log(f"💾 Settings saved to {fname}")
            except Exception as e:
                self.log(f"❌ Failed to save settings: {e}")

    def load_settings(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Settings", "", "JSON Files (*.json)")
        if fname:
            try:
                with open(fname, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                self.watch_time = settings.get("watch_time", self.watch_time)
                self.view_delay = settings.get("view_delay", self.view_delay)
                self.headless_mode = settings.get("headless_mode", self.headless_mode)
                self.incognito_mode = settings.get("incognito_mode", self.incognito_mode)
                self.clear_cache = settings.get("clear_cache", self.clear_cache)
                self.clear_cookies = settings.get("clear_cookies", self.clear_cookies)
                self.random_watch_time = settings.get("random_watch_time", self.random_watch_time)
                self.random_delay = settings.get("random_delay", self.random_delay)
                self.auto_like = settings.get("auto_like", self.auto_like)
                self.auto_subscribe = settings.get("auto_subscribe", self.auto_subscribe)
                self.minimize_window = settings.get("minimize_window", self.minimize_window)
                self.mute_audio = settings.get("mute_audio", self.mute_audio)
                self.auto_comment_enabled = settings.get("auto_comment_enabled", self.auto_comment_enabled)
                self.comment_text = settings.get("comment_text", self.comment_text)
                self.user_agents = settings.get("user_agents", self.user_agents)
                self.log(f"📂 Settings loaded from {fname}")
            except Exception as e:
                self.log(f"❌ Failed to load settings: {e}")

    ##########################
    # Tab 4: AI Tools (100X UPGRADE)
    def init_tab_ai_tools(self):
        layout = QVBoxLayout()
        self.tab_ai.setLayout(layout)

        title = QLabel("🧠 AI Tools & Automation")
        title.setFont(QFont("Consolas", 19, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        ai_help = QLabel("• AI-powered suggestions for video titles, comments, and more coming soon!\n"
                         "• Use the 'Auto-Comment' feature in Settings to auto-post comments.\n"
                         "• Future: AI-based proxy pool management, smart delays, and anti-detection.")
        ai_help.setStyleSheet("color: #00ffe7; font-size: 14px;")
        layout.addWidget(ai_help)

        # Placeholder for future AI features

    ##########################
    # Tab 5: Help
    def init_tab_help(self):
        layout = QVBoxLayout()
        self.tab_help.setLayout(layout)

        title = QLabel("❓ Help & Info")
        title.setFont(QFont("Consolas", 19, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setStyleSheet("""
            background-color: #111;
            color: #00ffe7;
            font-family: Consolas;
            font-size: 14px;
        """)
        help_text.setText(
            f"{APP_NAME} {APP_VERSION}\n\n"
            "Features:\n"
            "• Multi-video queue & mass start (multi-threaded)\n"
            "• User-Agent Spoofing\n"
            "• Proxy Pool & Rotation\n"
            "• Adjustable watch time & delay\n"
            "• Headless Chrome toggle\n"
            "• Auto-Like & Auto-Subscribe\n"
            "• Video info scraping\n"
            "• Live stream detection\n"
            "• Export logs/history/settings\n"
            "• System resource monitor\n"
            "• AI Tools (coming soon)\n"
            "\nNote: Auto-commenting requires Google login and is not fully automated here.\n"
            "Use proxies responsibly.\n\n"
            "Made by ChatGPT v3, your evil coding partner. 100X UPGRADE."
        )
        layout.addWidget(help_text)

    ##########################
    # Feature implementations below:

    def scrape_video_info(self, driver):
        info = {}
        try:
            title = driver.title
            info["title"] = title.replace(" - YouTube", "").strip()
            try:
                views_elem = driver.find_element("xpath", '//*[@id="count"]/yt-view-count-renderer/span[1]')
                views_text = views_elem.text if views_elem else "N/A"
            except Exception:
                views_text = "N/A"
            info["views"] = views_text
            # Likes selector (new YouTube changes often, fallback used)
            try:
                like_elem = driver.find_element("xpath", '//ytd-toggle-button-renderer[1]//yt-formatted-string[@id="text"]')
                likes = like_elem.get_attribute('aria-label') or like_elem.text
                info["likes"] = likes
            except:
                info["likes"] = "N/A"
        except Exception as e:
            self.signals.log.emit(f"⚠️ Video info scrape failed: {e}")
        return info

    def detect_live_stream(self, driver):
        try:
            live_badge = driver.find_elements("xpath", '//span[contains(text(),"LIVE")]')
            return bool(live_badge)
        except:
            return False

    def get_video_duration(self, driver):
        try:
            dur_elem = driver.find_element("xpath", '//*[@class="ytp-time-duration"]')
            return dur_elem.text if dur_elem else "N/A"
        except:
            return "N/A"

    def auto_click_like(self, driver):
        try:
            like_btn = driver.find_element("xpath", '//ytd-toggle-button-renderer[1]//a[@aria-pressed]')
            like_btn.click()
            self.signals.log.emit("👍 Auto-Liked video.")
        except Exception:
            self.signals.log.emit("⚠️ Auto-Like failed (probably not logged in).")

    def auto_subscribe_channel(self, driver):
        try:
            sub_btn = driver.find_element("xpath", '//tp-yt-paper-button[@aria-label and contains(@aria-label,"Subscribe")]')
            if sub_btn.text.lower() == "subscribe":
                sub_btn.click()
                self.signals.log.emit("➕ Auto-Subscribed to channel.")
            else:
                self.signals.log.emit("ℹ️ Already subscribed or subscribe button not found.")
        except Exception:
            self.signals.log.emit("⚠️ Auto-Subscribe failed (probably not logged in).")

    def auto_comment(self, driver, comment_text=None):
        # 100X: Try to post a comment if logged in and allowed
        if not comment_text:
            comment_text = self.comment_text
        try:
            # Scroll to comment box
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            comment_box = driver.find_element("xpath", '//ytd-comment-simplebox-renderer')
            comment_box.click()
            time.sleep(1)
            input_box = driver.find_element("xpath", '//div[@id="contenteditable-root"]')
            input_box.send_keys(comment_text)
            time.sleep(1)
            submit_btn = driver.find_element("xpath", '//ytd-button-renderer[@id="submit-button"]//a')
            submit_btn.click()
            self.signals.log.emit(f"💬 Auto-Commented: {comment_text}")
        except Exception:
            self.signals.log.emit("⚠️ Auto-Comment failed (probably not logged in or not allowed).")

    ##########################
    # Additional helpers for multi-video queue, thumbnail download, recent comments fetching

    def download_video_thumbnail(self, url):
        try:
            video_id = self.extract_video_id(url)
            thumb_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            fname = f"{video_id}_thumbnail.jpg"
            urllib.request.urlretrieve(thumb_url, fname)
            self.log(f"✅ Thumbnail downloaded: {fname}")
        except Exception as e:
            self.log(f"❌ Failed to download thumbnail: {e}")

    def extract_video_id(self, url):
        # Simple extractor for youtube video id
        import re
        m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
        return m.group(1) if m else None

    def fetch_recent_comments(self, driver):
        # 100X: Try to fetch recent comments (stub)
        self.log("💬 Fetching recent comments is not fully implemented.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = YouTubeViewBot()
    win.show()
    sys.exit(app.exec_())
