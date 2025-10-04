import subprocess
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

# ---------------------------------------------------------------------------
# Configuration & Environment Helpers
# ---------------------------------------------------------------------------

def resource_path(relative_name: str) -> str:
    """Return absolute path to resource, works for dev and PyInstaller executable.

    When bundled with PyInstaller, sys._MEIPASS points to the temp extraction dir.
    We keep the editable config (apps_to_open.txt) alongside the executable, so
    we look relative to sys.executable when frozen; otherwise use script folder.
    """
    if getattr(sys, 'frozen', False):  # Running as bundled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_name)

APPS_FILE = resource_path('apps_to_open.txt')

def update_apps_file(app_paths):
    """Update the apps_to_open.txt file with the current app paths."""
    try:
        with open(APPS_FILE, 'w', encoding='utf-8') as file:
            for app in app_paths:
                file.write(app + '\n')
    except OSError as e:
        messagebox.showerror("Error", f"Unable to write to apps file:\n{APPS_FILE}\n{e}")

def get_new_path(old_path):
    """Prompt user for a new file path using Windows dialogs"""
    # Create a hidden root window
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Show message about missing file
    title = "Application Not Found"
    message = f"File not found:\n{old_path}\n\nWould you like to browse for the correct location?"
    
    result = messagebox.askyesnocancel(title, message)
    
    if result is True:  # Yes - browse for file
        new_path = filedialog.askopenfilename(
            title="Select the correct application file",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        root.destroy()
        if new_path and os.path.exists(new_path):
            return new_path
        elif new_path:  # User selected a file but it doesn't exist
            messagebox.showerror("Error", f"Selected file does not exist: {new_path}")
            return None
        else:  # User cancelled file dialog
            return None
    elif result is False:  # No - manually enter path
        new_path = simpledialog.askstring(
            "Enter File Path", 
            f"Enter the correct file path for:\n{os.path.basename(old_path)}"
        )
        root.destroy()
        if new_path and os.path.exists(new_path.strip()):
            return new_path.strip()
        elif new_path:
            messagebox.showerror("Error", f"File not found: {new_path}")
            return None
        else:
            return None
    else:  # Cancel - skip this app
        root.destroy()
        return None

"""Load or create the applications file.

If the file does not exist, create a starter template so the user can edit it.
"""
if not os.path.exists(APPS_FILE):
    try:
        with open(APPS_FILE, 'w', encoding='utf-8') as f:
            f.write('# Add one full application path per line. Lines starting with # are ignored.\n')
    except OSError as e:
        # We'll still proceed with empty list; user will get summary only.
        pass

try:
    with open(APPS_FILE, 'r', encoding='utf-8') as file:
        app_paths = [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]
except OSError as e:
    app_paths = []
    # We'll show an error dialog after Tk is initialized.
    _deferred_file_error = str(e)
else:
    _deferred_file_error = None

root = tk.Tk()
root.withdraw()  # Hide the main window

if _deferred_file_error:
    messagebox.showerror("File Error", f"Failed to read apps file:\n{APPS_FILE}\n{_deferred_file_error}")

updated_paths = []
file_updated = False
opened_count = 0
skipped_count = 0

for i, app in enumerate(app_paths):
    if os.path.exists(app):
        try:
            subprocess.Popen(app)
            updated_paths.append(app)
            opened_count += 1
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open {os.path.basename(app)}:\n{str(e)}")
            updated_paths.append(app)
    else:
        new_path = get_new_path(app)
        if new_path:
            try:
                subprocess.Popen(new_path)
                updated_paths.append(new_path)
                file_updated = True
                opened_count += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open {os.path.basename(new_path)}:\n{str(e)}")
                updated_paths.append(new_path)
                file_updated = True
        else:
            skipped_count += 1
            # Don't add skipped apps to updated_paths

# Update the file if any changes were made
if file_updated:
    update_apps_file(updated_paths)
    messagebox.showinfo("File Updated", f"Updated apps file:\n{APPS_FILE}")

# Show final summary
summary_message = f"Launch Summary:\n• {opened_count} applications opened successfully\n• {skipped_count} applications skipped"
messagebox.showinfo("Launch Complete", summary_message)

# Clean up
root.destroy()
