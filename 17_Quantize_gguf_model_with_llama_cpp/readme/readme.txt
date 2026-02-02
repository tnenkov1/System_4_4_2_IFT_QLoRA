Python script for quantizing the .gguf model with .llama.cpp

- pull .llama.cpp, than change the path in the .bat file config:

REM =====================================================
REM Set base directories (adjust if needed)
REM =====================================================
set "BASE_DIR=%~dp0"
set "GGUF_FOLDER=%BASE_DIR%GGUF"
set "QUANTIZE_EXE=C:\Users\.....PC 1.......\llama.cpp\build\bin\Release\llama-quantize.exe" <----- change path


1. Move the the .gguf from "16_convert_safetensors_to_gguf_with_llama_cpp\GGUF" to the folder: "17_Quantize_gguf_model_with_llama_cpp\GGUF"

2. Execute the .bat file
3. Name the model
4. The quantized model will be in the folder: "GGUF"