import customtkinter as ctk
import sys


class ConsoleFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.main_frame = ctk.CTkTextbox(self, wrap="word", height=200)  # Console log
        self.main_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)  # Ensure it expands properly
        self.grid_columnconfigure(0, weight=1)

        # Redirect console output to the Text widget
        sys.stdout = self

    def write(self, message):
        """Write message to the console and scroll to the bottom."""
        self.main_frame.insert("end", message)
        self.main_frame.see("end")

    def flush(self):
        """Required for compatibility with sys.stdout."""
        pass