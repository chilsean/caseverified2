# Birth Certificate Verification System

This is a **Streamlit web application** that verifies birth certificate authenticity using **OCR, edge detection, and image analysis**.

## Fix for Tesseract Not Found Issue:
Tesseract OCR must be installed on the system for the app to work correctly.

### How to Fix on **Streamlit Cloud**
No manual setup is required! The app now automatically installs Tesseract on startup.

### Install Tesseract on **Linux (Ubuntu/Debian)**
```sh
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

### Install Tesseract on **Mac (Homebrew)**
```sh
brew install tesseract
```

### Install Tesseract on **Windows**
1. Download and install Tesseract from: [Tesseract Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki)
2. Add the installation path (e.g., `C:\Program Files\Tesseract-OCR`) to the system PATH.

## Deployment:
To deploy on **Streamlit Cloud**:
1. Ensure your GitHub repository is updated with this new `app.py`.
2. Push the repository to **GitHub**.
3. Redeploy the app.

🚀 **Enjoy automated birth certificate verification!**
