import customtkinter as ctk
import threading
import os


class UploadFrame(ctk.CTkFrame):
    def __init__(self, parent, path_frame, checkbox_frame, client):
        super().__init__(parent)
        self.configure(width=250, height=300)
        self.pack_propagate(False)
        self.client = client
        self.path_frame = path_frame
        self.file_list = []
        self.checkbox_frame = checkbox_frame
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
                collected_ids.append((asset_id, immediate_dir))
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
        single_album_ids = [asset_id for asset_id, _ in ids]
        checkbox_states = self.checkbox_frame.get_states()
        if checkbox_states['album_input_enabled']:
            self.client.create_album(checkbox_states['album_input'],  single_album_ids)
        if checkbox_states['directory_names_as_albums']:
            albums_by_directory = {}
            for asset_id, directory_name in ids:
                albums_by_directory.setdefault(directory_name, []).append(asset_id)

            for directory_name, asset_ids in albums_by_directory.items():
                # Create an album for each directory
                self.client.create_album(directory_name, asset_ids)

    def stop_upload(self):
        """Signal to stop the upload process."""
        self._stop_flag.set()
        self.progressbar_status.set("Stopping upload...")
