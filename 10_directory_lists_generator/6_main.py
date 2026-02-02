def main():
    print("📁 Starting the navigator (Full Paths mode)...")
    selected_folder = navigate_folders()
    
    if selected_folder:
        save_directory_list(selected_folder)
    else:
        print("\n👋 Operation cancelled.")

if __name__ == "__main__":
    main()