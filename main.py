#!/usr/bin/env python3
"""
Main entry point for the Shift Window Monitor application.

A Python script that opens a small window in the bottom right corner
when the Shift key is held down, and closes it after 2 seconds.
"""

import tkinter as tk
from tkinter import messagebox
import platform
import sys
from pynput import keyboard

from shift_window import ShiftWindow


def check_mac_permissions():
    """Check if running on Mac and test if permissions are already granted"""
    if platform.system() == "Darwin":  # macOS
        print("🍎 macOS detected - checking accessibility permissions...")
        
        # Test if we can actually monitor keyboard input
        try:
            # Try to create a keyboard listener to test permissions
            test_listener = keyboard.Listener(on_press=lambda x: None)
            test_listener.start()
            test_listener.stop()
            print("✅ Accessibility permissions are already granted!")
            return True
        except Exception as e:
            print(f"Permission test error: {e}")
            print("❌ Accessibility permissions not granted or not working.")
            print("=" * 60)
            print("This script requires Accessibility permissions to monitor keyboard input.")
            print()
            print("To grant permissions:")
            print("1. Go to System Preferences > Security & Privacy > Privacy")
            print("2. Select 'Accessibility' from the left sidebar")
            print("3. Click the lock icon and enter your password")
            print("4. Add your Terminal app (or Python environment) to the list")
            print("5. Make sure it's checked/enabled")
            print()
            print("If you don't grant these permissions, the script won't work.")
            print("=" * 60)
            
            # Show a GUI dialog as well
            try:
                root = tk.Tk()
                root.withdraw()  # Hide the main window
                
                result = messagebox.askokcancel(
                    "macOS Permissions Required",
                    "This script needs Accessibility permissions to monitor keyboard input.\n\n"
                    "Please go to:\n"
                    "System Preferences > Security & Privacy > Privacy > Accessibility\n\n"
                    "Add your Terminal/Python app and enable it.\n\n"
                    "Click OK to continue or Cancel to exit."
                )
                root.destroy()
                
                if not result:
                    print("Permission setup cancelled. Exiting...")
                    sys.exit(0)
            except:
                pass  # If GUI fails, continue with text prompt
            return False
    return True


def main():
    """Main function"""
    # Check if required packages are installed
    try:
        import pynput
    except ImportError:
        print("Error: pynput package is required but not installed.")
        print("Please install it using: pip install pynput")
        sys.exit(1)
    
    # Check for Mac and show permission prompt
    if not check_mac_permissions():
        print("Please grant accessibility permissions and try again.")
        return
    
    # Create and start the shift window monitor
    shift_window = ShiftWindow()
    shift_window.start_monitoring()


if __name__ == "__main__":
    main()
