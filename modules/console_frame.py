import customtkinter as ctk
import sys
from datetime import datetime


class ConsoleFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.main_frame = ctk.CTkTextbox(self, wrap="word", height=200)  # Console log
        self.main_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", columnspan=2)
        self.grid_rowconfigure((0, 1), weight=1)  # Ensure it expands properly
        self.grid_columnconfigure(0, weight=1)
        self.save_button = ctk.CTkButton(self, text="Save Log", command=self.save_log)
        self.save_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.copy_button = ctk.CTkButton(self, text="Copy to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        # Redirect console output to the Text widget
        sys.stdout = self

    def copy_to_clipboard(self):
        """Copy the contents of the main_frame to the clipboard."""
        log_text = self.main_frame.get("1.0", "end").strip()  # Get all text
        if log_text:  # Only copy if there's text
            self.clipboard_clear()  # Clear the clipboard
            self.clipboard_append(log_text)  # Append text to clipboard
            self.update()  # Update clipboard contents
            print("Log copied to clipboard.")  # Confirm the action in the console

    def save_log(self):
        """Save the contents of the main_frame to a log file."""
        log_text = self.main_frame.get("1.0", "end").strip()  # Get all text
        if log_text:  # Only save if there's text
            filename = datetime.now().strftime("log_%Y-%m-%d_%H-%M-%S.txt")
            with open(filename, "w") as log_file:
                log_file.write(log_text)
            print(f"Log saved to {filename}")  # Confirm the save in the console

    def write(self, message):
        """Write message to the console and scroll to the bottom."""
        self.main_frame.insert("end", message)
        self.main_frame.see("end")

    def flush(self):
        """Required for compatibility with sys.stdout."""
        pass
