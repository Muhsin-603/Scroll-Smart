import pyautogui
import time
import threading

class ActionEngine:
    def __init__(self):
        pyautogui.FAILSAFE = True
        self.scroll_momentum = 0
        self.friction = 0.85 # Decay rate
        self.max_momentum = 800
        self.acceleration = 150
        
        # Start a background thread for smooth scrolling ticks
        self.running = True
        self.scroll_thread = threading.Thread(target=self._scroll_tick_loop, daemon=True)
        self.scroll_thread.start()

    def _scroll_tick_loop(self):
        while self.running:
            if abs(self.scroll_momentum) > 1:
                # Apply the current momentum
                pyautogui.scroll(int(self.scroll_momentum))
                # Apply friction (decay)
                self.scroll_momentum *= self.friction
            else:
                self.scroll_momentum = 0
            
            time.sleep(0.01) # 100Hz smooth tick

    def perform(self, gesture):
        if gesture == "SCROLL_DOWN":
            # Add to momentum (negative for down)
            self.scroll_momentum -= self.acceleration
            if self.scroll_momentum < -self.max_momentum:
                self.scroll_momentum = -self.max_momentum
        elif gesture == "SCROLL_UP":
            # Supporting UP just in case, though user asked for Down only
            self.scroll_momentum += self.acceleration
            if self.scroll_momentum > self.max_momentum:
                self.scroll_momentum = self.max_momentum

    def stop(self):
        self.running = False
