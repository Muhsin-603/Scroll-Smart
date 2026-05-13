# Build script for Scroll-toungue

# Ensure pyinstaller is installed
pip install pyinstaller

# Run pyinstaller with necessary flags
# --onefile: Create a single executable
# --noconsole: Hide the console window
# --collect-all mediapipe: Ensure all mediapipe dependencies/data are included
# --add-data: Include any other assets if needed
python -m PyInstaller --onefile --noconsole --collect-all mediapipe --name "Scroll-toungue" main.py

Write-Host "Build complete! Check the 'dist' folder for the executable."
