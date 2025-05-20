# Webcam ASCII Art Converter

This Python application captures video from your webcam and converts it to real-time ASCII art. The program uses OpenCV for webcam capture and converts each frame into ASCII characters that are displayed in the terminal. The ASCII art automatically adjusts to your terminal window size!

## Requirements
- Python 3.8+
- Webcam
- Terminal

## Installation
1. Clone this repository
2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Unix/macOS
# or
.\venv\Scripts\activate  # On Windows
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage
Run the main script:
```bash
python ascii_webcam.py
```

### Controls
- Press 'q' to quit the application
- Press 's' to save the current ASCII frame
- Resize your terminal window to adjust the ASCII art resolution!
