import time

class GestureInterpreter:
    def __init__(self):
        self.last_gesture = None
        self.last_time = time.time()
        self.cooldown = 0.1  # seconds
        
    def interpret(self, tongue_centroid, occlusion_score=None, refs=None):
        # Only identify scrolling down when seeing tongue
        if tongue_centroid is not None:
            return "SCROLL_DOWN"
            
        return "NEUTRAL"
