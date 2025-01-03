import customtkinter as ctk
import sys
from modules.console_frame import ConsoleFrame
from modules.login_frame import LoginFrame
from modules.upload_frame import UploadFrame
from modules.path_frame import PathFrame
from modules.checkbox_frame import CheckboxFrame
from modules.api_client import ImmichClient

# Create the customtkinter app


class GimmichApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("gimmich")

        self.client = ImmichClient()  # Create the API client.
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)  # Main container frame
        self.main_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.main_frame.grid_rowconfigure(0, weight=1)  # Top frame (fixed size)
        self.main_frame.grid_rowconfigure(1, weight=1)  # Empty space if needed
        self.main_frame.grid_rowconfigure(2, weight=1)  # Console log (resizable)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.top_frame = ctk.CTkFrame(self.main_frame)  # Frame for buttons and info
        self.top_frame.grid(row=0, column=0, padx=5, pady=5, sticky="new")

        self.console_text = ConsoleFrame(self.main_frame)  # Console log
        self.console_text.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        self.top_frame.grid_columnconfigure(0, weight=1)  # Login frame (fixed size)
        self.top_frame.grid_columnconfigure(1, weight=1)  # Path frame (resizable)
        self.top_frame.grid_columnconfigure(2, weight=1)  # Checkbox frame (fixed size)
        self.top_frame.grid_columnconfigure(3, weight=1)  # Upload frame (fixed size)

        self.path_frame = PathFrame(parent=self.top_frame)  # Path frame
        self.path_frame.grid(row=1, column=2, padx=5, pady=5, sticky="ns")

        self.checkbox_frame = CheckboxFrame(self.top_frame)  # Checkbox frame
        self.checkbox_frame.grid(row=1, column=3, padx=5, pady=5, sticky="ns")
        self.checkbox_states = self.checkbox_frame.get_states()

        self.login_frame = LoginFrame(self.top_frame, self.client)  # Login frame
        self.login_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsw")

        self.upload_frame = UploadFrame(self.top_frame, self.path_frame, self.checkbox_frame, self.login_frame,
                                        self.client)  # Upload Frame
        self.upload_frame.grid(row=1, column=4, padx=5, pady=5, sticky="ns")

    def on_closing(self):
        """Restore sys.stdout before closing"""
        sys.stdout = sys.__stdout__
        self.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    gimmich = GimmichApp()
    gimmich.protocol("WM_DELETE_WINDOW", gimmich.on_closing)
    gimmich.mainloop()
