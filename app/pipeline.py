"""
Ramify RR - Core Translation Pipeline

Pipeline steps:
  1. Extract audio from video (moviepy / ffmpeg)
  2. Speech-to-Text using OpenAI Whisper
  3. Machine Translation using googletrans
  4. Voice Cloning TTS via ElevenLabs (or fallback to gTTS)
  5. Merge translated audio back into the video
"""

import os
import uuid
import logging
import subprocess
import tempfile
from pathlib import Path

import whisper
from googletrans import Translator
from moviepy.editor import VideoFileClip, AudioFileClip
from pydub import AudioSegment

from app.config import Config

logger = logging.getLogger(__name__)

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ur": "Urdu",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-cn": "Chinese (Simplified)",
    "ar": "Arabic",
}

_whisper_model = None


def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        model_size = Config.WHISPER_MODEL_SIZE
        logger.info("Loading Whisper model: %s", model_size)
        _whisper_model = whisper.load_model(model_size)
    return _whisper_model


def extract_audio(video_path: str, output_dir: str) -> str:
    """Extract audio track from a video file as WAV."""
    audio_filename = f"{uuid.uuid4().hex}_extracted.wav"
    audio_path = os.path.join(output_dir, audio_filename)

    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path, codec="pcm_s16le", logger=None)
    video.close()

    logger.info("Extracted audio to %s", audio_path)
    return audio_path


def transcribe_audio(audio_path: str) -> dict:
    """Transcribe audio using OpenAI Whisper. Returns detected language and text."""
    model = get_whisper_model()
    logger.info("Transcribing audio: %s", audio_path)

    result = model.transcribe(audio_path)

    detected_language = result.get("language", "unknown")
    text = result.get("text", "")
    segments = result.get("segments", [])

    logger.info("Detected language: %s | Transcription length: %d chars", detected_language, len(text))
    return {
        "language": detected_language,
        "text": text,
        "segments": segments,
    }


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate text from source language to target language."""
    translator = Translator()
    logger.info("Translating from %s to %s (%d chars)", source_lang, target_lang, len(text))

    chunks = _split_text(text, max_chars=4500)
    translated_parts = []

    for chunk in chunks:
        result = translator.translate(chunk, src=source_lang, dest=target_lang)
        translated_parts.append(result.text)

    translated = " ".join(translated_parts)
    logger.info("Translation complete: %d chars", len(translated))
    return translated


def _split_text(text: str, max_chars: int = 4500) -> list:
    """Split text into chunks respecting sentence boundaries."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""
    sentences = text.replace(". ", ".|").replace("? ", "?|").replace("! ", "!|").split("|")

    for sentence in sentences:
        if len(current) + len(sentence) > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current += " " + sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks


def generate_speech_elevenlabs(text: str, target_lang: str, output_dir: str, voice_id: str = None) -> str:
    """Generate speech using ElevenLabs voice cloning API."""
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save

    api_key = Config.ELEVENLABS_API_KEY
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY is not set. Please configure it in your .env file.")

    client = ElevenLabs(api_key=api_key)

    if not voice_id:
        voices = client.voices.get_all()
        if voices.voices:
            voice_id = voices.voices[0].voice_id
            logger.info("Using default voice: %s", voice_id)
        else:
            raise ValueError("No voices available in your ElevenLabs account.")

    audio = client.generate(
        text=text,
        voice=voice_id,
        model=Config.ELEVENLABS_MODEL,
    )

    output_filename = f"{uuid.uuid4().hex}_speech.mp3"
    output_path = os.path.join(output_dir, output_filename)
    save(audio, output_path)

    logger.info("ElevenLabs speech saved to %s", output_path)
    return output_path


def generate_speech_gtts(text: str, target_lang: str, output_dir: str) -> str:
    """Fallback: generate speech using Google Text-to-Speech (no voice cloning)."""
    from gtts import gTTS

    lang_code = target_lang if len(target_lang) == 2 else target_lang.split("-")[0]

    output_filename = f"{uuid.uuid4().hex}_speech.mp3"
    output_path = os.path.join(output_dir, output_filename)

    tts = gTTS(text=text, lang=lang_code)
    tts.save(output_path)

    logger.info("gTTS speech saved to %s", output_path)
    return output_path


def merge_audio_video(video_path: str, audio_path: str, output_dir: str) -> str:
    """Replace the original audio in the video with the new translated audio."""
    output_filename = f"{uuid.uuid4().hex}_translated.mp4"
    output_path = os.path.join(output_dir, output_filename)

    video = VideoFileClip(video_path)
    new_audio = AudioFileClip(audio_path)

    if new_audio.duration > video.duration:
        final_video = video.set_audio(new_audio.subclip(0, video.duration))
    elif new_audio.duration < video.duration:
        final_video = video.set_duration(new_audio.duration).set_audio(new_audio)
    else:
        final_video = video.set_audio(new_audio)

    final_video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        logger=None,
    )

    video.close()
    new_audio.close()

    logger.info("Merged video saved to %s", output_path)
    return output_path


def run_pipeline(
    video_path: str,
    target_lang: str,
    use_elevenlabs: bool = False,
    voice_id: str = None,
    progress_callback=None,
) -> dict:
    """
    Run the full translation pipeline on a video file.

    Args:
        video_path: Path to the input video.
        target_lang: Target language code (e.g. 'en', 'hi', 'te').
        use_elevenlabs: Whether to use ElevenLabs for voice cloning TTS.
        voice_id: Optional ElevenLabs voice ID.
        progress_callback: Optional callback(step, message) for progress updates.

    Returns:
        Dict with keys: output_video, source_lang, transcription, translation.
    """
    output_dir = Config.OUTPUT_FOLDER
    os.makedirs(output_dir, exist_ok=True)

    def update(step, msg):
        logger.info("[Step %d] %s", step, msg)
        if progress_callback:
            progress_callback(step, msg)

    update(1, "Extracting audio from video...")
    audio_path = extract_audio(video_path, output_dir)

    update(2, "Transcribing audio with Whisper...")
    transcription = transcribe_audio(audio_path)
    source_lang = transcription["language"]
    source_text = transcription["text"]

    if not source_text.strip():
        raise ValueError("No speech detected in the video. Please upload a video with clear audio.")

    update(3, f"Translating from {source_lang} to {target_lang}...")
    translated_text = translate_text(source_text, source_lang, target_lang)

    update(4, "Generating translated speech...")
    if use_elevenlabs and Config.ELEVENLABS_API_KEY:
        speech_path = generate_speech_elevenlabs(translated_text, target_lang, output_dir, voice_id)
    else:
        speech_path = generate_speech_gtts(translated_text, target_lang, output_dir)

    update(5, "Merging translated audio with video...")
    output_video = merge_audio_video(video_path, speech_path, output_dir)

    # Clean up intermediate files
    for f in [audio_path, speech_path]:
        try:
            os.remove(f)
        except OSError:
            pass

    update(6, "Done!")

    return {
        "output_video": output_video,
        "source_lang": source_lang,
        "source_lang_name": LANGUAGE_MAP.get(source_lang, source_lang),
        "target_lang": target_lang,
        "target_lang_name": LANGUAGE_MAP.get(target_lang, target_lang),
        "transcription": source_text,
        "translation": translated_text,
    }
