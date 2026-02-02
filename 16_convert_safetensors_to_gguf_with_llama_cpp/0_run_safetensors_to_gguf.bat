@echo off
title GGUF Conversion Script
color 0A

REM =====================================================
REM Resolve base directory (where this BAT lives)
REM =====================================================
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

REM =====================================================
REM Configuration
REM =====================================================
set "PYTHON_EXE=python"
set "LLAMA_CPP_DIR=C:\Users\GRIGS PC 1\llama.cpp"
set "CONVERT_SCRIPT=%LLAMA_CPP_DIR%\convert_hf_to_gguf.py"

set "MODEL_DIR=%BASE_DIR%FineTunedModel"
set "OUTPUT_FOLDER=%BASE_DIR%GGUF"

REM =====================================================
REM Safety checks
REM =====================================================
if not exist "%CONVERT_SCRIPT%" (
    echo ERROR: convert_hf_to_gguf.py not found!
    echo Expected at: %CONVERT_SCRIPT%
    pause
    exit /b 1
)

if not exist "%MODEL_DIR%\config.json" (
    echo ERROR: config.json not found in FineTunedModel
    pause
    exit /b 1
)

if not exist "%OUTPUT_FOLDER%" (
    mkdir "%OUTPUT_FOLDER%"
)

REM =====================================================
REM UI
REM =====================================================
echo ====================================================
echo        GGUF CONVERSION (HF -> GGUF)
echo ====================================================
echo.
echo llama.cpp: %LLAMA_CPP_DIR%
echo Model dir: %MODEL_DIR%
echo Output dir: %OUTPUT_FOLDER%
echo.

set /p filename="Enter output filename (without .gguf): "
set "FINAL_OUTPUT=%OUTPUT_FOLDER%\%filename%.gguf"

echo.
echo Converting... please wait.
echo.

REM =====================================================
REM Conversion
REM =====================================================
"%PYTHON_EXE%" "%CONVERT_SCRIPT%" "%MODEL_DIR%" ^
  --outfile "%FINAL_OUTPUT%" ^
  --outtype f16

REM =====================================================
REM Result
REM =====================================================
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================================
    echo SUCCESS: %filename%.gguf created successfully!
    echo ====================================================
) else (
    echo.
    echo ====================================================
    echo ERROR: GGUF conversion failed.
    echo ====================================================
)

echo.
pause
