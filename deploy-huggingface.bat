@echo off
REM Hugging Face Spaces Deployment Script for Windows

echo ========================================
echo  Hugging Face Spaces Deployment
echo ========================================
echo.

REM Check if huggingface_hub is installed
python -c "import huggingface_hub" 2>nul
if errorlevel 1 (
    echo Installing huggingface_hub...
    pip install huggingface_hub
)

REM Login to Hugging Face
echo.
echo ========================================
echo  Step 1: Login to Hugging Face
echo ========================================
echo.
huggingface-cli login

REM Ask for space name
echo.
echo ========================================
echo  Step 2: Enter Space Details
echo ========================================
echo.
set /p USERNAME="Enter your Hugging Face username: "
set /p SPACENAME="Enter space name (e.g., face-attendance): "

REM Clone the space
echo.
echo ========================================
echo  Step 3: Cloning your Space...
echo ========================================
echo.
if exist "%SPACENAME%" (
    echo Space directory already exists, skipping clone...
) else (
    git clone https://huggingface.co/spaces/%USERNAME%/%SPACENAME%
)

REM Copy files
echo.
echo ========================================
echo  Step 4: Copying project files...
echo ========================================
echo.

echo Copying backend files...
xcopy /E /I /Y backend\* "%SPACENAME%\backend\"

echo Copying frontend files...
xcopy /E /I /Y frontend\ "%SPACENAME%\frontend\"

echo Copying Dockerfile...
copy /Y Dockerfile.huggingface "%SPACENAME%\Dockerfile"

echo Copying requirements...
copy /Y backend\requirements_minimal.txt "%SPACENAME%\"

REM Commit and push
echo.
echo ========================================
echo  Step 5: Pushing to Hugging Face...
echo ========================================
echo.

cd "%SPACENAME%"

git add .
git commit -m "Deploy face attendance system"
git push

echo.
echo ========================================
echo  Deployment Complete!
echo ========================================
echo.
echo Your app will be live at:
echo https://huggingface.co/spaces/%USERNAME%/%SPACENAME%
echo.
echo Build time: 5-10 minutes
echo.

pause
