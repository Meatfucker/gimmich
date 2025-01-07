import customtkinter as ctk
import sys
from modules.console_frame import ConsoleFrame
from modules.login_frame import LoginFrame
from modules.upload_frame import UploadFrame
from modules.path_frame import PathFrame
from modules.checkbox_frame import CheckboxFrame
from modules.api_client import ImmichClient
from modules.download_frame import DownloadFrame
from modules.add_asset_frame import AddAssetFrame


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

        # Create Login Tab
        self.login_frame = None
        self.login_tab = self.tab_view.add("Login")
        self.init_login_tab(self.login_tab)

        # Create Upload Tab
        self.upload_tab = self.tab_view.add("Upload")
        self.init_upload_tab(self.upload_tab)

        # Create Download Tab
        self.download_tab = self.tab_view.add("Download")
        self.init_download_tab(self.download_tab)

    def init_login_tab(self, tab):
        """Initialize the login tab."""
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=100)

        # Console Frame
        console_text = ConsoleFrame(tab)
        console_text.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")
        console_text.grid_rowconfigure(1, weight=1)
        console_text.grid_columnconfigure(0, weight=1)

        # Login Frame
        self.login_frame = LoginFrame(tab, self.client)
        self.login_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

    def init_upload_tab(self, tab):
        """Initialize the Upload tab."""
        tab.grid_rowconfigure(0, weight=1)  # Main frame resizable
        tab.grid_rowconfigure(1, weight=1)  # Main frame resizable
        tab.grid_columnconfigure(0, weight=1)  # Main frame resizable
        tab.grid_columnconfigure(1, weight=1)  # Path frame resizable


        # Path Frame
        path_frame = PathFrame(parent=tab)
        path_frame.grid(row=0, column=0, padx=10, pady=2, sticky="nsew", rowspan=2)

        # Checkbox Frame
        checkbox_frame = CheckboxFrame(tab)
        checkbox_frame.grid(row=0, column=1, padx=10, pady=2, sticky="nsew")

        # Upload Frame
        upload_frame = UploadFrame(tab, path_frame, checkbox_frame, self.login_frame, self.client)
        upload_frame.grid(row=1, column=1, padx=10, pady=2, sticky="sew")

    def init_download_tab(self, tab):
        """Initialize the Download tab."""
        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        download_frame = DownloadFrame(tab, self.login_frame, self.client)
        download_frame.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

        add_asset_frame = AddAssetFrame(tab, self.client, download_frame)
        add_asset_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

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
