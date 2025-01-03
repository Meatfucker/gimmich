import os
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog

allowed_extensions = ['.3fr', '.ari', '.arw', '.cap', '.cin', '.cr2', '.cr3', '.crw', '.dcr', '.dng', '.erf', '.fff',
                      '.iiq', '.k25', '.kdc', '.mrw', '.nef', '.nrw', '.orf', '.ori', '.pef', '.psd', '.raf', '.raw',
                      '.rw2', '.rwl', '.sr2', '.srf', '.srw', '.x3f', '.avif', '.bmp', '.gif', '.heic', '.heif', '.hif',
                      '.insp', '.jpe', '.jpeg', '.jpg', '.jxl', '.png', '.svg', '.tif', '.tiff', '.webp', '.3gp',
                      '.3gpp', '.avi', '.flv', '.insv', '.m2ts', '.m4v', '.mkv', '.mov', '.mp4', '.mpe', '.mpeg',
                      '.mpg', '.mts', '.vob', '.webm', '.wmv']


class PathFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.filtered_file_list = []
        self.file_list = []
        self.path_list = []
        self.path_listbox_label = ctk.CTkLabel(self, text="Selected Paths:")
        self.path_listbox_label.grid(row=0, column=1, padx=5, pady=5)
        # Using tkinter Listbox here and theming it to match
        custom_font = ctk.CTkFont(family="Roboto", size=20)
        self.path_listbox = tk.Listbox(self, height=10, width=40, fg="#9E9E9E", bg="#343638", selectbackground="gray",
                                       selectforeground="white", font=custom_font, borderwidth=0, highlightthickness=0)

        self.path_listbox.grid(row=1, column=1, padx=5, pady=5)

        self.select_path_button = ctk.CTkButton(self, text="Select Path", command=self.select_path)
        self.select_path_button.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.remove_path_button = ctk.CTkButton(self, text="Remove Path", command=self.remove_selected_path)
        self.remove_path_button.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    def select_path(self):
        """Open file dialog to select a path"""
        selected_path = filedialog.askdirectory(title="Select a Directory")
        if selected_path:
            # Add the selected path to the path_list
            self.path_list.append(selected_path)
            self.update_path_listbox()

    def remove_selected_path(self):
        """Remove the selected path"""
        # Get the selected path index
        selected_index = self.path_listbox.curselection()
        if selected_index:
            # Remove the path from the list
            selected_path = self.path_list[selected_index[0]]
            self.path_list.remove(selected_path)
            self.update_path_listbox()
        else:
            pass

    def update_path_listbox(self):
        """Clear and then update the listbox"""
        self.path_listbox.delete(0, tk.END)
        for path in self.path_list:
            self.path_listbox.insert(tk.END, path)

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
