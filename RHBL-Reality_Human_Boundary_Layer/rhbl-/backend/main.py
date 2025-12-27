import sys
import os
import threading
import time
import shutil
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from logic import SentinelEngine
from database import save_log
from layer_b.utils.audio_to_text import audio_to_text 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SentinelEngine()
camera = None
VIDEO_SOURCE = 0
current_stats = {}

def get_camera():
    global camera, VIDEO_SOURCE
    if camera is not None and camera.isOpened():
        return camera
    camera = cv2.VideoCapture(VIDEO_SOURCE)
    return camera

def db_worker():
    while True:
        time.sleep(1)
        if current_stats.get("trust_score", 0.0) > 1.0:
            save_log(current_stats)

threading.Thread(target=db_worker, daemon=True).start()

def generate_frames():
    global camera, current_stats
    while True:
        cap = get_camera()
        success, frame = cap.read()
        if not success: continue
        processed_frame, stats = engine.process_frame(frame)
        current_stats = stats
        _, buffer = cv2.imencode('.jpg', processed_frame)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stats")
def get_stats():
    return current_stats

@app.post("/analyze_audio")
async def analyze_audio(file: UploadFile = File(...)):
    global current_stats
    try:
        transcript = audio_to_text(file)
        # FIXED: Pass transcript to persistent engine state
        _, stats = engine.process_frame(np.zeros((480, 640, 3), dtype=np.uint8), current_text=transcript)
        current_stats = stats
        return {"transcript": transcript, "stats": current_stats}
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze_text")
async def analyze_text(text: str = Body(..., embed=True)):
    global current_stats
    _, stats = engine.process_frame(None, current_text=text)
    current_stats = stats
    return {"status": "success", "stats": current_stats}

@app.post("/reset_camera")
def reset_camera():
    global camera, VIDEO_SOURCE
    if camera: camera.release()
    camera = None
    VIDEO_SOURCE = 0
    return {"status": "Reset to webcam"}