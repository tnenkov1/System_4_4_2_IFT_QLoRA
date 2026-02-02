def main():
    write_log("--- SESSION START ---")
    
    # 1. Load JSON list of prompts
    if not os.path.exists(PROMPTS_JSON):
        print(f"❌ Error: {PROMPTS_JSON} not found!")
        write_log("Error: prompt_list.json missing")
        return

    with open(PROMPTS_JSON, "r", encoding="utf-8") as f:
        languages = json.load(f)

    # 2. Check for DOCX files
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".docx")]
    if not files:
        print(f"⚠️ No .docx files found in {INPUT_DIR}")
        write_log("End: No files to process.")
        return

    # 3. User interface
    print(f"\n📂 Files found for translation: {len(files)}")
    print("🌍 Select target language:")
    for idx, lang in enumerate(languages, 1):
        print(f"{idx:2}. {lang['desc']}")

    choice = input("\nEnter number(s) (e.g., 1,3) or 'all': ").strip().lower()
    
    if choice == 'all':
        selected_langs = languages
    else:
        try:
            indices = [int(i.strip()) - 1 for i in choice.split(",")]
            selected_langs = [languages[i] for i in indices if 0 <= i < len(languages)]
        except:
            print("❌ Invalid selection.")
            return

    if not selected_langs: return

    os.makedirs(SESSION_OUTPUT_DIR, exist_ok=True)
    write_log(f"Selected languages: {[l['name'] for l in selected_langs]}")

    # 4. Translation process
    session = requests.Session()
    print(f"\n🚀 Starting... Results will be in: {RUN_TS}")

    for lang in tqdm(selected_langs, desc="OVERALL PROGRESS (Languages)", unit="lang"):
        prompt_content = load_prompt_text(lang['name'])
        
        if not prompt_content:
            write_log(f"Error: Missing .txt prompt file for {lang['name']}")
            continue
            
        for doc_file in files:
            translate_docx(doc_file, lang, prompt_content, session)

    write_log("--- SESSION END ---")
    print("-" * 30)
    print(f"\n✨ Done! Check logs in the 'logs' folder for details.")
    print(f"📂 Results saved in folder: docx_translated_files")
    print("-" * 30)
    print("👋 Byee!")

if __name__ == "__main__":
    main()