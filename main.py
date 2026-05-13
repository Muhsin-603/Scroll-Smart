import cv2
import tkinter as tk
from vision_engine import VisionEngine
from tongue_detector import TongueDetector
from gesture_interpreter import GestureInterpreter
from action_engine import ActionEngine
from overlay_ui import OverlayUI
import sys

class ScrollTongueApp:
    def __init__(self):
        self.root = tk.Tk()
        self.vision = VisionEngine()
        self.detector = TongueDetector()
        self.interpreter = GestureInterpreter()
        self.actions = ActionEngine()
        self.ui = OverlayUI(self.root, self.on_close)
        
        self.cap = cv2.VideoCapture(0)
        self.running = True
        
        self.process_loop()
        self.root.mainloop()

    def on_close(self):
        self.running = False
        self.cap.release()
        self.root.destroy()
        sys.exit()

    def process_loop(self):
        if not self.running:
            return
            
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1) # Flip for mirror effect
            landmarks = self.vision.get_landmarks(frame)
            gesture = None
            
            if landmarks:
                mouth_roi, roi_dims, refs, inner_mask = self.vision.get_mouth_roi(frame, landmarks)
                if mouth_roi is not None:
                    tongue_centroid, occlusion_score, mask = self.detector.detect(mouth_roi, refs.get('skin_color'), inner_mask)
                    gesture = self.interpreter.interpret(tongue_centroid, occlusion_score, refs)
                    
                    if gesture:
                        self.actions.perform(gesture)
                    
                    # Draw for feedback in overlay
                    self.vision.draw_landmarks(frame, landmarks)
                    if tongue_centroid:
                        # Map centroid back to frame coordinates for drawing
                        fx = roi_dims[0] + tongue_centroid[0]
                        fy = roi_dims[1] + tongue_centroid[1]
                        cv2.circle(frame, (fx, fy), 5, (0, 0, 255), -1)
                
            self.ui.update_frame(frame, gesture)
            
        self.root.after(10, self.process_loop)

if __name__ == "__main__":
    ScrollTongueApp()
