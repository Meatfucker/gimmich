import os
import customtkinter as ctk
from tkinter import filedialog

allowed_extensions = ['.3fr', '.ari', '.arw', '.cap', '.cin', '.cr2', '.cr3', '.crw', '.dcr', '.dng', '.erf', '.fff',
                      '.iiq', '.k25', '.kdc', '.mrw', '.nef', '.nrw', '.orf', '.ori', '.pef', '.psd', '.raf', '.raw',
                      '.rw2', '.rwl', '.sr2', '.srf', '.srw', '.x3f', '.avif', '.bmp', '.gif', '.heic', '.heif', '.hif',
                      '.insp', '.jpe', '.jpeg', '.jpg', '.jxl', '.png', '.svg', '.tif', '.tiff', '.webp', '.3gp',
                      '.3gpp', '.avi', '.flv', '.insv', '.m2ts', '.m4v', '.mkv', '.mov', '.mp4', '.mpe', '.mpeg',
                      '.mpg', '.mts', '.vob', '.webm', '.wmv']


class AddPackUploadFrame(ctk.CTkFrame):
    def __init__(self, parent, name, parent_frame):
        super().__init__(parent, border_width=2, border_color="gray")
        for row in range(1):
            self.rowconfigure(row, weight=1)
        self.columnconfigure(0, weight=1)
        self.parent = parent
        self.parent_frame = parent_frame
        self.name = name
        self.name_label = ctk.CTkLabel(self, text=self.name)
        self.name_label.grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        self.remove_pack_button = ctk.CTkButton(self, text="Remove", command=self.remove_upload_pack, corner_radius=0)
        self.remove_pack_button.grid(row=0, column=1, padx=2, pady=0, sticky="ew")

    def remove_upload_pack(self):
        print(self.parent_frame.path_list)
        self.parent_frame.remove_selected_path(self.name)
        print(self.parent_frame.path_list)
        self.destroy()
        for index, child in enumerate(self.parent.winfo_children()):
            child.grid(row=index, column=0, padx=5, pady=1, sticky="ew")


class PathFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.filtered_file_list = []
        self.file_list = []
        self.path_list = []
        self.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=1)
        self.path_scrollable_frame = ctk.CTkScrollableFrame(self)
        self.path_scrollable_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.path_scrollable_frame.columnconfigure(0, weight=1)
        self.select_path_button = ctk.CTkButton(self, text="Select Upload Path", command=self.select_path)
        self.select_path_button.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

    def add_pack(self, name):
        next_row = len(self.path_scrollable_frame.winfo_children())
        path_pack = AddPackUploadFrame(self.path_scrollable_frame, name, self)
        path_pack.grid(row=next_row, column=0, padx=2, pady=2, sticky="ew")

    def select_path(self):
        """Open file dialog to select a path"""
        selected_path = filedialog.askdirectory(title="Select a Directory")
        if selected_path:
            self.add_pack(selected_path)
            self.path_list.append(selected_path)

    def remove_selected_path(self, name):
        """Remove the selected path"""
        # Get the selected path index
        self.path_list = [path for path in self.path_list if path != name]

    def get_files_from_paths(self, recursive=False):
        """Return a list of the files from the paths, optionally recursively."""
        self.file_list = []
        for path in self.path_list:
            if os.path.isdir(path):  # Check if the path is a directory
                if recursive:  # If recursive, traverse directories using os.walk
                    for root, _, filenames in os.walk(path):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            if os.path.isfile(file_path):  # Only add files
                                self.file_list.append(file_path)
                else:  # Non-recursive: only list files in the current directory
                    for filename in os.listdir(path):
                        file_path = os.path.join(path, filename)
                        if os.path.isfile(file_path):  # Only add files
                            self.file_list.append(file_path)
            elif os.path.isfile(path):  # If it's a file, add it directly
                self.file_list.append(path)

        self.filter_files_by_extension()
        return self.filtered_file_list

    def filter_files_by_extension(self):
        """Remove any files from the list that don't match the allowed extension types."""
        filtered_files = []
        for file in self.file_list:
            if any(file.lower().endswith(ext.lower()) for ext in allowed_extensions):
                filtered_files.append(file)
        self.filtered_file_list = filtered_files
