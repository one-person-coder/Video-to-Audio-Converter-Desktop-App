# 🎬 Video to Audio Converter (Python + MoviePy + CustomTkinter)

A modern, fully functional GUI application that converts video files into MP3 audio using Python.  
The app features a clean CustomTkinter interface, multi-file batch conversion, progress tracking, error handling, and automatic output folder creation.

---

## 🚀 Features

- Convert videos into **high-quality MP3 audio**
- Support for multiple video formats
- Batch conversion (multiple files at once)
- Modern UI powered by **CustomTkinter**
- Real-time progress bar and status updates
- Automatic "Converted Audio" output folder
- System notifications (if Plyer is installed)
- Smooth multithreading (no UI freezing)
- Safe cancel/stop conversion button
- Scrollable UI for file list and video format list

---

## 📁 Supported Video Formats

MP4, MKV, AVI, MOV, WMV, FLV, WEBM, OGG, 3GP, TS, VOB

---

**Note:** `tkinter`, `threading`, `os`, `sys`, and `time` are built-in Python modules.

---

## Preview Image

![Project Preview Image](/assets/preview.png)

## 🛠️ Installation

### 1. Install Python (3.10+ recommended)

Check your Python version:

```bash
python --version
```

### 2. Download or Clone the Project

```bash
git clone https://github.com/one-person-coder/Video-to-Audio-Converter-Desktop-App.git
cd Video-to-Audio-Converter-Desktop-App
```

### 3. Create a Virtual Environment (recommended)

#### 1. Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### 2. Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Running the Application

Start the GUI app:

```bash
python main.py
```

### 6. Output Location

For every selected video, the application automatically creates:

```bash
Converted Audio/
```

inside the source video’s folder, and stores the MP3 file there.