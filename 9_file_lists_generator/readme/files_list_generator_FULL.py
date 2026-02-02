import os
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
LISTS_DIR = SCRIPT_DIR / "file_lists"

LISTS_DIR.mkdir(exist_ok=True)

def list_contents(path):
    """Retrieve folders and files."""
    folders = []
    files = []
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    folders.append(entry.name)
                elif entry.is_file():
                    files.append(entry.name)
        folders.sort()
        files.sort()
    except PermissionError:
        print(f"\n⚠️ Access denied: {path}")
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
        
    return folders, files

def navigate_folders():
    """Interactive navigation starting from Desktop."""
    current_path = Path.home() / "Desktop"
    history = []

    while True:
        folders, files = list_contents(current_path)
        print(f"\n📂 Current folder: {current_path}")
        print("-" * 50)
        print("Navigation:")
        print("  [number+Enter] - enter folder")
        print("  [0+Enter]      - go back to previous folder")
        print("  [Enter]        - generate file list for this folder")
        print("-" * 50)

        for idx, folder in enumerate(folders, start=1):
            print(f"{idx:3}. 📁 {folder}")

        choice = input("\nYour choice: ").strip()

        # [Enter] - generate file list
        if choice == "":
            return current_path

        # [0+Enter] - go back
        if choice == "0":
            if history:
                current_path = history.pop()
            else:
                print("ℹ️ Already at the starting folder (Desktop).")
            continue

        # [number+Enter] - enter folder
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(folders):
                history.append(current_path)
                current_path = current_path / folders[idx]
            else:
                print("⚠️ Invalid number.")
        elif choice.lower() == 'q':
            return None
        else:
            print("⚠️ Invalid command. Use a number or Enter.")

def save_file_list(target_path):
    """Save the file list with a timestamp in the file_lists folder."""
    folders, files = list_contents(target_path)
    
    timestamp = datetime.now().strftime("%H-%M-%S")
    file_name = f"file_list_{timestamp}.txt"
    output_path = LISTS_DIR / file_name

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"FILE LIST FOR: {target_path}\n")
            f.write(f"DATE AND TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("Folders:\n")
            for folder in folders:
                f.write(f"{folder}\n")
            
            f.write("\nFiles:\n")
            for file in files:
                f.write(f"{file}\n")
        
        print(f"\n✅ File list is generated!")
        print(f"📄 File: {file_name}")
        print(f"📂 Folder: file_lists")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

def main():
    print("📁 Starting the folder navigator...")
    selected_folder = navigate_folders()
    
    if selected_folder:
        save_file_list(selected_folder)
    else:
        print("\n👋 Operation cancelled.")

if __name__ == "__main__":
    main()
