import whisper
import tempfile
import os
import shutil

# load whisper model once
model = whisper.load_model("base")

def audio_to_text(file):
    # Check if FFmpeg is available in the system path before starting
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg not found. Please add FFmpeg to your Windows System PATH.")

    # Save uploaded file to temp wav
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
        temp.write(file.file.read())
        temp_path = temp.name

    try:
        # Transcribe audio
        result = model.transcribe(temp_path)
        return result["text"]
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)