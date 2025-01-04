import customtkinter as ctk
import sys
from modules.console_frame import ConsoleFrame
from modules.login_frame import LoginFrame
from modules.upload_frame import UploadFrame
from modules.path_frame import PathFrame
from modules.checkbox_frame import CheckboxFrame
from modules.api_client import ImmichClient


class GimmichApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("gimmich")
        self.geometry("1200x600")  # Set a default size for the window

        self.client = ImmichClient()  # Create the API client.

        # Configure row and column weights for resizing
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Add Tabview
        self.tab_view = ctk.CTkTabview(self)  # Create a Tabview
        self.tab_view.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        # Create Upload Tab
        self.upload_tab = self.tab_view.add("Upload")
        self.init_upload_tab(self.upload_tab)

        # Create Download Tab
        self.download_tab = self.tab_view.add("Download")
        self.init_download_tab(self.download_tab)

    def init_upload_tab(self, tab):
        """Initialize the Upload tab with existing UI elements."""
        tab.grid_rowconfigure(0, weight=1)  # Main frame resizable
        tab.grid_columnconfigure(0, weight=1)  # Main frame resizable

        # Main Frame
        main_frame = ctk.CTkFrame(tab)
        main_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        main_frame.grid_rowconfigure(0, weight=1)  # Top frame resizable
        main_frame.grid_rowconfigure(1, weight=100)  # Console frame resizable
        main_frame.grid_columnconfigure(0, weight=1)

        # Top Frame
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.grid(row=0, column=0, padx=2, pady=2, sticky="new")
        top_frame.grid_columnconfigure(0, weight=1)  # Login frame fixed size
        top_frame.grid_columnconfigure(1, weight=1)  # Path frame resizable
        top_frame.grid_columnconfigure(2, weight=1)  # Checkbox frame fixed size
        top_frame.grid_columnconfigure(3, weight=1)  # Upload frame fixed size

        # Console Frame
        console_text = ConsoleFrame(main_frame)
        console_text.grid(row=1, column=0, padx=2, pady=2, sticky="nsew")
        console_text.grid_rowconfigure(1, weight=1)
        console_text.grid_columnconfigure(0, weight=1)

        # Login Frame
        login_frame = LoginFrame(top_frame, self.client)
        login_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        # Path Frame
        path_frame = PathFrame(parent=top_frame)
        path_frame.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

        # Checkbox Frame
        checkbox_frame = CheckboxFrame(top_frame)
        checkbox_frame.grid(row=0, column=2, padx=2, pady=2, sticky="nsew")

        # Upload Frame
        upload_frame = UploadFrame(top_frame, path_frame, checkbox_frame, login_frame, self.client)
        upload_frame.grid(row=0, column=3, padx=2, pady=2, sticky="nsew")

    def init_download_tab(self, tab):
        """Initialize the Download tab."""
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)

        # Empty frame for now
        empty_frame = ctk.CTkFrame(tab)
        empty_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

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
