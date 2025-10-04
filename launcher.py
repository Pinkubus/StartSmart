import subprocess
import os

def update_apps_file(app_paths):
    """Update the apps_to_open.txt file with the current app paths"""
    with open('apps_to_open.txt', 'w') as file:
        for app in app_paths:
            file.write(app + '\n')

def get_new_path(old_path):
    """Prompt user for a new file path"""
    print(f"\nFile not found: {old_path}")
    while True:
        new_path = input("Please enter the correct file path (or 'skip' to skip this app): ").strip()
        if new_path.lower() == 'skip':
            return None
        if os.path.exists(new_path):
            return new_path
        else:
            print(f"File not found: {new_path}. Please try again.")

# Read application paths from the text file
with open('apps_to_open.txt', 'r') as file:
    app_paths = [line.strip() for line in file if line.strip()]

updated_paths = []
file_updated = False

for i, app in enumerate(app_paths):
    if os.path.exists(app):
        try:
            subprocess.Popen(app)
            print(f"Opened: {app}")
            updated_paths.append(app)
        except Exception as e:
            print(f"Failed to open {app}: {e}")
            updated_paths.append(app)
    else:
        new_path = get_new_path(app)
        if new_path:
            try:
                subprocess.Popen(new_path)
                print(f"Opened: {new_path}")
                updated_paths.append(new_path)
                file_updated = True
            except Exception as e:
                print(f"Failed to open {new_path}: {e}")
                updated_paths.append(new_path)
                file_updated = True
        else:
            print(f"Skipping: {app}")
            # Don't add skipped apps to updated_paths

# Update the file if any changes were made
if file_updated:
    update_apps_file(updated_paths)
    print("\nUpdated apps_to_open.txt with new file paths.")
