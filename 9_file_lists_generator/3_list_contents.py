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