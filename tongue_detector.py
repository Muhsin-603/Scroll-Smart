import cv2
import numpy as np

class TongueDetector:
    def __init__(self):
        # Initial HSV ranges for tongue detection
        # Reds/Pinks
        self.lower_red1 = np.array([0, 50, 50])
        self.upper_red1 = np.array([20, 255, 255])
        self.lower_red2 = np.array([160, 50, 50])
        self.upper_red2 = np.array([180, 255, 255])

        self.centroid_history = []
        self.history_size = 5

    def detect(self, mouth_roi, skin_color=None, inner_mask=None):
        if mouth_roi is None or mouth_roi.size == 0:
            return None, 0.0, None

        hsv = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2HSV)

        # 1. Tongue Mask (Red/Pink)
        mask1 = cv2.inRange(hsv, self.lower_red1, self.upper_red1)
        mask2 = cv2.inRange(hsv, self.lower_red2, self.upper_red2)
        tongue_mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply inner mouth spatial filter if provided
        if inner_mask is not None:
            tongue_mask = cv2.bitwise_and(tongue_mask, inner_mask)

        # Clean up mask
        kernel = np.ones((5, 5), np.uint8)
        tongue_mask = cv2.morphologyEx(tongue_mask, cv2.MORPH_OPEN, kernel)

        # Find tongue centroid
        tongue_centroid = None
        contours, _ = cv2.findContours(tongue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 100:
                M = cv2.moments(largest)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    self.centroid_history.append((cx, cy))
                    if len(self.centroid_history) > self.history_size:
                        self.centroid_history.pop(0)
                    avg_cx = int(sum(p[0] for p in self.centroid_history) / len(self.centroid_history))
                    avg_cy = int(sum(p[1] for p in self.centroid_history) / len(self.centroid_history))
                    tongue_centroid = (avg_cx, avg_cy)
        
        # 2. Occlusion Detection
        occlusion_score = 0.0
        if skin_color is not None:
            avg_mouth_color = np.mean(mouth_roi, axis=(0, 1))
            # Distance between mouth color and skin color
            color_dist = np.linalg.norm(avg_mouth_color - skin_color)
            # If color is VERY similar to skin (hand over mouth) or VERY uniform
            # Standard skin vs lip distance is usually > 30.
            if color_dist < 20: # Mouth area matches skin color (covered by hand)
                occlusion_score = 1.0
            
            # Also check for extremely low variance (covered by flat mask/object)
            gray_mouth = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2GRAY)
            if np.std(gray_mouth) < 10:
                occlusion_score = 1.0

        return tongue_centroid, occlusion_score, tongue_mask
