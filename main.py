import tkinter as tk
from PIL import ImageTk
import pyautogui
import pytesseract


class InitialWindow(tk.Tk):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.title("Screen Capture")

        btn_capture = tk.Button(self, text="Capture", command=self.start_capture, bg="black", fg="white")
        btn_capture.pack(pady=20)

    def start_capture(self):
        self.destroy()
        self.app.capture_screen()


class TextDisplayWindow(tk.Tk):
    def __init__(self, text):
        super().__init__()
        self.title("Recognized Text")
        self.txt_display = tk.Text(self)
        self.update_text(text)
        self.txt_display.pack(padx=10, pady=10)

    def update_text(self, new_text):
        self.txt_display.insert(tk.END, new_text + "\n\n")


class CaptureRegion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.text_display_window = None
        self.withdraw()  # Hide the main window
        self.initial_window = InitialWindow(self)

    def capture_screen(self):
        self.screenshot = pyautogui.screenshot()
        self.win_width = 800
        self.win_height = 600
        scale_x = self.win_width / self.screenshot.width
        scale_y = self.win_height / self.screenshot.height
        self.scale_factor = min(scale_x, scale_y)
        self.screenshot_resized = self.screenshot.resize(
            (int(self.screenshot.width * self.scale_factor), int(self.screenshot.height * self.scale_factor)))
        self.screenshot_tk = ImageTk.PhotoImage(self.screenshot_resized)

        self.canvas = tk.Canvas(self, width=self.screenshot_resized.width, height=self.screenshot_resized.height,
                                cursor="cross")
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.screenshot_tk)
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.canvas.bind("<ButtonPress-1>", self.start_rect)
        self.canvas.bind("<B1-Motion>", self.dragging)
        self.canvas.bind("<ButtonRelease-1>", self.capture_selected_region)

        self.deiconify()  # Show the main window after setting it up

    def start_rect(self, event):
        self.start_x = event.x / self.scale_factor
        self.start_y = event.y / self.scale_factor
        if not self.rect:
            self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red')

    def dragging(self, event):
        self.canvas.coords(self.rect, self.start_x * self.scale_factor, self.start_y * self.scale_factor, event.x,
                           event.y)

    def capture_selected_region(self, event):
        cur_x = event.x / self.scale_factor
        cur_y = event.y / self.scale_factor
        x1 = min(self.start_x, cur_x)
        y1 = min(self.start_y, cur_y)
        x2 = max(self.start_x, cur_x)
        y2 = max(self.start_y, cur_y)
        selected_region = self.screenshot.crop((x1, y1, x2, y2))
        text = pytesseract.image_to_string(selected_region)

        if self.text_display_window:
            self.text_display_window.update_text(text)
        else:
            self.text_display_window = TextDisplayWindow(text)
            self.text_display_window.mainloop()


app = CaptureRegion()
app.mainloop()
