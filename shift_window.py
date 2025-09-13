#!/usr/bin/env python3
"""
A Python script that opens a small window in the bottom right corner
when the Shift key is held down, and closes it after 2 seconds.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import queue
from pynput import keyboard
import sys
import os
import platform

class ShiftWindow:
    def __init__(self):
        self.window = None
        self.shift_pressed = False
        self.window_timer = None
        self.running = True
        self.event_queue = queue.Queue()
        self.window_visible = False
        self.window_created = False  # Track if window has been created
        
    def create_window_main_thread(self):
        """Create and position the small window in bottom right corner on main thread"""
        # Create the main window
        window = tk.Tk()
        window.title("Shift Window")
        window.overrideredirect(True)  # Remove window decorations
        window.attributes('-topmost', True)  # Keep on top
        window.configure(bg='#2c3e50')
        
        # Set window size
        width = 200
        height = 80
        
        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Calculate position for bottom right corner
        x = screen_width - width - 10  # 10px margin from right edge
        y = screen_height - height - 10  # 10px margin from bottom edge
        
        # Set window geometry
        window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Add some content to the window
        frame = tk.Frame(window, bg='#2c3e50')
        frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        label = tk.Label(
            frame, 
            text="Shift Key\nDetected!", 
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#2c3e50',
            justify='center'
        )
        label.pack(expand=True)
        
        # Don't start timer here - it will be started when window is created
        
        # Initially hide the window (will be shown when needed)
        window.withdraw()
        
        # Now show the window and bring it to front
        window.deiconify()
        window.lift()
        window.attributes('-topmost', True)  # Keep on top of other windows
        window.focus_force()
        
        return window
    
    def start_timer(self):
        """Start a 2-second timer to close the window"""
        if self.window_timer:
            self.window_timer.cancel()
        
        self.window_timer = threading.Timer(2.0, self.schedule_window_close)
        self.window_timer.start()
    
    def schedule_window_close(self):
        """Schedule window hide on main thread"""
        self.event_queue.put("hide_window")
    
    def hide_window(self):
        """Hide the window without destroying it"""
        if self.window and self.window_visible:
            try:
                self.window.withdraw()  # Hide the window
                self.window_visible = False
                print("Window hidden")
            except tk.TclError:
                pass  # Window might already be destroyed
        self.window_timer = None
    
    def close_window(self):
        """Close the window completely"""
        if self.window:
            try:
                self.window.destroy()
            except tk.TclError:
                pass  # Window might already be destroyed
            self.window = None
            self.window_created = False
            self.window_visible = False
        self.window_timer = None
    
    def show_window(self):
        """Show the window with proper dimensions and position"""
        if self.window and not self.window_visible:
            try:
                # Restore window to proper size and position
                width = 200
                height = 80
                
                # Get screen dimensions
                screen_width = self.window.winfo_screenwidth()
                screen_height = self.window.winfo_screenheight()
                
                # Calculate position for bottom right corner
                x = screen_width - width - 10  # 10px margin from right edge
                y = screen_height - height - 10  # 10px margin from bottom edge
                
                # Set window geometry
                self.window.geometry(f"{width}x{height}+{x}+{y}")
                self.window.attributes('-topmost', True)  # Keep on top
                self.window.deiconify()  # Show the window
                self.window.lift()
                self.window.focus_force()
                self.window_visible = True
                print("Window shown")
            except tk.TclError:
                # Window might be destroyed, recreate it
                self.window = None
                self.window_created = False
                self.window_visible = False
    
    def on_shift_press(self, key):
        """Handle Shift key press"""
        # Log all key presses
        try:
            key_name = key.name if hasattr(key, 'name') else str(key)
        except:
            key_name = str(key)

        if ('shift' in key_name) and not self.shift_pressed:
            print("🎯 Shift key detected! Creating window...")
            self.shift_pressed = True
            # Send event to main thread via queue
            self.event_queue.put("create_window")
    
    def on_shift_release(self, key):
        """Handle Shift key release"""
        # Log all key releases
        try:
            key_name = key.name if hasattr(key, 'name') else str(key)
        except:
            key_name = str(key)
        
        if 'shift' in key_name:
            self.shift_pressed = False
    
    def start_monitoring(self):
        """Start monitoring keyboard for Shift key"""
        print("\n" + "=" * 50)
        print("🎯 Shift Window Monitor started!")
        print("=" * 50)
        print("Hold down the Shift key to open the window.")
        print("Press Ctrl+C to exit.")
        print("=" * 50)
        
        # Start keyboard listener in a separate thread
        def keyboard_monitor():
            with keyboard.Listener(
                on_press=self.on_shift_press,
                on_release=self.on_shift_release
            ) as listener:
                try:
                    listener.join()
                except KeyboardInterrupt:
                    print("\nExiting...")
                    self.running = False
                    if self.window:
                        self.close_window()
        
        # Start keyboard monitoring in background thread
        keyboard_thread = threading.Thread(target=keyboard_monitor, daemon=True)
        keyboard_thread.start()
        
        # Run tkinter main loop on main thread
        try:
            while self.running:
                # Check for events from keyboard thread
                try:
                    event = self.event_queue.get_nowait()
                    if event == "create_window":
                        if not self.window_created:
                            print("Creating window on main thread...")
                            self.window = self.create_window_main_thread()
                            self.window_visible = True
                            self.window_created = True
                            # Start timer only when window is first created
                            self.start_timer()
                        elif not self.window_visible:
                            print("Showing existing window...")
                            self.show_window()
                            self.start_timer()
                        else:
                            print("Window already visible, resetting timer...")
                            self.start_timer()
                    elif event == "hide_window":
                        print("Hiding window on main thread...")
                        self.hide_window()
                    elif event == "close_window":
                        print("Closing window on main thread...")
                        self.close_window()
                        print("Window closed successfully")
                except queue.Empty:
                    pass
                
                # Update tkinter window if it exists
                if self.window:
                    try:
                        self.window.update()
                    except tk.TclError:
                        # Window was closed
                        self.window = None
                
                time.sleep(0.01)  # Small delay to prevent high CPU usage
        except KeyboardInterrupt:
            print("\nExiting...")
            self.running = False
            if self.window:
                self.close_window()
        finally:
            self.running = False
            if self.window:
                self.close_window()

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
