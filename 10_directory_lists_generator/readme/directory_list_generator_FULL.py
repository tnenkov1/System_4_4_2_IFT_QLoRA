import os
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
LISTS_DIR = SCRIPT_DIR / "directory_lists"

LISTS_DIR.mkdir(exist_ok=True)

def list_contents(path):
    """Retrieve folder and file names."""
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
        print("  [Enter]        - generate list with FULL PATHS")
        print("-" * 50)

        for idx, folder in enumerate(folders, start=1):
            print(f"{idx:3}. 📁 {folder}")

        choice = input("\nYour choice: ").strip()

        # [Enter] - generate list for this folder
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
            print("⚠️ Invalid command.")

def save_directory_list(target_path):
    """Save FULL PATHS of elements into a text file."""
    folders, files = list_contents(target_path)
    
    timestamp = datetime.now().strftime("%H-%M-%S")
    file_name = f"full_paths_list_{timestamp}.txt"
    output_path = LISTS_DIR / file_name

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"FULL LIST FOR: {target_path}\n")
            f.write(f"DATE AND TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("Folders (Full Paths):\n")
            for folder in folders:
                full_folder_path = target_path / folder
                f.write(f"{full_folder_path}\n")
            
            f.write("\nFiles (Full Paths):\n")
            for file in files:
                full_file_path = target_path / file
                f.write(f"{full_file_path}\n")
        
        print(f"\n✅ Full paths list generated successfully!")
        print(f"📄 File: {file_name}")
        print(f"📂 Folder: directory_lists")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

def main():
    print("📁 Starting the navigator (Full Paths mode)...")
    selected_folder = navigate_folders()
    
    if selected_folder:
        save_directory_list(selected_folder)
    else:
        print("\n👋 Operation cancelled.")

if __name__ == "__main__":
    main()
