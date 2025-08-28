🥩 BifteKYS Script Runner

BifteKYS Script Runner is a simple, user-friendly GUI tool for running your custom Python scripts.
It supports drag-and-drop input, custom output folders, and per-script instructions, all inside one clean interface.

🚀 Getting Started
1. Clone or Download
git clone https://github.com/yourusername/biftekys-script-runner.git
cd biftekys-script-runner

2. Install Requirements

Make sure Python 3.10+ is installed, then:

pip install -r requirements.txt

3. Run the App

Double-click RUN.bat
or run manually:

python gui_runner.py

📂 Folder Structure
BifteKYS/
├─ gui_runner.py           # Main GUI application
├─ RUN.bat                 # Batch file to start the app
├─ requirements.txt        # Dependencies
├─ app_logo.png            # Customizable logo
└─ scripts/
   ├─ facebook_list/
   │   ├─ list_script.py
   │   └─ README.txt
   └─ agent_monthly/
       ├─ monthly_report_script.py
       └─ README.txt

🛠️ Adding New Scripts

Create a new folder inside /scripts/ (e.g. scripts/my_script/).

Add your .py script inside.

Add a README.txt with How to use and Notes (EN + GR).

Restart the app — your script will appear automatically.

✨ Features

🖥️ Drag & Drop GUI (no terminal needed)

📂 Script auto-discovery (tabs for each script)

📥 Flexible input (any filename allowed)

📤 Custom output folder support

🌍 EN & GR instructions in each script tab

👨‍💻 Author

Created by Menelaos Ioannidis