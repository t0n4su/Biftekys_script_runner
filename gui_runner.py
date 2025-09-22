import sys
import os
import subprocess
import json
import configparser
import markdown
import shutil
import time
from datetime import datetime
from functools import partial
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QTextEdit, QSplitter,
    QFileDialog, QProgressBar, QMessageBox, QComboBox, QCheckBox,
    QGroupBox, QLineEdit, QToolBar, QStatusBar, QDialog, QDialogButtonBox
)
from PyQt6.QtGui import QIcon, QAction, QPalette, QColor, QFont
from PyQt6.QtCore import Qt, QSettings, QThread, pyqtSignal

# ---------- robust resource resolver ----------
def resource_path(rel_path: str) -> str:
    if getattr(sys, 'frozen', False):  # running as EXE
        base_dir = os.path.dirname(sys.argv[0])
    else:
        base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, rel_path.replace("/", os.sep))

# ---------- Theme Manager ----------
class ThemeManager:
    @staticmethod
    def apply_theme(app, dark_mode):
        if dark_mode:
            # Dark theme
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
            dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(35, 35, 35))
            app.setPalette(dark_palette)
            
            # Additional dark style
            dark_stylesheet = """
            QMainWindow, QWidget {
                background-color: #353535;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background: #353535;
            }
            QTabBar::tab {
                background: #444;
                color: #fff;
                padding: 8px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2a82da;
            }
            QTextEdit, QListView, QTreeView {
                background-color: #252525;
                color: #ffffff;
                border: 1px solid #444;
            }
            QPushButton {
                background-color: #555;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #2a82da;
            }
            QPushButton:disabled {
                background-color: #333;
                color: #777;
            }
            QLineEdit {
                background-color: #252525;
                color: white;
                border: 1px solid #444;
                padding: 5px;
                border-radius: 3px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: white;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
                background-color: #252525;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
                width: 10px;
            }
            QSplitter::handle {
                background-color: #444;
            }
            QSplitter::handle:hover {
                background-color: #2a82da;
            }
            QCheckBox {
                color: white;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #666;
                border-radius: 3px;
                background: #353535;
            }
            QCheckBox::indicator:checked {
                background: #2a82da;
                border: 1px solid #2a82da;
                image: url(icons/checkmark_white.svg);
            }
            QCheckBox::indicator:unchecked:hover {
                border: 1px solid #888;
            }
            """
            app.setStyleSheet(dark_stylesheet)
        else:
            # Light theme (default)
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: #f0f0f0;
            }
            QTabBar::tab {
                background: #e0e0e0;
                color: #333;
                padding: 8px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2a82da;
                color: white;
            }
            QTextEdit, QListView, QTreeView {
                background-color: white;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #2a82da;
                color: white;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #999;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 3px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #333;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
                width: 10px;
            }
            QSplitter::handle {
                background-color: #ccc;
            }
            QSplitter::handle:hover {
                background-color: #2a82da;
            }
            QCheckBox {
                color: #333;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #999;
                border-radius: 3px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #2a82da;
                border: 1px solid #2a82da;
                image: url(:/icons/checkmark_white.svg);
            }
            QCheckBox::indicator:unchecked:hover {
                border: 1px solid #666;
            }
            """)

# ---------- Script Runner Thread ----------
class ScriptRunnerThread(QThread):
    output_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, args, cwd, env):
        super().__init__()
        self.args = args
        self.cwd = cwd
        self.env = env
        self.process = None
        self.is_running = True
        
    def run(self):
        try:
            self.process = subprocess.Popen(
                self.args, 
                cwd=self.cwd, 
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=self.env,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output in real-time
            for line in iter(self.process.stdout.readline, ''):
                if not self.is_running:
                    break
                self.output_signal.emit(line)
                
            self.process.stdout.close()
            return_code = self.process.wait()
            
            if return_code == 0:
                self.finished_signal.emit(True, "Script completed successfully")
            else:
                self.finished_signal.emit(False, f"Script failed with return code {return_code}")
                
        except Exception as e:
            self.finished_signal.emit(False, f"Error running script: {str(e)}")
    
    def stop(self):
        self.is_running = False
        if self.process:
            self.process.terminate()

# ---------- Drop Area ----------
class DropArea(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("\n\n Drop input file(s) here ")
        self.setStyleSheet("QLabel { border: 2px dashed #555; font-size:16px; }")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.dropped_files = []
        self.setMinimumHeight(100)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            self.dropped_files = [url.toLocalFile() for url in event.mimeData().urls()]
            file_list = "\n".join([os.path.basename(f) for f in self.dropped_files])
            self.setText(f"Dropped files:\n{file_list}")
            event.accept()

# ---------- Script Configuration ----------
class ScriptConfig:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.config_file = os.path.join(folder_path, "script_config.ini")
        self.config = configparser.ConfigParser()
        self.load_config()
        
    def load_config(self):
        if os.path.exists(self.config_file):
            self.config.read(self.config_file, encoding='utf-8')
        else:
            # Create default config
            self.config['DEFAULT'] = {
                'input_formats': '.csv,.xlsx,.txt',
                'output_format': 'excel',
                'parameters': '{}'
            }
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    def get_input_formats(self):
        return self.config['DEFAULT'].get('input_formats', '.csv,.xlsx,.txt').split(',')
    
    def get_parameters(self):
        try:
            return json.loads(self.config['DEFAULT'].get('parameters', '{}'))
        except:
            return {}
    
    def set_parameters(self, params):
        self.config['DEFAULT']['parameters'] = json.dumps(params)
        self.save_config()

# ---------- Script Tab ----------
class ScriptTab(QWidget):
    def __init__(self, folder_path, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.script_file = self.find_script()
        self.config = ScriptConfig(folder_path)
        self.settings = QSettings("BifteKYS", "ScriptRunner")
        self.runner_thread = None
        self.output_dir = self.settings.value(f"{os.path.basename(folder_path)}/output_dir", os.path.expanduser("~"))
        self.script_name = os.path.basename(folder_path)  # Store script name for backup organization
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Script info
        info_label = QLabel(f"Script: {os.path.basename(self.script_file) if self.script_file else 'Not found'}")
        info_label.setStyleSheet("QLabel { color: #666; font-size: 12px; }")
        layout.addWidget(info_label)
        
        # Drop zone
        self.drop_area = DropArea()
        layout.addWidget(self.drop_area)
        
        # Parameters group
        self.param_widgets = {}
        self.setup_parameters_ui(layout)
        
        # Buttons row
        buttons = QHBoxLayout()
        self.choose_folder_btn = QPushButton("Choose Output Folder")
        self.choose_folder_btn.clicked.connect(self.choose_output_folder)
        self.run_button = QPushButton("Run Script")
        self.run_button.clicked.connect(self.run_script)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_script)
        self.stop_button.setEnabled(False)
        buttons.addWidget(self.choose_folder_btn)
        buttons.addWidget(self.run_button)
        buttons.addWidget(self.stop_button)
        layout.addLayout(buttons)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Splitter: console + README
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.output_box = QTextEdit(readOnly=True)
        self.output_box.setPlaceholderText("Script output will appear here...")
        splitter.addWidget(self.output_box)
        
        self.readme_box = QTextEdit(readOnly=True)
        self.readme_box.setPlaceholderText("No README found.")
        self.load_readme()
        splitter.addWidget(self.readme_box)
        
        splitter.setSizes([300, 200])
        layout.addWidget(splitter)
        
        # Update output folder label
        self.update_output_folder_label()

    def find_script(self):
        for file in os.listdir(self.folder_path):
            if file.endswith(".py"):
                return os.path.join(self.folder_path, file)
        return None

    def setup_parameters_ui(self, layout):
        params = self.config.get_parameters()
        if not params:
            return
            
        param_group = QGroupBox("Script Parameters")
        param_layout = QVBoxLayout()
        
        for param_name, param_config in params.items():
            param_type = param_config.get('type', 'text')
            param_label = QLabel(param_config.get('label', param_name))
            
            if param_type == 'dropdown':
                widget = QComboBox()
                for option in param_config.get('options', []):
                    widget.addItem(option)
                widget.setCurrentText(param_config.get('default', ''))
            elif param_type == 'checkbox':
                widget = QCheckBox()
                widget.setChecked(param_config.get('default', False))
            else:  # text input
                widget = QLineEdit()
                widget.setText(param_config.get('default', ''))
                if param_type == 'file':
                    browse_btn = QPushButton("Browse")
                    browse_btn.clicked.connect(partial(self.browse_file, widget))
                    hbox = QHBoxLayout()
                    hbox.addWidget(widget)
                    hbox.addWidget(browse_btn)
                    param_widget = QWidget()
                    param_widget.setLayout(hbox)
                    widget = param_widget
            
            self.param_widgets[param_name] = widget
            param_layout.addWidget(param_label)
            param_layout.addWidget(widget)
        
        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            line_edit.setText(file_path)

    def load_readme(self):
        # Try different readme formats
        readme_files = [
            os.path.join(self.folder_path, "README.md"),
            os.path.join(self.folder_path, "README.txt"),
            os.path.join(self.folder_path, "readme.md"),
            os.path.join(self.folder_path, "readme.txt")
        ]
        
        for readme_file in readme_files:
            if os.path.exists(readme_file):
                try:
                    with open(readme_file, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    # If it's markdown, convert to HTML
                    if readme_file.endswith('.md'):
                        content = markdown.markdown(content)
                        self.readme_box.setHtml(content)
                    else:
                        self.readme_box.setPlainText(content)
                    break
                except Exception as e:
                    self.readme_box.setPlainText(f"Error loading README: {str(e)}")

    def choose_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_dir)
        if folder:
            self.output_dir = folder
            self.settings.setValue(f"{os.path.basename(self.folder_path)}/output_dir", self.output_dir)
            self.update_output_folder_label()
            self.output_box.append(f"📁 Output folder set to: {self.output_dir}\n")

    def update_output_folder_label(self):
        self.choose_folder_btn.setText(f"Output: {os.path.basename(self.output_dir)}")

    def run_script(self):
        if not self.script_file:
            self.output_box.append("❌ No Python script found in this folder.\n")
            return
            
        # Validate input files
        input_files = self.drop_area.dropped_files
        if not input_files:
            reply = QMessageBox.question(self, "No Input Files", 
                                       "No input files were provided. Continue with default behavior?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Backup input files if enabled in settings
        if self.settings.value("backup_input", False, type=bool):
            self.backup_input_files(input_files)
        
        # Prepare environment
        env = os.environ.copy()
        env["OUTPUT_DIR"] = self.output_dir
        
        # Add parameters to environment
        for param_name, widget in self.param_widgets.items():
            if isinstance(widget, QComboBox):
                env[param_name.upper()] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                env[param_name.upper()] = "1" if widget.isChecked() else "0"
            elif isinstance(widget, QLineEdit):
                env[param_name.upper()] = widget.text()
            elif isinstance(widget, QWidget):  # File browser case
                line_edit = widget.findChild(QLineEdit)
                if line_edit:
                    env[param_name.upper()] = line_edit.text()
        
        # Prepare script arguments
        args = [sys.executable, self.script_file]
        for file_path in input_files:
            args.append(file_path)
        
        # Clear output and show progress
        self.output_box.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        
        # Run script in a separate thread
        self.runner_thread = ScriptRunnerThread(args, self.folder_path, env)
        self.runner_thread.output_signal.connect(self.output_box.append)
        self.runner_thread.finished_signal.connect(self.script_finished)
        self.runner_thread.start()

    def backup_input_files(self, input_files):
        # Get custom backup folder or use default
        backup_dir = self.settings.value("backup_folder", "")
        if not backup_dir:
            # Use default backup location (output_folder/backups/script_name/timestamp)
            backup_dir = os.path.join(self.output_dir, "backups", self.script_name)
        else:
            # Use custom backup location with script subfolder
            backup_dir = os.path.join(backup_dir, self.script_name)
        
        # Add timestamp to backup path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(backup_dir, timestamp)
        os.makedirs(backup_dir, exist_ok=True)
        
        for file_path in input_files:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                name, ext = os.path.splitext(filename)
                backup_filename = f"{name}_{timestamp}{ext}"
                backup_path = os.path.join(backup_dir, backup_filename)
                shutil.copy2(file_path, backup_path)
                self.output_box.append(f"📂 Backed up: {filename} → {backup_filename}\n")

    def stop_script(self):
        if self.runner_thread:
            self.runner_thread.stop()
            self.output_box.append("🛑 Script execution stopped by user\n")
            self.script_finished(False, "Stopped by user")

    def script_finished(self, success, message):
        self.progress_bar.setVisible(False)
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        if success:
            self.output_box.append(f"✅ {message}\n")
            # Offer to open output folder
            reply = QMessageBox.question(self, "Script Completed", 
                                       "Script completed successfully. Open output folder?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.open_output_folder()
        else:
            self.output_box.append(f"❌ {message}\n")
            
            # Show error details if available
            if "traceback" in message.lower() or "error" in message.lower():
                QMessageBox.critical(self, "Script Error", 
                                   f"An error occurred during script execution:\n\n{message}")

    def open_output_folder(self):
        if sys.platform.startswith("win"):
            os.startfile(self.output_dir)  # type: ignore
        elif sys.platform == "darwin":
            subprocess.call(["open", self.output_dir])
        else:
            subprocess.call(["xdg-open", self.output_dir])

# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("BifteKYS", "ScriptRunner")
        self.setWindowTitle("BifteKYS Script Runner GUI")
        self.resize(1200, 800)
        
        # Set application icon
        icon_path = resource_path("app_logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Create toolbar
        self.setup_toolbar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Determine scripts dir
        self.scripts_dir = resource_path("scripts")
        os.makedirs(self.scripts_dir, exist_ok=True)
        
        # Header with theme button
        header = QHBoxLayout()
        self.path_label = QLabel(f"Scripts folder: {self.scripts_dir}")
        self.path_label.setStyleSheet("color:#666;")
        
        # Theme toggle button
        self.theme_button = QPushButton()
        self.update_theme_button_text()
        self.theme_button.clicked.connect(self.toggle_theme)
        
        open_btn = QPushButton("Open Scripts Folder")
        open_btn.clicked.connect(self.open_scripts_folder)
        refresh_btn = QPushButton("Refresh Scripts")
        refresh_btn.clicked.connect(self.load_tabs)
        
        header.addWidget(self.path_label)
        header.addStretch(1)
        header.addWidget(self.theme_button)
        header.addWidget(open_btn)
        header.addWidget(refresh_btn)
        
        main_layout.addLayout(header)
        main_layout.addWidget(self.tabs)
        
        # Footer
        footer = QLabel("Menelaos Ioannidis © - All rights reserved.")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            QLabel { color: gray; font-size: 12px; font-style: italic;
                     padding: 6px; border-top: 1px solid #ccc; }
        """)
        main_layout.addWidget(footer)
        
        # Load tabs
        self.load_tabs()
        
        # Apply saved theme
        dark_mode = self.settings.value("dark_mode", False, type=bool)
        ThemeManager.apply_theme(QApplication.instance(), dark_mode)

    def setup_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Backup toggle action
        self.backup_action = QAction("Backup Input", self)
        self.backup_action.setCheckable(True)
        self.backup_action.setChecked(self.settings.value("backup_input", False, type=bool))
        self.backup_action.toggled.connect(self.toggle_backup)
        toolbar.addAction(self.backup_action)
        
        toolbar.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
        
        # Help action
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.show_help)
        toolbar.addAction(help_action)

    def update_theme_button_text(self):
        dark_mode = self.settings.value("dark_mode", False, type=bool)
        self.theme_button.setText("Switch to Light Mode" if dark_mode else "Switch to Dark Mode")

    def toggle_theme(self):
        dark_mode = not self.settings.value("dark_mode", False, type=bool)
        self.settings.setValue("dark_mode", dark_mode)
        ThemeManager.apply_theme(QApplication.instance(), dark_mode)
        self.update_theme_button_text()

    def toggle_backup(self, enabled):
        self.settings.setValue("backup_input", enabled)
        self.backup_action.setChecked(enabled)

    def show_settings(self):
        settings_dialog = QDialog(self)
        settings_dialog.setWindowTitle("Settings")
        layout = QVBoxLayout()
        
        # Theme setting
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout()
        dark_mode_cb = QCheckBox("Dark Mode")
        dark_mode_cb.setChecked(self.settings.value("dark_mode", False, type=bool))
        dark_mode_cb.toggled.connect(lambda checked: self.settings.setValue("dark_mode", checked))
        dark_mode_cb.toggled.connect(lambda: ThemeManager.apply_theme(QApplication.instance(), 
                                                                     self.settings.value("dark_mode", False, type=bool)))
        dark_mode_cb.toggled.connect(self.update_theme_button_text)
        theme_layout.addWidget(dark_mode_cb)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Backup setting
        backup_group = QGroupBox("Files")
        backup_layout = QVBoxLayout()
        
        # Backup enable checkbox
        backup_cb = QCheckBox("Backup input files before processing")
        backup_cb.setChecked(self.settings.value("backup_input", False, type=bool))
        backup_cb.toggled.connect(self.toggle_backup)
        backup_layout.addWidget(backup_cb)
        
        # Custom backup folder setting
        backup_folder_layout = QHBoxLayout()
        backup_folder_label = QLabel("Custom Backup Folder:")
        backup_folder_layout.addWidget(backup_folder_label)
        
        self.backup_folder_edit = QLineEdit()
        self.backup_folder_edit.setText(self.settings.value("backup_folder", ""))
        backup_folder_layout.addWidget(self.backup_folder_edit)
        
        backup_folder_btn = QPushButton("Browse")
        backup_folder_btn.clicked.connect(self.choose_backup_folder)
        backup_folder_layout.addWidget(backup_folder_btn)
        
        backup_layout.addLayout(backup_folder_layout)
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.save_settings(settings_dialog))
        button_box.rejected.connect(settings_dialog.reject)
        layout.addWidget(button_box)
        
        settings_dialog.setLayout(layout)
        settings_dialog.exec()

    def choose_backup_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
        if folder:
            self.backup_folder_edit.setText(folder)

    def save_settings(self, dialog):
        self.settings.setValue("backup_folder", self.backup_folder_edit.text())
        dialog.accept()

    def show_help(self):
        help_text = """
        <h2>BifteKYS Script Runner</h2>
        <p>This application allows you to run various Python scripts with a user-friendly interface.</p>
        
        <h3>Usage:</h3>
        <ol>
          <li>Select a script tab from the top</li>
          <li>Drag and drop input files onto the drop area</li>
          <li>Configure any script parameters if available</li>
          <li>Select an output folder</li>
          <li>Click "Run Script" to execute</li>
        </ol>
        
        <h3>Features:</h3>
        <ul>
          <li>Real-time output display</li>
          <li>Dark/Light theme support</li>
          <li>Input file backup with timestamps</li>
          <li>Custom backup folder support</li>
          <li>Parameter configuration for scripts</li>
          <li>Multi-file support</li>
        </ul>
        
        <p>For script-specific instructions, check the README section in each tab.</p>
        """
        
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Help")
        help_dialog.resize(500, 400)
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(help_text)
        layout.addWidget(text_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(help_dialog.accept)
        layout.addWidget(button_box)
        
        help_dialog.setLayout(layout)
        help_dialog.exec()

    def open_scripts_folder(self):
        path = self.scripts_dir
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore
        elif sys.platform == "darwin":
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])

    def load_tabs(self):
        # Clear existing tabs
        while self.tabs.count():
            self.tabs.removeTab(0)
            
        # Show loading indicator
        self.statusBar().showMessage("Loading scripts...")
        QApplication.processEvents()
        
        added = 0
        try:
            entries = sorted(os.listdir(self.scripts_dir))
        except FileNotFoundError:
            entries = []
            
        for folder in entries:
            folder_path = os.path.join(self.scripts_dir, folder)
            if os.path.isdir(folder_path):
                tab = ScriptTab(folder_path)
                tab_name = folder.replace("_", " ").title()
                self.tabs.addTab(tab, tab_name)
                added += 1
                
        if added == 0:
            placeholder = QTextEdit(
                "⚠ No script folders found inside /scripts.\n\n"
                "➡ Create subfolders like:\n"
                "   scripts/facebook_list/\n"
                "   scripts/agent_monthly/\n\n"
                "Each folder must contain a .py script (and optionally README.txt).\n\n"
                f"Detected path: {self.scripts_dir}"
            )
            placeholder.setReadOnly(True)
            self.tabs.addTab(placeholder, "No Scripts Found")
            
        self.statusBar().showMessage(f"Loaded {added} scripts")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("BifteKYS Script Runner")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("BifteKYS")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()