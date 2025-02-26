# YouTube Automation with LLM and OpenCV

This project automates YouTube content creation by generating random stories using an LLM, combining them with video using OpenCV, adding audio narration, generating a title and description, and publishing the video—all without manual intervention.

## Features
- **Story Generation:** Uses an LLM to generate random stories.
- **Video Creation:** Uses OpenCV to create a video with relevant images and animations.
- **Audio Narration:** Converts text to speech and overlays it onto the video.
- **Title & Description Generation:** Uses LLM to create an optimized YouTube title and description.
- **YouTube Upload Automation:** Logs in and uploads the video automatically.
- **Fully Hands-Free:** No manual steps required.

## Requirements
- Python 3.9+
- Ollama (for LLM model inference)
- OpenCV (`cv2`)
- `gTTS` (Google Text-to-Speech)
- Selenium (for YouTube login automation)
- `moviepy` (for video processing)

## Installation
```sh
pip install opencv-python gtts selenium moviepy pytube
```

## Setup
### 1. Configure Ollama
Install Ollama and set up your preferred LLM model:
```sh
curl -fsSL https://ollama.com/install.sh | sh
ollama pull your-model-name
```
Set the model name in the `.env` file:
```sh
MODEL_NAME=your-model-name
```

### 2. Configure YouTube Login
Use Selenium to log in to YouTube. Make sure you have ChromeDriver installed.
```sh
# Update ChromeDriver if needed
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE -O chromedriver
chmod +x chromedriver
mv chromedriver /usr/local/bin/
```

### 3. Run the Automation Script
```sh
python main.py
```

## How It Works
1. **Generate Story**: Uses Ollama LLM to create a unique short story.
2. **Generate Video**: Finds relevant images and animations using OpenCV and `moviepy`.
3. **Generate Audio**: Converts the story to speech using `gTTS`.
4. **Compile Video**: Merges audio, images, and text overlays.
5. **Generate Metadata**: Creates an engaging title and description.
6. **Upload to YouTube**: Logs in using Selenium and uploads the video.

## Future Enhancements
- Add AI-powered thumbnail generation.
- Use Whisper AI for better narration.
- Automate hashtag and tag selection for SEO.

## Disclaimer
Use this script responsibly and ensure compliance with YouTube's policies.

## License
MIT License

