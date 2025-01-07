import customtkinter as ctk
import threading
import os
import re


class UploadFrame(ctk.CTkFrame):
    def __init__(self, parent, path_frame, checkbox_frame, login_frame, client):
        super().__init__(parent)
        self.configure(width=250, height=300)
        self.pack_propagate(False)
        # Layout grid configuration
        for col in range(1):
            self.columnconfigure(col, weight=1)  # Even column widths
        for row in range(6):
            self.rowconfigure(row, weight=0)  # Uniform row heights, no extra stretching
        self.client = client
        self.path_frame = path_frame
        self.file_list = []
        self.checkbox_frame = checkbox_frame
        self.login_frame = login_frame
        self.upload_button = ctk.CTkButton(self, text="Upload Images", command=self.upload_images)
        self.upload_button.grid(row=1, padx=5, pady=5, sticky="ew")
        self.stop_button = ctk.CTkButton(self, text="Stop Upload", command=self.stop_upload)
        self.stop_button.grid(row=2, padx=5, pady=5, sticky="ew")
        self._stop_flag = threading.Event()
        self.immich_user = None
        self.immich_url = None
        self.progressbar_status = ctk.StringVar(value="Upload stopped")
        self.progressbar_label = ctk.CTkLabel(self, textvariable=self.progressbar_status)
        self.progressbar_label.grid(row=4, padx=5, pady=5, sticky="ew")
        self.upload_progressbar = ctk.CTkProgressBar(master=self, mode="determinate", height=20)
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
            total_files = len(self.file_list)
            if total_files == 0:
                self.progressbar_status.set("No files to upload")
                return

            collected_ids = []
            collected_captions = []
            for index, file in enumerate(self.file_list):
                if self._stop_flag.is_set():
                    print("Upload stopped by user.")
                    self.progressbar_status.set("Upload stopped")
                    return

                print(f"Uploading {file} ({index + 1}/{len(self.file_list)})")
                asset_id, status = self.client.upload_asset(file)
                print(f"Status: {status}")
                directory = os.path.dirname(file)
                immediate_dir = os.path.basename(directory)
                collected_captions.append((file, asset_id))
                collected_ids.append((immediate_dir, asset_id))
                progress = (index + 1) / total_files
                self.upload_progressbar.set(progress)  # Update progress bar
                self.progressbar_status.set(f"Uploading... {index + 1}/{total_files} files")
            self.progressbar_status.set("Upload Complete")
            if collected_ids:
                self.process_options(collected_ids, collected_captions)

        except Exception as e:
            print(f"Unexpected error Uploading: {e}")

        finally:
            self.upload_progressbar.set(0)  # Reset progress bar
            self.upload_progressbar.stop()
            self.upload_button.configure(state="normal")  # Re-enable upload button
            self._stop_flag.clear()  # Reset the flag for the next upload
            self.login_frame.update_login_info()
        print("Upload Completed!")

    def process_options(self, collected_ids, collected_captions):
        """Runs the various non-upload tasks such as tagging and captioning."""
        self.process_albums(collected_ids)
        self.process_albums_by_dir(collected_ids)
        self.process_tags(collected_ids)
        self.process_tags_by_dir(collected_ids)
        self.process_captions(collected_captions)
        self.process_captions_as_tags(collected_captions)

    def gather_file_list(self):
        """Builds the file list based on user options"""
        checkbox_states = self.checkbox_frame.get_states()
        if checkbox_states["recursive"]:
            self.file_list = self.path_frame.get_files_from_paths(recursive=True)
        else:
            self.file_list = self.path_frame.get_files_from_paths(recursive=False)

    def process_captions(self, ids):
        checkbox_states = self.checkbox_frame.get_states()
        if checkbox_states['import_captions']:
            for file, asset_id in ids:
                txt_file = os.path.splitext(file)[0] + '.txt'
                if os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        caption = f.read()
                    self.client.update_asset_description(asset_id, caption)
                    print(f"Added caption for {file}")
                else:
                    print(f"No caption file found for: {file}")

    def process_captions_as_tags(self, ids):
        checkbox_states = self.checkbox_frame.get_states()
        caption_delimiters = checkbox_states['caption_delimiters']
        delimiters_pattern = f"[{re.escape(caption_delimiters)}]"
        if checkbox_states['captions_as_tags']:
            for file, asset_id in ids:
                txt_file = os.path.splitext(file)[0] + '.txt'
                if os.path.exists(txt_file):
                    with open(txt_file, 'r', encoding='utf-8') as f:
                        caption = f.read()
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

    def process_albums(self, ids):
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

    def process_albums_by_dir(self, ids):
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

    def process_tags(self, ids):
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

    def process_tags_by_dir(self, ids):
        checkbox_states = self.checkbox_frame.get_states()
        existing_tags = self.client.get_all_tags()
        if checkbox_states['directory_names_as_tags']:
            tags_by_directory = {}
            for directory_name, asset_id in ids:
                tags_by_directory.setdefault(directory_name, []).append(asset_id)

            for directory_name, asset_ids in tags_by_directory.items():
                #  Check if the tag exists and if not, create a tag for each directory
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
