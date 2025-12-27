import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
from scipy.spatial import distance as dist
import sys
import os

# Adds project root to path for cross-layer imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer_c.backend.app.core.physics import physics_consistency
from layer_c.backend.app.core.temporal import temporal_consistency
from layer_c.backend.app.core.biology import bio_motion_sync
from layer_c.backend.app.core.scorer import fuse_scores
from layer_b.logic.scoring import analyze_text_logic
from layer_d.trust_fusion import fuse_layers # Integrated Layer D

class SentinelEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=0.7, refine_landmarks=True)
        self.mp_pose = mp.solutions.pose.Pose(static_image_mode=False)
        self.pose_buffer = deque(maxlen=30)
        
        self.state = "SEARCHING"
        self.score = 0.0  
        self.manipulation_prob = 0.0 # PERSISTENT STATE
        self.reality_score = 0.0 
        self.trust_score = 0.0   
        self.quality = 0.0
        self.prompt = "Looking for subject..."
        self.rppg_buffer = deque(maxlen=150)
        self.checks = {"calibrated": False, "turned": False, "smiled": False, "blinked": False}
        self.reasons = []
        self.manipulation_reasons = [] # PERSISTENT STATE

    def process_frame(self, image, current_text=""): 
        # 1. Layer B: AI Manipulation Detection
        # FIXED: Only update if text is actually provided. Do not clear if empty.
        if current_text:
            m_score, patterns, _ = analyze_text_logic(current_text)
            self.manipulation_prob = m_score
            self.manipulation_reasons = [f"Manipulation: {p}" for p in patterns]
            self.prompt = f"ANALYZED: {current_text[:20]}..."

        if image is None: return None, self._build_json([])

        image = cv2.resize(image, (640, 480))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = image.shape
        face_results = self.face_mesh.process(image_rgb)
        pose_results = self.mp_pose.process(image_rgb)
        
        if pose_results.pose_landmarks:
            self.pose_buffer.append([(lm.x, lm.y, lm.z) for lm in pose_results.pose_landmarks.landmark])
        
        if not face_results.multi_face_landmarks:
            return image, self._build_json(["No Human Detected"])

        for face_landmarks in face_results.multi_face_landmarks:
            # Pulse (rPPG) extraction
            lm151 = face_landmarks.landmark[151]
            roi_y, roi_x = int(lm151.y * h), int(lm151.x * w)
            if 10 < roi_y < h-10 and 10 < roi_x < w-10:
                self.rppg_buffer.append(np.mean(image[roi_y-5:roi_y+5, roi_x-5:roi_x+5,  green_channel:=1]))
            
            self.quality = 0.8 
            if self.state == "SEARCHING": self.score = 0.95 

        # 2. Layer C & D: Reality Consistency & Dynamic Fusion
        if len(self.pose_buffer) >= 15:
            pose_seq = np.array(list(self.pose_buffer))
            phys = physics_consistency(pose_seq)
            temp = temporal_consistency(pose_seq)
            bio = bio_motion_sync(pose_seq)
            
            self.reality_score = (0.4 * phys) + (0.3 * temp) + (0.3 * bio)

            fusion_input = [
                {"layer": "human", "score": self.score, "confidence_interval": [0.9, 1.0], "quality": self.quality, "violated_rules": []},
                {"layer": "reality", "score": self.reality_score, "confidence_interval": [0.8, 0.9], "quality": self.quality, "violated_rules": self.reasons},
                {"layer": "manipulation", "score": 1 - self.manipulation_prob, "confidence_interval": [0.7, 0.8], "quality": 1.0, "violated_rules": self.manipulation_reasons}
            ]
            self.trust_score = fuse_layers(fusion_input)["trust_score"]

        return image, self._build_json([])

    def _build_json(self, violated_rules):
        all_violations = list(set(violated_rules + self.reasons + self.manipulation_reasons))
        graph_data = []
        if len(self.rppg_buffer) > 10:
            arr = np.array(self.rppg_buffer)
            diff = np.max(arr) - np.min(arr)
            if diff > 0:
                graph_data = ((arr - np.min(arr)) / diff).tolist()

        return {
            "trust_score": self.trust_score,
            "layer_scores": {
                "human_authenticity": round(self.score * 100, 2),
                "reality_consistency": round(self.reality_score * 100, 2),
                "manipulation_risk": round(self.manipulation_prob * 100, 2) 
            },
            "violated_rules": [r for r in all_violations if "No major" not in r],
            "prompt": self.prompt,
            "rppg_wave": graph_data,
            "checks": self.checks
        }