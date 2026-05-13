import tkinter as tk
from PIL import Image, ImageTk
import cv2

class OverlayUI:
    def __init__(self, root, on_close_callback):
        self.root = root
        self.root.title("Scroll-toungue Overlay")
        self.root.geometry("300x250+50+50")
        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.config(bg="black")
        
        # Draggable window logic
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        
        self.canvas = tk.Canvas(root, width=300, height=200, bg="black", highlightthickness=0)
        self.canvas.pack()
        
        self.status_label = tk.Label(root, text="Starting...", fg="cyan", bg="black", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=5)
        
        self.close_btn = tk.Button(root, text="X", command=on_close_callback, bg="red", fg="white", bd=0, font=("Arial", 10, "bold"))
        self.close_btn.place(x=280, y=0, width=20, height=20)
        
        self.image_id = None
        self._offset_x = 0
        self._offset_y = 0

    def start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def do_move(self, event):
        x = self.root.winfo_x() + event.x - self._offset_x
        y = self.root.winfo_y() + event.y - self._offset_y
        self.root.geometry(f"+{x}+{y}")

    def update_frame(self, frame, gesture):
        if frame is None:
            return
            
        # Resize frame for overlay
        frame = cv2.resize(frame, (300, 200))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(image=img)
        
        if self.image_id is None:
            self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        else:
            self.canvas.itemconfig(self.image_id, image=img_tk)
        
        # Keep a reference to avoid garbage collection
        self.current_img = img_tk
        
        # Update status
        status_text = f"Gesture: {gesture if gesture else 'None'}"
        self.status_label.config(text=status_text)
        
        if gesture and gesture != "NEUTRAL":
            self.status_label.config(fg="lime")
        else:
            self.status_label.config(fg="cyan")
