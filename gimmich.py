import sys
import customtkinter as ctk
from modules.console_frame import ConsoleFrame
from modules.login_frame import LoginFrame
from modules.upload_frame import UploadFrame
from modules.path_frame import PathFrame
from modules.checkbox_frame import CheckboxFrame
from modules.api_client import ImmichClient
from modules.download_frame import DownloadFrame
from modules.add_asset_frame import AddAssetFrame
from modules.smart_frame import SmartAssetFrame


class GimmichApp(ctk.CTk):
    """This is the main gimmich app window"""
    def __init__(self):
        super().__init__()
        self.title("gimmich")  # Set a default size and name for the window
        self.geometry("1200x600")

        self.client = ImmichClient()  # Create the API client.

        self.grid_rowconfigure(0, weight=1)  # Configure row and column weights for resizing
        self.grid_columnconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self)  # Create Tabview
        self.tab_view.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

        self.login_frame = None
        self.login_tab = self.tab_view.add("Login")  # Create Login Tab
        self.init_login_tab(self.login_tab)

        self.upload_tab = self.tab_view.add("Upload")  # Create Upload Tab
        self.init_upload_tab(self.upload_tab)

        self.download_tab = self.tab_view.add("Download")  # Create Download Tab
        self.init_download_tab(self.download_tab)

    def init_login_tab(self, tab: ctk.CTkFrame):
        """Initialize the login tab."""
        tab.grid_rowconfigure(0, weight=1)  # Configure row and column weights for resizing
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=100)

        console_text = ConsoleFrame(tab)  # Create Console Frame
        console_text.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")
        console_text.grid_rowconfigure(1, weight=1)
        console_text.grid_columnconfigure(0, weight=1)

        self.login_frame = LoginFrame(tab, self.client)  # Create Login Frame
        self.login_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

    def init_upload_tab(self, tab: ctk.CTkFrame):
        """Initialize the Upload tab."""
        tab.grid_rowconfigure(0, weight=1)  # Configure row and column weights for resizing
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)

        path_frame = PathFrame(parent=tab)  # Create Path Frame
        path_frame.grid(row=0, column=0, padx=10, pady=2, sticky="nsew", rowspan=2)

        checkbox_frame = CheckboxFrame(tab)  # Create Checkbox Frame
        checkbox_frame.grid(row=0, column=1, padx=10, pady=2, sticky="nsew")

        upload_frame = UploadFrame(tab, path_frame, checkbox_frame, self.login_frame, self.client)  # Make Upload Frame
        upload_frame.grid(row=1, column=1, padx=10, pady=2, sticky="sew")

    def init_download_tab(self, tab: ctk.CTkFrame):
        """Initialize the Download tab."""
        tab.columnconfigure(0, weight=1)  # Configure row and column weights for resizing
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_columnconfigure(2, weight=1)

        download_frame = DownloadFrame(tab, self.login_frame, self.client)  # Create Download Frame
        download_frame.grid(row=0, column=2, padx=2, pady=2, sticky="nsew")

        smart_search_frame = SmartAssetFrame(tab, self.client, download_frame)
        smart_search_frame.grid(row=0, column=1, padx=2, pady=2, sticky="nsew")

        add_asset_frame = AddAssetFrame(tab, self.client, download_frame)  # Create Add Asset Frame
        add_asset_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")

    def on_closing(self):
        """Restore sys.stdout before closing"""
        sys.stdout = sys.__stdout__
        self.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  # Set themes
    ctk.set_default_color_theme("dark-blue")
    gimmich = GimmichApp()
    gimmich.protocol("WM_DELETE_WINDOW", gimmich.on_closing)
    gimmich.mainloop()
