**RHBL Infrastructure: Reality-Human Boundary Layer**
RHBL is an advanced multi-layered detection framework designed to verify human authenticity and physical reality consistency in digital environments. It utilizes computer vision, bio-signal processing, and psychological analysis to establish a "Final Trust Judgment" score.

Core Infrastructure Layers
The system operates across four specialized layers:

Layer A: Human Authenticity: Uses MediaPipe FaceMesh and rPPG (Remote Photoplethysmography) to extract biological pulse signals from forehead ROI frames.

Layer B: Manipulation Risk: Analyzes audio and text for psychological triggers (urgency, fear, authority) using OpenAI Whisper for transcription and pattern-matching rules.

Layer C: Reality Consistency: Validates skeletal motion against physics-based, temporal, and biological consistency models to detect deepfakes or synthetic overlays.

Layer D: Dynamic Trust Fusion: A weighted scoring engine that fuses data from all layers to generate a real-time trust percentage based on signal quality.

🚀 Getting Started
1. Prerequisites
Python 3.10+

Node.js & npm (for the React dashboard)

FFmpeg: Required for audio transcription. Ensure ffmpeg is installed and added to your System PATH.

2. Backend Installation
Navigate to the root directory and install the required Python libraries:

Bash

pip install fastapi uvicorn mediapipe opencv-python numpy openai-whisper sqlalchemy
3. Frontend Installation
Navigate to the frontend directory and install dependencies:

Bash

npm install lucide-react

Running the System
Step 1: Start the Backend
Run the FastAPI server on port 7000:

Bash

uvicorn backend.main:app --host 127.0.0.1 --port 7000 --reload
The database rhbl_logs.db will initialize automatically upon startup.

Step 2: Start the Frontend
In a new terminal, launch the React development server:

Bash

npm run dev


Testing Features
Persistent Manipulation Risk (Red Bar)
The system now preserves manipulation data until a new input is provided. You can test it in two ways:

Text Test: Use the "Test text triggers" box in the header. Type phrases like "Act now, or the police will be called" to trigger urgency and fear patterns.

Audio Test: Click "ANALYZE AUDIO" and upload a .wav file. The backend will transcribe the speech and update the risk score based on detected keywords.

Reality Consistency (Purple Bar)
Move in front of the camera for at least 3 seconds. The system requires a buffer of 15 frames of skeletal data to begin calculating physical consistency scores.

Biological Pulse (rPPG Wave)
Ensure your face is well-lit and clearly visible. The cyan graph at the bottom displays the extracted heart rate signal from the forehead.


Project Structure
backend/main.py: FastAPI entry point and API endpoints.

backend/logic.py: The SentinelEngine class handling the live processing pipeline and state management.

layer_b/utils/audio_to_text.py: Whisper integration for speech-to-text transcription.

layer_d/trust_fusion.py: Scoring algorithms for multi-layer data integration.

src/App.jsx: React-based real-time monitoring dashboard with explicit color-coded gauges.
