# Shift Window

A Python script that opens a small window in the bottom right corner of your screen when you hold down the Shift key, and closes it after 2 seconds.

## Features

- Opens a 200px × 80px window in the bottom right corner
- Triggers when Shift key is held down
- Automatically closes after 2 seconds
- Stays on top of other windows
- Clean, minimal design

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script:
```bash
python shift_window.py
```

- Hold down the Shift key to open the window
- The window will automatically close after 2 seconds
- Press Ctrl+C to exit the program

## Requirements

- Python 3.6+
- pynput (for keyboard monitoring)
- tkinter (usually included with Python)

## Notes

- The script requires accessibility permissions on macOS to monitor keyboard input
- You may need to grant permissions in System Preferences > Security & Privacy > Privacy > Accessibility
