# Gesture and Blink Controlled System
![71oo70ExnJL _AC_SX679_](https://github.com/user-attachments/assets/d2ced40d-0aab-4318-a05c-a3b2bfa1dcf6)

## Overview
This project utilizes Python, OpenCV, and MediaPipe to create an interactive system that responds to facial blinks and hand gestures. It allows users to control laptop volume and brightness with hand movements and automatically opens/closes YouTube to play music upon detecting a double blink.

## Features
- **Face Detection**: Detects and tracks facial landmarks.
- **Blink Detection**: Identifies double blinks to trigger actions.
- **Hand Detection**: Detects and tracks hand landmarks, differentiating between left and right hands.
- **Volume Control**: Adjusts system volume based on **left hand** gestures.
- **Brightness Control**: Adjusts screen brightness based on **right hand** gestures.
- **YouTube Automation**: Opens YouTube and plays music on the first double blink. A subsequent double blink will close the YouTube window.

## Requirements
- Python 3.x (Recommended: 3.10, 3.11, or 3.12 for MediaPipe compatibility)
- OpenCV
- MediaPipe
- PyCaw (Windows only)
- screen_brightness_control
- Selenium
- webdriver_manager

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/ahaseeb003/gesture-blink-control.git
cd gesture-blink-control
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# For Windows PowerShell:
. .\venv\Scripts\Activate.ps1
# For Windows Command Prompt:
.\venv\Scripts\activate
# For Linux/macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Chrome Driver
Selenium requires a WebDriver to interact with web browsers. This project uses `webdriver_manager` to automatically download the correct ChromeDriver. However, ensure you have Google Chrome installed on your system.

## Usage

### Running the application
```bash
python main.py
```

### Controls
- **Volume Control (Left Hand)**: Extend your thumb and index finger on your **left hand**. The distance between them will control the system volume. (Calibration might be needed based on your camera and hand size).
- **Brightness Control (Right Hand)**: Extend your thumb and index finger on your **right hand**. The distance between them will adjust screen brightness.
- **YouTube Music**: Blink twice rapidly to open a new Chrome window with YouTube playing relaxing music. If the YouTube window is already open, blinking twice again will close it.

## Troubleshooting
- **Camera not detected**: Ensure your webcam is properly connected and not in use by another application.
- **Module not found errors**: Make sure all dependencies are installed as per the `Installation` section.
- **PyCaw errors on Windows**: Ensure your audio drivers are up to date.
- **Brightness control issues**: On some systems, `screen_brightness_control` might require additional permissions or specific display drivers. Refer to its documentation for more details.
- **YouTube automation issues**: Ensure Google Chrome is installed. If issues persist, check your internet connection and verify YouTube\"s layout hasn\"t changed significantly, which might break the Selenium element finding.

## Contributing
Feel free to fork the repository, make improvements, and submit pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

