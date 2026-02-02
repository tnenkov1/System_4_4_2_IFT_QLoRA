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