def main():
    print("📁 Starting the folder navigator...")
    selected_folder = navigate_folders()
    
    if selected_folder:
        save_file_list(selected_folder)
    else:
        print("\n👋 Operation cancelled.")

if __name__ == "__main__":
    main()