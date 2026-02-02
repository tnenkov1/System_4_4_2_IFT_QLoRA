def translate_docx(file_name, lang_item, prompt_text, session):
    """Processes a single DOCX file element by element."""
    source_path = os.path.join(INPUT_DIR, file_name)
    suffix = get_lang_suffix(lang_item['name'])
    
    name_part, ext = os.path.splitext(file_name)
    new_filename = f"{name_part}_{suffix}{ext}"
    save_path = os.path.join(SESSION_OUTPUT_DIR, new_filename)
    
    write_log(f"Starting translation: {file_name} -> {new_filename}")
    
    try:
        doc = Document(source_path)
        
        elements = []
        for p in doc.paragraphs:
            if p.text.strip(): elements.append(p)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip(): elements.append(cell)

        pbar = tqdm(total=len(elements), desc=f"  ↳ {file_name[:25]}", unit="el", leave=False, colour='cyan')

        for obj in elements:
            obj.text = call_ollama(obj.text, prompt_text, session)
            pbar.update(1)
        
        doc.save(save_path)
        pbar.close()
        write_log(f"Successfully completed: {new_filename}")
        return True
    except Exception as e:
        write_log(f"Critical error processing {file_name}: {str(e)}")
        return False