import os
import re
import threading
from typing import Optional, List, Tuple
import customtkinter as ctk
from modules.path_frame import PathFrame
from modules.checkbox_frame import CheckboxFrame
from modules.login_frame import LoginFrame
from modules.api_client import ImmichClient


class UploadFrame(ctk.CTkFrame):
    """This frame contains the global upload options and the actual upload logic and GUI elements"""
    def __init__(self,
                 parent: ctk.CTkFrame,
                 path_frame: PathFrame,
                 checkbox_frame: CheckboxFrame,
                 login_frame: LoginFrame,
                 client: ImmichClient) -> None:
        super().__init__(parent)
        self.configure(width=250, height=300)  # Configure frame size
        for col in range(1):
            self.columnconfigure(col, weight=1)  # Even column widths
        for row in range(4):
            self.rowconfigure(row, weight=0)  # Uniform row heights, no extra stretching
        self.client: ImmichClient = client
        self.path_frame: PathFrame = path_frame
        self.file_list: List[str] = []
        self.checkbox_frame: CheckboxFrame = checkbox_frame
        self.login_frame: LoginFrame = login_frame
        self.upload_button: ctk.CTkButton = ctk.CTkButton(self, text="Upload Images", command=self.upload_images)
        self.upload_button.grid(row=1, padx=5, pady=5, sticky="ew")
        self.stop_button: ctk.CTkButton = ctk.CTkButton(self, text="Stop Upload", command=self.stop_upload)
        self.stop_button.grid(row=2, padx=5, pady=5, sticky="ew")
        self._stop_flag: threading.Event = threading.Event()
        self.immich_user: Optional[str] = None
        self.immich_url: Optional[str] = None
        self.progressbar_status: ctk.StringVar = ctk.StringVar(value="Upload stopped")
        self.progressbar_label: ctk.CTkLabel = ctk.CTkLabel(self, textvariable=self.progressbar_status)
        self.progressbar_label.grid(row=4, padx=5, pady=5, sticky="ew")
        self.upload_progressbar: ctk.CTkProgressBar = ctk.CTkProgressBar(master=self, mode="determinate", height=20)
        self.upload_progressbar.grid(row=5, padx=5, pady=5, sticky="ew")
        self.upload_progressbar.set(0)

    def upload_images(self):
        """Upload each file in a non-blocking manner, presenting a progressbar"""
        self.upload_progressbar.set(0)  # Reset progress bar before starting
        self.progressbar_status.set("Preparing to upload...")
        self.upload_button.configure(state="disabled")  # Disable upload button
        self._stop_flag.clear()  # Clear the stop flag before starting
        threading.Thread(target=self.upload_task, daemon=True).start()

    def upload_task(self):
        """Prepare the file list and upload the files, updating the progressbar."""
        try:
            self.gather_file_list()
            total_files = len(self.file_list)  # Get total list for progress bar
            if total_files == 0:
                self.progressbar_status.set("No files to upload")
                return

            collected_ids = []  # Collect ids and captions for the captions and tags processing
            collected_captions = []
            for index, file in enumerate(self.file_list):  # Iterate over the file list and upload them
                if self._stop_flag.is_set():
                    print("Upload stopped by user.")
                    self.progressbar_status.set("Upload stopped")
                    return

                print(f"Uploading {file} ({index + 1}/{len(self.file_list)})")
                asset_id, status = self.client.upload_asset(file)  # This is the actual upload
                print(f"Status: {status}")
                directory = os.path.dirname(file)  # Get variables for processing
                immediate_dir = os.path.basename(directory)
                collected_captions.append((file, asset_id))
                collected_ids.append((immediate_dir, asset_id))
                progress = (index + 1) / total_files  # Update count for progressbar
                self.upload_progressbar.set(progress)  # Update progress bar
                self.progressbar_status.set(f"Uploading... {index + 1}/{total_files} files")
            if collected_ids:
                self.process_options(collected_ids, collected_captions)  # Process captions/tags
            self.progressbar_status.set("Upload Complete")

        except Exception as e:
            print(f"Unexpected error Uploading: {e}")

        finally:
            self.upload_progressbar.set(0)  # Reset progress bar
            self.upload_progressbar.stop()
            self.upload_button.configure(state="normal")  # Re-enable upload button
            self._stop_flag.clear()  # Reset the flag for the next upload
            self.login_frame.update_login_info()
        print("Upload Completed!")

    def process_options(self, collected_ids: List[Tuple[str, str]], collected_captions: List[Tuple[str, str]]):
        """Runs the various non-upload tasks such as tagging and captioning."""
        self.progressbar_status.set("Processing Albums")
        self.process_albums(collected_ids)  # Create albums
        self.process_albums_by_dir(collected_ids)
        self.progressbar_status.set("Processing Tags")
        self.process_tags(collected_ids)  # Create tags
        self.process_tags_by_dir(collected_ids)
        self.progressbar_status.set("Processing Captions")
        self.process_captions(collected_captions)  # Create captions
        self.process_captions_as_tags(collected_captions)

    def gather_file_list(self):
        """Builds the file list based on user options"""
        checkbox_states = self.checkbox_frame.get_states()
        if checkbox_states["recursive"]:
            self.file_list = self.path_frame.get_files_from_paths(recursive=True)
        else:
            self.file_list = self.path_frame.get_files_from_paths(recursive=False)

    def process_captions(self, ids: List[Tuple[str, str]]):
        """Process uploading caption descriptions if enabled"""
        total_files = len(self.file_list)  # Get total amount of files to caption
        checkbox_states = self.checkbox_frame.get_states()
        if checkbox_states['import_captions']:
            index = 0  # Start index for progress bar.
            for file, asset_id in ids:  # Iterate over the ids
                index = index + 1
                txt_file = os.path.splitext(file)[0] + '.txt'  # Replace original filename extension
                if os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as f:  # Load caption from disk
                        caption = f.read()
                    self.client.update_asset_description(asset_id, caption)  # Upload caption to server
                    print(f"Added caption for {file}")
                else:
                    print(f"No caption file found for: {file}")
                progress = index / total_files  # Advance file count for progressbar
                self.upload_progressbar.set(progress)  # Update progress bar
                self.progressbar_status.set(f"Importing Captions as descriptions... {index + 1}/{total_files} files")

    def process_captions_as_tags(self, ids: List[Tuple[str, str]]):
        """Process uploading captions as tags if enabled"""
        total_files = len(self.file_list)  # Get total amount of files to be processed
        checkbox_states = self.checkbox_frame.get_states()
        caption_delimiters = checkbox_states['caption_delimiters']
        delimiters_pattern = f"[{re.escape(caption_delimiters)}]"
        if checkbox_states['captions_as_tags']:
            for file, asset_id in ids:  # Iterate over files to caption
                index = 0  # Create index for progress bar
                txt_file = os.path.splitext(file)[0] + '.txt'  # Replace file extension with txt
                if os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        caption = f.read()  # Load caption
                    tags = [tag.strip() for tag in re.split(delimiters_pattern, caption) if tag.strip()]
                    for tag in tags:
                        existing_tags = self.client.get_all_tags()
                        if tag not in existing_tags:
                            tag_id = self.client.create_tag(tag)
                            self.client.tag_assets(tag_id, [asset_id])
                            print(f"Created tag {tag}, id:{tag_id}")
                        else:
                            tag_id = existing_tags[tag]
                            self.client.tag_assets(tag_id, [asset_id])

                    print(f"Added tags from caption for {file}")
                else:
                    print(f"No caption file found for: {file}")
                progress = index / total_files  # Update file count for progress bar
                self.upload_progressbar.set(progress)  # Update progress bar
                self.progressbar_status.set(f"Importing Captions as tags... {index + 1}/{total_files} files")

    def process_albums(self, ids: List[Tuple[str, str]]):
        """Create albums based on user options"""
        checkbox_states = self.checkbox_frame.get_states()
        existing_albums = self.client.get_all_albums()
        all_asset_ids = [value for _, value in ids]
        if checkbox_states['album_input_enabled']:
            if checkbox_states['album_input'] not in existing_albums:
                album_id = self.client.create_album(checkbox_states['album_input'])
                self.client.add_assets_to_album(album_id, all_asset_ids)
                print(f"Created album {checkbox_states['album_input']}, id:{album_id}")
            else:
                album_id = existing_albums[checkbox_states['album_input']]
                self.client.add_assets_to_album(album_id, all_asset_ids)
                print(f"Album {checkbox_states['album_input']} already exists, added to existing album: {album_id}")

    def process_albums_by_dir(self, ids: List[Tuple[str, str]]):
        """Create albums based on existing folder name"""
        checkbox_states = self.checkbox_frame.get_states()
        existing_albums = self.client.get_all_albums()
        if checkbox_states['directory_names_as_albums']:
            albums_by_directory = {}
            for directory_name, asset_id in ids:
                albums_by_directory.setdefault(directory_name, []).append(asset_id)
            for directory_name, asset_ids in albums_by_directory.items():
                #  Check if the album exists and if not, create an album for each directory
                if directory_name not in existing_albums:
                    album_id = self.client.create_album(directory_name)
                    self.client.add_assets_to_album(album_id, asset_ids)
                    print(f"Created album {directory_name}, id:{album_id}")
                else:
                    album_id = existing_albums[directory_name]
                    self.client.add_assets_to_album(album_id, asset_ids)
                    print(f"Album {directory_name} already exists, added assets to existing album: {album_id}")

    def process_tags(self, ids: List[Tuple[str, str]]):
        """Create tags based on user options"""
        checkbox_states = self.checkbox_frame.get_states()
        existing_tags = self.client.get_all_tags()
        all_asset_ids = [value for _, value in ids]
        if checkbox_states['tag_input_enabled']:
            if checkbox_states['tag_input'] not in existing_tags:
                tag_id = self.client.create_tag(checkbox_states['tag_input'])
                self.client.tag_assets(tag_id, all_asset_ids)
                print(f"Created tag {checkbox_states['tag_input']}, id:{tag_id}")
            else:
                tag_id = existing_tags[checkbox_states['tag_input']]
                self.client.tag_assets(tag_id, all_asset_ids)
                print(f"Tag {checkbox_states['album_input']} already exists, added to existing tag: {tag_id}")

    def process_tags_by_dir(self, ids: List[Tuple[str, str]]):
        """Create tags based on the folder name"""
        checkbox_states = self.checkbox_frame.get_states()
        existing_tags = self.client.get_all_tags()
        if checkbox_states['directory_names_as_tags']:
            tags_by_directory = {}
            for directory_name, asset_id in ids:
                tags_by_directory.setdefault(directory_name, []).append(asset_id)

            for directory_name, asset_ids in tags_by_directory.items():
                if directory_name not in existing_tags:
                    tag_id = self.client.create_tag(directory_name)
                    self.client.tag_assets(tag_id, asset_ids)
                    print(f"Created tag {directory_name}, id:{tag_id}")
                else:
                    tag_id = existing_tags[directory_name]
                    self.client.tag_assets(tag_id, asset_ids)
                    print(f"Tag {directory_name} already exists, added assets to existing tag: {tag_id}")

    def stop_upload(self):
        """Signal to stop the upload process."""
        self._stop_flag.set()
        self.progressbar_status.set("Stopping upload...")
