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
