import customtkinter as ctk
import threading
import os


class UploadFrame(ctk.CTkFrame):
    def __init__(self, parent, path_frame, checkbox_frame, login_frame, client):
        super().__init__(parent)
        self.configure(width=250, height=300)
        self.pack_propagate(False)
        self.client = client
        self.path_frame = path_frame
        self.file_list = []
        self.checkbox_frame = checkbox_frame
        self.login_frame = login_frame
        self.upload_button = ctk.CTkButton(self, text="Upload Images", command=self.upload_images)
        self.upload_button.grid(row=1, pady=5, sticky="ew")
        self.stop_button = ctk.CTkButton(self, text="Stop Upload", command=self.stop_upload)
        self.stop_button.grid(row=2, pady=5, sticky="ew")
        self._stop_flag = threading.Event()
        self.immich_user = None
        self.immich_url = None
        self.progressbar_status = ctk.StringVar(value="Upload stopped")
        self.progressbar_label = ctk.CTkLabel(self, textvariable=self.progressbar_status)
        self.progressbar_label.grid(row=4, padx=5, pady=5)
        self.upload_progressbar = ctk.CTkProgressBar(master=self, mode="determinate", height=20)
        self.upload_progressbar.grid(row=5, padx=5, pady=5)
        self.upload_progressbar.set(0)
        self.album_button = ctk.CTkButton(self, text="get all albums", command=self.get_albums)
        self.album_button.grid(row=6, pady=5, sticky="ew")

    def get_albums(self):
        albums = self.client.get_all_albums()
        print(albums)

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
            for index, file in enumerate(self.file_list):
                if self._stop_flag.is_set():
                    print("Upload stopped by user.")
                    self.progressbar_status.set("Upload stopped")
                    break

                print(f"Uploading {file} ({index + 1}/{len(self.file_list)})")
                asset_id, status = self.client.upload_asset(file)
                print(f"Status: {status}")
                directory = os.path.dirname(file)
                immediate_dir = os.path.basename(directory)
                collected_ids.append((immediate_dir, asset_id))
                progress = (index + 1) / total_files
                self.upload_progressbar.set(progress)  # Update progress bar
                self.progressbar_status.set(f"Uploading... {index + 1}/{total_files} files")

            if collected_ids:
                self.process_albums(collected_ids)

        except Exception as e:
            print(f"Unexpected error Uploading: {e}")

        finally:
            self.upload_progressbar.set(0)  # Reset progress bar
            self.upload_progressbar.stop()
            self.progressbar_status.set("Upload stopped")
            self.upload_button.configure(state="normal")  # Re-enable upload button
            self._stop_flag.clear()  # Reset the flag for the next upload
            self.login_frame.update_login_info()
        print("Upload Completed!")

    def gather_file_list(self):
        """Builds the file list based on user options"""
        checkbox_states = self.checkbox_frame.get_states()
        if checkbox_states["recursive"]:
            self.file_list = self.path_frame.get_files_from_paths(recursive=True)
        else:
            self.file_list = self.path_frame.get_files_from_paths(recursive=False)

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
        if checkbox_states['directory_names_as_albums']:
            albums_by_directory = {}
            for directory_name, asset_id in ids:
                albums_by_directory.setdefault(directory_name, []).append(asset_id)

            for directory_name, asset_ids in albums_by_directory.items():
                #  Check if the album exists and if not, create an album for each directory
                if directory_name not in existing_albums:
                    album_id = self.client.create_album(directory_name)
                    self.client.add_assets_to_album(album_id, all_asset_ids)
                    print(f"Created album {directory_name}, id:{album_id}")
                else:
                    album_id = existing_albums[directory_name]
                    self.client.add_assets_to_album(album_id, all_asset_ids)
                    print(f"Album {directory_name} already exists, added assets to existing album: {album_id}")

    def stop_upload(self):
        """Signal to stop the upload process."""
        self._stop_flag.set()
        self.progressbar_status.set("Stopping upload...")
