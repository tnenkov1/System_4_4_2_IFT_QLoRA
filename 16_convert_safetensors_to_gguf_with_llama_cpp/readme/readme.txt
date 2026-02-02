Python script for converting the base model to .gguf format with .llama.cpp

- pull .llama.cpp, than change the path in the .bat file config:

EM =====================================================
REM Configuration
REM =====================================================
set "PYTHON_EXE=python"
set "LLAMA_CPP_DIR=C:\Users\.......PC 1.......\llama.cpp"       <------ change path
set "CONVERT_SCRIPT=%LLAMA_CPP_DIR%\convert_hf_to_gguf.py"   

set "MODEL_DIR=%BASE_DIR%FineTunedModel"
set "OUTPUT_FOLDER=%BASE_DIR%GGUF"


1. Move the the merged fine-tuned model from "15_QLoRA_merge\FineTunedModel" to the folder: "16_convert_safetensors_to_gguf_with_llama_cpp\FineTunedModel"

2. Execute the .bat file
3. Name the model
4. The converted fine-tuned model will be in the folder: "GGUF"