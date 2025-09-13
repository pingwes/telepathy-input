#!/usr/bin/env python3
"""
Browser detection module for checking if x.com/twitter.com is open in various browsers.
"""

import platform
import subprocess
import psutil


class BrowserDetector:
    """Detects if x.com/twitter.com is open in various browsers"""
    
    def __init__(self):
        self.system = platform.system()
        
    def is_x_com_open_mac(self):
        """Check if x.com is open in any browser on macOS"""
        browsers = {
            'Safari': '''
                tell application "Safari"
                    if it is running then
                        repeat with w in windows
                            repeat with t in tabs of w
                                try
                                    set tabURL to URL of t
                                    if tabURL contains "x.com" or tabURL contains "twitter.com" then
                                        return "true"
                                    end if
                                end try
                            end repeat
                        end repeat
                    end if
                end tell
                return "false"
            ''',
            'Google Chrome': '''
                tell application "Google Chrome"
                    if it is running then
                        repeat with w in windows
                            repeat with t in tabs of w
                                try
                                    set tabURL to URL of t
                                    if tabURL contains "x.com" or tabURL contains "twitter.com" then
                                        return "true"
                                    end if
                                end try
                            end repeat
                        end repeat
                    end if
                end tell
                return "false"
            ''',
            'Arc': '''
                tell application "Arc"
                    if it is running then
                        repeat with w in windows
                            repeat with t in tabs of w
                                try
                                    set tabURL to URL of t
                                    if tabURL contains "x.com" or tabURL contains "twitter.com" then
                                        return "true"
                                    end if
                                end try
                            end repeat
                        end repeat
                    end if
                end tell
                return "false"
            '''
        }
        
        for browser_name, script in browsers.items():
            try:
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.stdout.strip() == "true":
                    return True, browser_name
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                continue
                
        return False, None
    
    def get_active_window_title_mac(self):
        """Get the title of the currently active window on macOS"""
        script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                tell process frontApp
                    if exists (window 1) then
                        return name of window 1
                    else
                        return ""
                    end if
                end tell
            end tell
        '''
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=1
            )
            return result.stdout.strip()
        except:
            return ""
    
    def is_browser_active_with_x(self):
        """Check if the active window is a browser with x.com"""
        if self.system == "Darwin":
            title = self.get_active_window_title_mac()
            # X.com usually shows "X" or specific page titles in the window title
            return "x.com" in title.lower() or " / X" in title or "(@" in title
        return False
    
    def get_frontmost_application(self):
        """Get the name of the frontmost (active) application on macOS"""
        if self.system != "Darwin":
            return None
            
        script = 'tell application "System Events" to return name of first application process whose frontmost is true'
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=1
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"AppleScript error: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error getting frontmost app: {e}")
            return None
    
    def is_browser_frontmost_with_x_com(self):
        """Check if a browser with x.com is the frontmost application"""
        if self.system != "Darwin":
            return False, None
            
        frontmost_app = self.get_frontmost_application()
        if not frontmost_app:
            return False, None
        
        # Check if the frontmost app is a browser
        browser_apps = ['Safari', 'Google Chrome', 'Arc', 'Firefox', 'Microsoft Edge', 
                       'Brave Browser', 'Opera', 'Vivaldi']
        
        frontmost_browser = None
        for browser in browser_apps:
            if browser.lower() in frontmost_app.lower():
                frontmost_browser = browser
                break
        
        if not frontmost_browser:
            return False, None
        
        # Now check if this specific browser has x.com open
        browser_scripts = {
            'Safari': '''
                tell application "Safari"
                    if it is running and frontmost then
                        repeat with w in windows
                            repeat with t in tabs of w
                                try
                                    set tabURL to URL of t
                                    if tabURL contains "x.com" or tabURL contains "twitter.com" then
                                        return "true"
                                    end if
                                end try
                            end repeat
                        end repeat
                    end if
                end tell
                return "false"
            ''',
            'Google Chrome': '''
                tell application "Google Chrome"
                    if it is running and frontmost then
                        repeat with w in windows
                            repeat with t in tabs of w
                                try
                                    set tabURL to URL of t
                                    if tabURL contains "x.com" or tabURL contains "twitter.com" then
                                        return "true"
                                    end if
                                end try
                            end repeat
                        end repeat
                    end if
                end tell
                return "false"
            ''',
            'Arc': '''
                tell application "Arc"
                    if it is running and frontmost then
                        repeat with w in windows
                            repeat with t in tabs of w
                                try
                                    set tabURL to URL of t
                                    if tabURL contains "x.com" or tabURL contains "twitter.com" then
                                        return "true"
                                    end if
                                end try
                            end repeat
                        end repeat
                    end if
                end tell
                return "false"
            '''
        }
        
        # Try to find the matching script for the frontmost browser
        script = None
        for browser_name, browser_script in browser_scripts.items():
            if browser_name.lower() in frontmost_browser.lower():
                script = browser_script
                break
        
        if not script:
            # Fallback: check window title for browsers we don't have scripts for
            title = self.get_active_window_title_mac()
            has_x_com = "x.com" in title.lower() or " / X" in title or "(@" in title
            return has_x_com, frontmost_browser
        
        # Execute the script to check for x.com
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )
            has_x_com = result.stdout.strip() == "true"
            return has_x_com, frontmost_browser
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False, frontmost_browser
    
    def check_browser_processes(self):
        """Check if browser processes are running"""
        browser_processes = [
            'Safari', 'Google Chrome', 'firefox', 'Microsoft Edge',
            'Arc', 'Brave Browser', 'Opera', 'Vivaldi'
        ]
        
        running_browsers = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                process_name = proc.info['name']
                if any(browser.lower() in process_name.lower() for browser in browser_processes):
                    running_browsers.append(process_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return running_browsers
