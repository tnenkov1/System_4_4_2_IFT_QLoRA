@echo off
title Llama.cpp Quantization Tool
color 0B

REM =====================================================
REM Set base directories (adjust if needed)
REM =====================================================
set "BASE_DIR=%~dp0"
set "GGUF_FOLDER=%BASE_DIR%GGUF"
set "QUANTIZE_EXE=C:\Users\GRIGS PC 1\llama.cpp\build\bin\Release\llama-quantize.exe"

REM =====================================================
REM STEP 1: Select Source Model
REM =====================================================
echo ====================================================
echo      STEP 1: Select Source Model
echo ====================================================
set /p sourcename="Enter the name of the source GGUF file (without .gguf): "
set "INPUT_FILE=%GGUF_FOLDER%\%sourcename%.gguf"

if not exist "%INPUT_FILE%" (
    color 0C
    echo ERROR: File "%INPUT_FILE%" not found!
    pause
    exit /b 1
)

REM =====================================================
REM STEP 2: Name Output Model
REM =====================================================
echo.
echo ====================================================
echo      STEP 2: Name your Quantized Model
echo ====================================================
set /p base_output_name="Enter base name for output (e.g. MyModel): "

REM =====================================================
REM STEP 3: Select Quantization Method
REM =====================================================
echo.
echo ====================================================
echo      STEP 3: Select Quantization Method
echo ====================================================
echo [1]  Q4_0
echo [2]  Q4_1
echo [3]  Q2_K
echo [4]  Q3_K_S
echo [5]  Q3_K_M
echo [6]  Q3_K_L
echo [7]  Q4_K_S
echo [8]  Q4_K_M  (Recommended)
echo [9]  Q5_K_S
echo [10] Q5_K_M
echo [11] Q6_K
echo [12] Q8_0
echo.

set /p choice="Enter choice number (1-12): "

REM =====================================================
REM Map choice to method
REM =====================================================
if "%choice%"=="1"  set "METHOD=Q4_0"
if "%choice%"=="2"  set "METHOD=Q4_1"
if "%choice%"=="3"  set "METHOD=Q2_K"
if "%choice%"=="4"  set "METHOD=Q3_K_S"
if "%choice%"=="5"  set "METHOD=Q3_K_M"
if "%choice%"=="6"  set "METHOD=Q3_K_L"
if "%choice%"=="7"  set "METHOD=Q4_K_S"
if "%choice%"=="8"  set "METHOD=Q4_K_M"
if "%choice%"=="9"  set "METHOD=Q5_K_S"
if "%choice%"=="10" set "METHOD=Q5_K_M"
if "%choice%"=="11" set "METHOD=Q6_K"
if "%choice%"=="12" set "METHOD=Q8_0"

if not defined METHOD (
    echo ERROR: Invalid choice!
    pause
    exit /b 1
)

REM =====================================================
REM Build output filename
REM =====================================================
set "OUTPUT_FILE=%GGUF_FOLDER%\%base_output_name%_%METHOD%.gguf"

REM =====================================================
REM STEP 4: Process
REM =====================================================
echo.
echo ====================================================
echo      STEP 4: Processing...
echo ====================================================
echo Input:  "%INPUT_FILE%"
echo Output: "%OUTPUT_FILE%"
echo Method: %METHOD%
echo.

REM =====================================================
REM Run quantization
REM =====================================================
"%QUANTIZE_EXE%" "%INPUT_FILE%" "%OUTPUT_FILE%" %METHOD%

REM =====================================================
REM Check result
REM =====================================================
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================================
    echo SUCCESS: Quantization complete!
    echo ====================================================
) else (
    echo.
    echo ====================================================
    echo ERROR: Quantization failed.
    echo ====================================================
)

pause
