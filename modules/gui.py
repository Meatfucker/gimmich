import shutil
import threading
import subprocess
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog


class CheckboxFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Variables for checkboxes
        self.recursive = ctk.BooleanVar(value=False)
        self.names_as_albums = ctk.BooleanVar(value=False)
        self.skip_hash = ctk.BooleanVar(value=False)
        self.include_hidden = ctk.BooleanVar(value=False)
        self.dry_run = ctk.BooleanVar(value=False)
        self.delete_local = ctk.BooleanVar(value=False)
        self.album_input_enabled = ctk.BooleanVar(value=False)
        self.album_input_field = ctk.StringVar(value="Enter Album Name")

        # Checkboxes
        self.recursive = ctk.CTkCheckBox(self, text="Recursive", variable=self.recursive)
        self.recursive.grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.names_as_albums = ctk.CTkCheckBox(self, text="Directory names as albums", variable=self.names_as_albums)
        self.names_as_albums.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.skip_hash = ctk.CTkCheckBox(self, text="Skip Hash", variable=self.skip_hash)
        self.skip_hash.grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.include_hidden = ctk.CTkCheckBox(self, text="Include Hidden", variable=self.include_hidden)
        self.include_hidden.grid(row=3, column=0, pady=5, padx=5, sticky="w")
        self.dry_run = ctk.CTkCheckBox(self, text="Dry Run", variable=self.dry_run)
        self.dry_run.grid(row=4, column=0, pady=5, padx=5, sticky="w")
        self.delete_local = ctk.CTkCheckBox(self, text="Delete Local Files", variable=self.delete_local)
        self.delete_local.grid(row=5, column=0, pady=5, padx=5, sticky="w")
        self.album_input = ctk.CTkCheckBox(self, text="Album Name", variable=self.album_input_enabled)
        self.album_input.grid(row=6, column=0, pady=5, padx=5, sticky="w")
        self.album_input_entry = ctk.CTkEntry(self, textvariable=self.album_input_field)
        self.album_input_entry.grid(row=7, column=0, pady=5, padx=5)

    def get_states(self):
        """Returns the states of all checkboxes as a dictionary."""
        return {
            "recursive": self.recursive.get(),
            "directory_names_as_albums": self.names_as_albums.get(),
            "skip_hash": self.skip_hash.get(),
            "include_hidden": self.include_hidden.get(),
            "dry_run": self.dry_run.get(),
            "delete_local": self.delete_local.get(),
            "album_input_enabled": self.album_input_enabled.get(),
            "album_input": self.album_input_field.get(),
        }


class ConsoleOutput:

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.configure(state="normal")

    def write(self, message):
        self.text_widget.insert("end", message)
        self.text_widget.see("end")  # Auto-scroll to the end

    def flush(self):
        pass  # Required for compatibility with sys.stdout


class InfoFrame(ctk.CTkFrame):
    def __init__(self, parent, path_list, checkbox_states):
        super().__init__(parent)
        self.immich_command = shutil.which("immich")
        self.path_list = path_list
        self.checkbox_states = checkbox_states
        self.logged_in_status = ctk.StringVar(value="Logged in: False")  # Logged-in status label
        self.logged_in_label = ctk.CTkLabel(self, textvariable=self.logged_in_status)
        self.logged_in_label.pack(pady=5)
        self.immich_user_status = ctk.StringVar(value="User: Unknown")  # Username status label
        self.immich_user_label = ctk.CTkLabel(self, textvariable=self.immich_user_status)
        self.immich_user_label.pack(pady=5)
        self.immich_url_status = ctk.StringVar(value="URL: Unknown")  # URL status label
        self.immich_url_label = ctk.CTkLabel(self, textvariable=self.immich_url_status)
        self.immich_url_label.pack(pady=5)
        self.upload_button = ctk.CTkButton(self, text="Upload Images", command=self.upload_images)
        self.upload_button.pack(pady=5, side="bottom")
        self.server_info_result = None
        self.immich_user = None
        self.immich_url = None
        self.check_immich_server_info()
        self.check_immich_login()

    def check_immich_server_info(self):
        try:
            # Run `immich server-info` and capture the output
            result = subprocess.run([self.immich_command, "server-info"], text=True, capture_output=True, check=False)
            self.server_info_result = result.stdout.strip()
            print(self.server_info_result)
        except Exception as e:  # Catch all exceptions
            print(f"Unexpected error checking login: {e}")

    def check_immich_login(self):
        try:
            if "No auth file exists. Please login first." in self.server_info_result:
                self.logged_in_status.set("Logged in: False")
                self.immich_user_status.set(f"User: Unknown")
                self.immich_url_status.set(f"URL: Unknown")
            else:
                self.logged_in_status.set("Logged in: True")
                self.check_immich_user()
                self.check_immich_url()
        except Exception as e:  # Catch all exceptions
            print(f"Unexpected error checking login: {e}")

    def check_immich_user(self):
        lines = self.server_info_result.splitlines()
        for line in lines:
            if line.startswith("Server Info (via "):
                # Extract the part of the line after "Server Info"
                extracted_user = line[len("Server Info (via "):].strip()
                # Remove the last character
                self.immich_user = extracted_user[:-1]
                self.immich_user_status.set(f"User: {self.immich_user}")
                return
            else:
                self.immich_user = None

    def check_immich_url(self):
        lines = self.server_info_result.splitlines()
        for line in lines:
            if line.startswith("  Url: "):
                # Extract the part of the line after "  Url: "
                self.immich_url = line[len("  Url: "):].strip()
                self.immich_url_status.set(f"URL: {self.immich_url}")
                return
            else:
                self.immich_url = None

    def upload_images(self):
        def run_subprocess():
            try:
                checkbox_states = self.checkbox_states
                # Build the command
                compiled_run_list = [self.immich_command, "upload"] + self.path_list
                if checkbox_states["album_input_enabled"]:
                    compiled_run_list += ["--album-name", checkbox_states["album_input"]]
                if checkbox_states["recursive"]:
                    compiled_run_list += ["--recursive"]
                if checkbox_states["directory_names_as_albums"]:
                    compiled_run_list += ["--album"]
                if checkbox_states["skip_hash"]:
                    compiled_run_list += ["--skip-hash"]
                if checkbox_states["include_hidden"]:
                    compiled_run_list += ["--include-hidden"]
                if checkbox_states["dry_run"]:
                    compiled_run_list += ["--dry-run"]
                if checkbox_states["delete_local"]:
                    compiled_run_list += ["--delete"]
                print(compiled_run_list)

                process = subprocess.Popen(
                    compiled_run_list,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                # Read output line by line and display it
                for line in iter(process.stdout.readline, ''):
                    print(line.strip())  # Redirect output to your custom console
                process.stdout.close()
                process.wait()

            except Exception as e:
                print(f"Unexpected error Uploading: {e}")
            print("Upload Completed!")

        # Run the subprocess in a separate thread
        upload_thread = threading.Thread(target=run_subprocess)
        upload_thread.daemon = True  # Allow thread to exit when main program exits
        upload_thread.start()


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, info_frame):
        super().__init__(parent)
        self.immich_command = shutil.which("immich")
        self.info_frame = info_frame
        # Login URL Entry
        self.login_url = ctk.StringVar(value="Enter Login URL")
        self.login_url_input = ctk.CTkEntry(self, textvariable=self.login_url, width=350)
        self.login_url_input.grid(row=0, column=0, pady=5, padx=5)

        # Login API Key Entry
        self.login_key = ctk.StringVar(value="Enter Login API Key")
        self.login_key_input = ctk.CTkEntry(self, textvariable=self.login_key, width=350)
        self.login_key_input.grid(row=1, column=0, pady=5, padx=5)

        # Login Button
        self.login_button = ctk.CTkButton(self, text="Login", command=self.login_action, width=350)
        self.login_button.grid(row=2, column=0, pady=5, padx=5)

        # Logout Button
        self.logout_button = ctk.CTkButton(self, text="Logout", command=self.logout_action, width=350)
        self.logout_button.grid(row=3, column=0, pady=5, padx=5)

    def login_action(self):
        try:
            # Run `immich login` and capture the output
            login_url = self.login_url.get()
            login_key = self.login_key.get()
            result = subprocess.run([self.immich_command, "login", login_url, login_key], text=True,
                                    capture_output=True, check=False)
            server_login_result = result.stdout.strip()
            self.info_frame.check_immich_server_info()
            self.info_frame.check_immich_login()
            print(server_login_result)
        except Exception as e:  # Catch all exceptions
            print(f"Unexpected error logging in: {e}")
        print("Login clicked!")

    def logout_action(self):
        try:
            # Run `immich logout` and capture the output
            result = subprocess.run([self.immich_command, "logout"], text=True, capture_output=True, check=False)
            server_logout_result = result.stdout.strip()
            self.info_frame.check_immich_server_info()
            self.info_frame.check_immich_login()
            print(server_logout_result)
        except Exception as e:  # Catch all exceptions
            print(f"Unexpected error logging out: {e}")
        print("Logout Clicked!")


class PathFrame(ctk.CTkFrame):
    def __init__(self, parent, path_list):
        super().__init__(parent)
        self.path_list = path_list

        self.path_listbox_label = ctk.CTkLabel(self, text="Selected Paths:")
        self.path_listbox_label.grid(row=0, column=1, padx=5, pady=5)
        self.path_listbox = tk.Listbox(self, height=10, width=40)  # Using tkinter Listbox here
        self.path_listbox.grid(row=1, column=1, padx=5, pady=5)

        self.select_path_button = ctk.CTkButton(self, text="Select Path", command=self.select_path)
        self.select_path_button.grid(row=2, column=1, pady=5)

        self.remove_path_button = ctk.CTkButton(self, text="Remove Path", command=self.remove_selected_path)
        self.remove_path_button.grid(row=3, column=1, pady=5)

    def select_path(self):
        # Open file dialog to select a path
        selected_path = filedialog.askdirectory(title="Select a Directory")
        if selected_path:
            # Add the selected path to the path_list
            self.path_list.append(selected_path)
            print(f"Path added: {selected_path}")
            self.update_path_listbox()

    def remove_selected_path(self):
        # Get the selected path index
        selected_index = self.path_listbox.curselection()
        if selected_index:
            # Remove the path from the list
            selected_path = self.path_list[selected_index[0]]
            self.path_list.remove(selected_path)
            print(f"Path removed: {selected_path}")
            self.update_path_listbox()
        else:
            print("No path selected for removal.")

    def update_path_listbox(self):
        # Clear and then update the listbox
        self.path_listbox.delete(0, tk.END)
        for path in self.path_list:
            self.path_listbox.insert(tk.END, path)
