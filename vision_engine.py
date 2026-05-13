import cv2
import mediapipe as mp
import numpy as np

class VisionEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_draw.DrawingSpec(thickness=1, circle_radius=1)

    def get_landmarks(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]
        return None

    def get_mouth_roi(self, frame, landmarks):
        ih, iw, _ = frame.shape
        # Mouth landmarks (indices for inner and outer lips)
        # Using a bounding box around lip landmarks
        lip_indices = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 185, 40, 39, 37, 0, 267, 269, 270, 409]
        
        points = []
        for idx in lip_indices:
            lm = landmarks.landmark[idx]
            points.append((int(lm.x * iw), int(lm.y * ih)))
        
        if not points:
            return None, None
            
        x, y, w, h = cv2.boundingRect(np.array(points))
        
        # Expand ROI slightly
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(iw - x, w + 2 * padding)
        h = min(ih - y, h + 2 * padding)
        
        # Key reference points: Inner lip top (13) and bottom (14)
        top_inner = landmarks.landmark[13]
        bot_inner = landmarks.landmark[14]
        
        # Forehead landmark for skin reference (landmark 10)
        fh = landmarks.landmark[10]
        fh_x, fh_y = int(fh.x * iw), int(fh.y * ih)
        # Sample a small area around forehead
        fh_roi = frame[max(0, fh_y-10):min(ih, fh_y+10), max(0, fh_x-10):min(iw, fh_x+10)]
        avg_skin_color = np.mean(fh_roi, axis=(0, 1)) if fh_roi.size > 0 else np.array([0, 0, 0])
        
        # Proximity and shape references
        refs = {
            'top_y': top_inner.y * ih,
            'bot_y': bot_inner.y * ih,
            'top_x': top_inner.x * iw,
            'bot_x': bot_inner.x * iw,
            'left_x': landmarks.landmark[61].x * iw,
            'right_x': landmarks.landmark[291].x * iw,
            'mouth_h': (bot_inner.y - top_inner.y) * ih,
            'mouth_w': (landmarks.landmark[291].x - landmarks.landmark[61].x) * iw,
            'face_w': (landmarks.landmark[454].x - landmarks.landmark[234].x) * iw,
            'skin_color': avg_skin_color
        }
        
        # 3. Create a precise mask for the inner mouth area to avoid lip/skin interference
        # Inner lip indices: 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78, 191, 80, 81, 82
        inner_lip_indices = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]
        inner_points = []
        for idx in inner_lip_indices:
            lm = landmarks.landmark[idx]
            inner_points.append((int(lm.x * iw - x), int(lm.y * ih - y)))
        
        inner_mask = np.zeros((h, w), dtype=np.uint8)
        if inner_points:
            cv2.fillPoly(inner_mask, [np.array(inner_points)], 255)
        
        mouth_roi = frame[y:y+h, x:x+w]
        return mouth_roi, (x, y, w, h), refs, inner_mask

    def draw_landmarks(self, frame, landmarks):
        self.mp_draw.draw_landmarks(
            image=frame,
            landmark_list=landmarks,
            connections=self.mp_face_mesh.FACEMESH_LIPS,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
        )
