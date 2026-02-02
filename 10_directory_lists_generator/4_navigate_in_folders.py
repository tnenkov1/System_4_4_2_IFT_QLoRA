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