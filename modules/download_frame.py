import os
import threading
from typing import List
import tkinter
import customtkinter as ctk
from tkinter import filedialog
from modules.login_frame import LoginFrame
from modules.api_client import ImmichClient


class DownloadFrame(ctk.CTkFrame):
    """This contains the packs to download and the logic for downloading them and thier options."""
    def __init__(self, parent: ctk.CTkFrame, login_frame: LoginFrame, client: ImmichClient):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)  # Configure frame for stretching to fit window
        self.rowconfigure(0, weight=1)
        self.client = client
        self.login_frame = login_frame
        self.queued_downloads = []  # List to hold DownloadPackFrame objects
        self.save_path = "No Path Selected"
        self.composed_save_path = "No Path Selected"

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Download Queue")  # Scrollable frame for queued downloads
        self.scrollable_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew", columnspan=2)
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.select_path_button = ctk.CTkButton(self, text="Select Save Path", command=self.select_path)
        self.select_path_button.grid(row=1, column=1, padx=5, pady=5, sticky="e")
        self.save_path_label = ctk.CTkLabel(self, text=self.save_path, state="disabled", fg_color="#343638",
                                            corner_radius=5)
        self.save_path_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.download_button = ctk.CTkButton(self, text="Download", command=self.download_images) # Download buttons
        self.download_button.grid(row=2, padx=5, pady=5, sticky="ew", columnspan=2)
        self.stop_button = ctk.CTkButton(self, text="Stop Download", command=self.stop_download)
        self.stop_button.grid(row=3, padx=5, pady=5, sticky="ew", columnspan=2)

        self.progressbar_status = ctk.StringVar(value="Download stopped") # Download progressbar
        self.progressbar_label = ctk.CTkLabel(self, textvariable=self.progressbar_status)
        self.progressbar_label.grid(row=4, padx=5, pady=5, sticky="ew", columnspan=2)
        self.download_progressbar = ctk.CTkProgressBar(self, mode="determinate", height=20)
        self.download_progressbar.grid(row=5, padx=5, pady=5, sticky="ew", columnspan=2)
        self.download_progressbar.set(0)

        self._stop_flag = threading.Event()   # Internal stop flag for threading

    def add_pack(self, name: str, thumb: ctk.CTkImage, asset_ids: List, color: str):
        """This creates a download pack and adds it to the frame"""
        next_row = len(self.scrollable_frame.winfo_children())
        album_pack = AddPackDownloadFrame(self.scrollable_frame, name, thumb, asset_ids, color)
        album_pack.grid(row=next_row, column=0, padx=5, pady=1, sticky="ew")

    def download_images(self):
        """Download each pack in a non-blocking manner, presenting a progressbar"""
        if self.save_path == "No Path Selected":
            return
        self.download_progressbar.set(0)  # Reset progress bar before starting
        self.progressbar_status.set("Preparing to download...")
        self.download_button.configure(state="disabled")  # Disable upload button
        self._stop_flag.clear()  # Clear the stop flag before starting
        threading.Thread(target=self.download_task, daemon=True).start()

    def download_task(self):
        """This iterates over the packs in the download frame and downloads them"""
        try:
            # Iterate over all download packs in the scrollable frame for total number of items
            total_files = sum(len(child.asset_ids) for child in self.scrollable_frame.winfo_children())

            if total_files == 0:
                self.progressbar_status.set("No files to download")
                return
            processed_files = 0  # Create index for updating progress bar

            for index, child in enumerate(self.scrollable_frame.winfo_children()):
                if self._stop_flag.is_set():
                    print("Download stopped by user.")
                    self.progressbar_status.set("Download Stopped")
                    return
                if child.directory_type_var.get() == 0:  # Adjust base path according to pack options
                    self.composed_save_path = self.save_path
                if child.directory_type_var.get() == 1:
                    self.composed_save_path = f"{self.save_path}/{child.name}"
                    os.makedirs(f"{self.composed_save_path}", exist_ok=True)
                if child.directory_type_var.get() == 2:
                    user_path = child.user_directory.get()
                    self.composed_save_path = f"{self.save_path}/{user_path}"
                    os.makedirs(f"{self.composed_save_path}", exist_ok=True)

                for id in child.asset_ids:
                    self.process_options(child, id)  # Process file download options
                    processed_files += 1
                    progress = (processed_files + 1) / total_files
                    self.download_progressbar.set(progress)  # Update progress bar
                    self.progressbar_status.set(f"Downloading... {processed_files}/{total_files} files")
            self.progressbar_status.set("Download Complete")

        except Exception as e:
            print(f"Unexpected error Downloading: {e}")

        finally:
            self.download_progressbar.set(0)  # Reset progress bar
            self.download_progressbar.stop()
            self.download_button.configure(state="normal")  # Re-enable upload button
            self._stop_flag.clear()  # Reset the flag for the next upload
            self.login_frame.update_login_info()
        print("Download Completed!")

    def process_options(self, child, id: str):
        """Process download packs and their options"""
        image = self.client.download_asset(id)
        filename = self.client.get_original_filename(id)

        with open(f"{self.composed_save_path}/{filename}", "wb") as file:
            file.write(image.getvalue())

        if child.caption_type_var.get() == 0:  # Write caption files based on pack options
            pass
        elif child.caption_type_var.get() == 1:
            self.write_description_caption(id, filename)
        elif child.caption_type_var.get() == 2:
            self.write_tag_caption(id, filename)

    def write_tag_caption(self, id: str, filename: str):
        """Takes an assetId and filename string and writes a caption file based on the tags"""
        tags = self.client.get_asset_tags(id)
        tag_string = ", ".join(tag['value'] for tag in tags if 'value' in tag)
        base_filename = os.path.splitext(filename)[0]
        with open(f"{self.composed_save_path}/{base_filename}.txt", "w") as file:
            file.write(tag_string)

    def write_description_caption(self, id, filename):
        """Takes an assetId and filename string and writes a caption file based on the description"""
        description = self.client.get_asset_description(id)
        base_filename = os.path.splitext(filename)[0]
        with open(f"{self.composed_save_path}/{base_filename}.txt", "w") as file:
            file.write(description)

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


class AddPackDownloadFrame(ctk.CTkFrame):
    """This contains the download pack and its options"""
    def __init__(self, parent: ctk.CTkScrollableFrame, name: str, thumb: ctk.CTkImage, asset_ids: List, color: str):
        super().__init__(parent, border_width=2, border_color="gray", fg_color=color)
        for row in range(1):
            self.rowconfigure(row, weight=1)
        self.columnconfigure(1, weight=1)
        self.parent = parent
        self.name = name
        self.thumb = thumb
        self.asset_ids = asset_ids
        self.thumbnail_label = ctk.CTkLabel(self, image=self.thumb, text="")
        self.thumbnail_label.grid(row=0, column=0, padx=2, pady=0)
        self.name_label = ctk.CTkLabel(self, text=self.name)
        self.name_label.grid(row=0, column=1, padx=2, pady=0, sticky="ew")
        self.options_button = ctk.CTkButton(self, text="...", command=self.options, corner_radius=0, width=10)
        self.options_button.grid(row=0, column=2, padx=2, pady=0)
        self.remove_pack_button = ctk.CTkButton(self, text="Remove", command=self.remove_download_pack, corner_radius=0)
        self.remove_pack_button.grid(row=0, column=3, padx=2, pady=0, sticky="ew")
        self.descriptions_as_captions_var = ctk.BooleanVar(value=False)
        self.tags_as_captions_var = ctk.BooleanVar(value=False)
        self.directory_type_var = tkinter.IntVar(value=0)
        self.caption_type_var = tkinter.IntVar(value=0)
        self.user_directory = tkinter.StringVar(value="")

    def options(self):
        """This opens a pop up window to configure the packs options."""
        options_window = ctk.CTkToplevel(self)
        options_window.title(self.name)

        button_x = self.options_button.winfo_rootx()  # Get the mouse coordinates for opening the popup window nearby
        button_y = self.options_button.winfo_rooty()
        offset_x = 10
        offset_y = self.options_button.winfo_height() + 5
        options_window.geometry(f"{button_x + offset_x}+{button_y + offset_y}")  # Open options popup

        options_window.transient(self)  # Bring options window to the front
        options_window.focus_set()
        options_window.resizable(False, False)

        create_captions_frame = ctk.CTkFrame(options_window, border_width=2, border_color="gray")
        create_captions_frame.grid(row=1, column=0, pady=5, padx=5, sticky="ew")
        create_captions_radio_1 = ctk.CTkRadioButton(create_captions_frame,
                                                     text="Dont create captions",
                                                     variable=self.caption_type_var,
                                                     value=0)
        create_captions_radio_2 = ctk.CTkRadioButton(create_captions_frame,
                                                     text="Create captions from descriptions",
                                                     variable=self.caption_type_var,
                                                     value=1)
        create_captions_radio_3 = ctk.CTkRadioButton(create_captions_frame,
                                                     text="Create captions from tags",
                                                     variable=self.caption_type_var,
                                                     value=2)
        create_captions_radio_1.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        create_captions_radio_2.grid(row=2, column=0, pady=5, padx=5, sticky="w")
        create_captions_radio_3.grid(row=3, column=0, pady=5, padx=5, sticky="w")

        create_directory_frame = ctk.CTkFrame(options_window, border_width=2, border_color="gray")
        create_directory_frame.grid(row=3, column=0, pady=5, padx=5, sticky="ew")
        create_directory_radio_1 = ctk.CTkRadioButton(create_directory_frame,
                                                      text="Dont create directories",
                                                      variable=self.directory_type_var,
                                                      value=0)
        create_directory_radio_2 = ctk.CTkRadioButton(create_directory_frame,
                                                      text="Create directories based on pack name",
                                                      variable=self.directory_type_var,
                                                      value=1)
        create_directory_radio_3 = ctk.CTkRadioButton(create_directory_frame,
                                                      text="Create user specified directory",
                                                      variable=self.directory_type_var,
                                                      value=2)
        create_directory_radio_1.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        create_directory_radio_2.grid(row=2, column=0, pady=5, padx=5, sticky="w")
        create_directory_radio_3.grid(row=3, column=0, pady=5, padx=5, sticky="w")
        user_directory_entry = ctk.CTkEntry(create_directory_frame, placeholder_text="Enter directory name",
                                            textvariable=self.user_directory)
        user_directory_entry.grid(row=3, column=1, pady=5, padx=5, sticky="ew")

        def close_window():
            """Destroys the pop up window"""
            options_window.destroy()

        close_button = ctk.CTkButton(options_window, text="Close", command=close_window)
        close_button.grid(row=7, column=0, pady=5, padx=5, sticky="ew", columnspan=2)

    def remove_download_pack(self):
        """Removes the pack from the download frame and destroys it"""
        self.destroy()
        for index, child in enumerate(self.parent.winfo_children()):
            child.grid(row=index, column=0, padx=5, pady=1, sticky="ew")
