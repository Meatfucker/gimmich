import customtkinter as ctk
import threading
from tkinter import filedialog


class AddAlbumPackDownloadFrame(ctk.CTkFrame):
    def __init__(self, parent, album_name, thumb, asset_ids):
        super().__init__(parent, border_width=2, border_color="gray")
        for row in range(1):
            self.rowconfigure(row, weight=1)
        self.columnconfigure(1, weight=1)
        self.parent = parent
        self.name = album_name
        self.thumb = thumb
        self.asset_ids = asset_ids
        self.thumbnail_label = ctk.CTkLabel(self, image=self.thumb, text="")
        self.thumbnail_label.grid(row=0, column=0, padx=5, pady=1)
        self.name_label = ctk.CTkLabel(self, text=f"Album: {self.name}")
        self.name_label.grid(row=0, column=1, padx=5, pady=1, sticky="ew")
        self.remove_pack_button = ctk.CTkButton(self, text="Remove", command=self.remove_album_pack)
        self.remove_pack_button.grid(row=0, column=2, padx=5, pady=1, sticky="ew")

    def remove_album_pack(self):
        self.destroy()
        for index, child in enumerate(self.parent.winfo_children()):
            child.grid(row=index, column=0, padx=5, pady=1, sticky="ew")


class DownloadFrame(ctk.CTkFrame):
    def __init__(self, parent, login_frame, client):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.client = client
        self.login_frame = login_frame
        self.queued_downloads = []  # List to hold DownloadPackFrame objects
        self.save_path = "No Path Selected"

        # Scrollable frame for queued downloads
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", columnspan=2)
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.select_path_button = ctk.CTkButton(self, text="Select Save Path", command=self.select_path)
        self.select_path_button.grid(row=1, column=1, padx=5, pady=5, sticky="e")
        self.save_path_label = ctk.CTkLabel(self, text=self.save_path, state="disabled", fg_color="#343638",
                                            corner_radius=5)
        self.save_path_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        # Buttons for download control
        self.download_button = ctk.CTkButton(self, text="Download Images", command=self.download_images)
        self.download_button.grid(row=2, padx=5, pady=5, sticky="ew", columnspan=2)
        self.stop_button = ctk.CTkButton(self, text="Stop Download", command=self.stop_download)
        self.stop_button.grid(row=3, padx=5, pady=5, sticky="ew", columnspan=2)

        # Download progress
        self.progressbar_status = ctk.StringVar(value="Download stopped")
        self.progressbar_label = ctk.CTkLabel(self, textvariable=self.progressbar_status)
        self.progressbar_label.grid(row=4, padx=5, pady=5, sticky="ew", columnspan=2)
        self.download_progressbar = ctk.CTkProgressBar(self, mode="determinate", height=20)
        self.download_progressbar.grid(row=5, padx=5, pady=5, sticky="ew", columnspan=2)
        self.download_progressbar.set(0)

        # Internal stop flag for threading
        self._stop_flag = threading.Event()

    def add_album_pack(self, name, thumb, asset_ids):
        next_row = len(self.scrollable_frame.winfo_children())
        album_pack = AddAlbumPackDownloadFrame(self.scrollable_frame, name, thumb, asset_ids)
        album_pack.grid(row=next_row, column=0, padx=5, pady=1, sticky="ew")

    def download_images(self):
        """Download each pack in a non-blocking manner, presenting a progressbar"""
        self.download_progressbar.set(0)  # Reset progress bar before starting
        self.progressbar_status.set("Preparing to download...")
        self.download_button.configure(state="disabled")  # Disable upload button
        self._stop_flag.clear()  # Clear the stop flag before starting
        threading.Thread(target=self.download_task, daemon=True).start()

    def download_task(self):
        try:
            # Iterate over all child widgets in the scrollable frame
            for child in self.scrollable_frame.winfo_children():
                archive = self.client.download_archive(child.asset_ids)
                with open(f"{child.name}.zip", "wb") as file:
                    file.write(archive.getvalue())

        except Exception as e:
            print(f"Unexpected error Downloading: {e}")

        finally:
            self.download_progressbar.set(0)  # Reset progress bar
            self.download_progressbar.stop()
            self.progressbar_status.set("Download Complete")
            self.download_button.configure(state="normal")  # Re-enable upload button
            self._stop_flag.clear()  # Reset the flag for the next upload
            self.login_frame.update_login_info()
        print("Download Completed!")

    def select_path(self):
        """Open file dialog to select a path"""
        selected_path = filedialog.askdirectory(title="Select a Directory")
        if selected_path:
            self.save_path = selected_path
            self.save_path_label.configure(text=self.save_path)

    def stop_download(self):
        """Signal to stop the download process."""
        self._stop_flag.set()
        self.progressbar_status.set("Stopping download...")
