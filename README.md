# Ramify RR 🎬🌍

**Cross-lingual video translator with AI voice cloning**

Translate videos from one language to another while preserving the original speaker's voice — powered by Whisper, Google Translate, and ElevenLabs.

---

## The 6 W's

| W | Answer |
|---|--------|
| **What** | An AI-powered web application that converts videos from one language to another with the same voice. Upload a video in Telugu, get it back in English — with the original speaker's voice preserved via AI voice cloning. |
| **Who** | Content creators, language learners, businesses expanding globally, educators, and anyone who watches or produces multilingual video content on platforms like YouTube and Instagram. |
| **Why** | Social media is full of videos in different languages (Telugu, Hindi, English, etc). This tool breaks the language barrier by automatically translating video speech while keeping the original voice, making content accessible worldwide. |
| **When** | Whenever you need to consume or publish video content across languages — dubbing YouTube videos, translating educational content, making regional content accessible to a global audience. |
| **Where** | A web application accessible from any browser — desktop or mobile. Upload your video, select the target language, and download the translated result. |
| **How** | Upload a video file → AI extracts and transcribes the speech (Whisper) → translates the text (Google Translate) → generates speech in the target language with the original voice (ElevenLabs) → merges the new audio back into the video. |

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Video File │────▶│ Audio Extract │────▶│ Whisper STT     │
│  (Upload)   │     │ (moviepy)     │     │ (Transcription) │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                                                   ▼
                    ┌──────────────┐     ┌─────────────────┐
                    │  Merge A/V   │◀────│ Google Translate │
                    │  (moviepy)   │     │ (Translation)    │
                    └──────┬───────┘     └────────┬────────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐     ┌─────────────────┐
                    │ Output Video │     │ ElevenLabs TTS   │
                    │ (Download)   │     │ (Voice Cloning)  │
                    └──────────────┘     └─────────────────┘
```

### Pipeline Steps

1. **Extract Audio** — Pulls the audio track from the uploaded video using `moviepy`/`ffmpeg`.
2. **Speech-to-Text** — Transcribes the audio using OpenAI's Whisper model (runs locally, no API key needed). Automatically detects the source language.
3. **Machine Translation** — Translates the transcribed text to the target language using Google Translate.
4. **Text-to-Speech** — Generates speech in the target language:
   - **With ElevenLabs** (recommended): Uses voice cloning to preserve the original speaker's voice. Requires an API key.
   - **Without ElevenLabs** (fallback): Uses Google Text-to-Speech (gTTS) — functional but uses a generic voice.
5. **Audio-Video Merge** — Replaces the original audio with the translated audio and produces the final video.

---

## Supported Languages

English, Hindi, Telugu, Tamil, Kannada, Malayalam, Marathi, Bengali, Gujarati, Punjabi, Urdu, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese (Simplified), Arabic.

---

## Quick Start

### Prerequisites

- Python 3.10+
- `ffmpeg` installed on your system

### Installation

```bash
# Clone the repository
git clone https://github.com/Rishilovers8/coding-ai-agent.git
cd coding-ai-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
```

### Configuration

Edit `.env` to configure:

```env
# Required for voice cloning (optional — app works without it using gTTS fallback)
ELEVENLABS_API_KEY=your-api-key-here

# Whisper model size: tiny (fastest), base, small, medium, large (most accurate)
WHISPER_MODEL_SIZE=base
```

### Run

```bash
python run.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

### Production

```bash
gunicorn run:app --bind 0.0.0.0:5000 --timeout 600 --workers 2
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask (Python) |
| Speech-to-Text | OpenAI Whisper |
| Translation | Google Translate (googletrans) |
| Voice Cloning TTS | ElevenLabs API |
| Fallback TTS | gTTS |
| Video Processing | moviepy + ffmpeg |
| Frontend | Vanilla HTML/CSS/JS |

---

## Project Structure

```
ramify-rr/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration from environment
│   ├── pipeline.py         # Core translation pipeline
│   ├── routes.py           # Flask routes and API
│   ├── static/
│   │   ├── css/style.css   # UI styles
│   │   └── js/app.js       # Frontend logic
│   └── templates/
│       └── index.html      # Main page template
├── uploads/                # Temporary upload storage
├── outputs/                # Translated video output
├── run.py                  # Application entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## API

### `POST /translate`

Translate a video file.

**Form Data:**
- `video` (file, required) — Video file to translate
- `target_lang` (string) — Target language code (default: `en`)
- `use_elevenlabs` (string) — `"true"` to use voice cloning
- `voice_id` (string) — ElevenLabs voice ID (optional)

**Response:**
```json
{
  "success": true,
  "download_url": "/download/abc123_translated.mp4",
  "source_lang": "Telugu",
  "target_lang": "English",
  "transcription": "Original text...",
  "translation": "Translated text..."
}
```

### `GET /health`

Health check endpoint.

---

## License

MIT
