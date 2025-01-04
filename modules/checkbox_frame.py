import customtkinter as ctk


class CheckboxFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Variables for checkboxes
        self.recursive_var = ctk.BooleanVar(value=False)
        self.dirs_as_albums_var = ctk.BooleanVar(value=False)
        self.album_input_var = ctk.BooleanVar(value=False)
        self.dirs_as_tags_var = ctk.BooleanVar(value=False)
        self.tag_input_var = ctk.BooleanVar(value=False)
        self.captions_var = ctk.BooleanVar(value=False)
        self.captions_as_tags_var = ctk.BooleanVar(value=False)

        # Layout grid configuration
        for col in range(2):
            self.columnconfigure(col, weight=1)  # Even column widths
        for row in range(6):
            self.rowconfigure(row, weight=0)  # Uniform row heights, no extra stretching

        # Create and place widgets
        self.create_checkbox("Recursive", self.recursive_var, 0, 0)
        self.create_checkbox("Directories as albums", self.dirs_as_albums_var, 0, 1)
        self.create_checkbox("Album Name", self.album_input_var, 3, 0)
        self.album_input_entry = ctk.CTkEntry(self, placeholder_text="Enter Album Name")
        self.album_input_entry.grid(row=3, column=1, pady=5, padx=5, sticky="ew")
        self.create_checkbox("Directories as tags", self.dirs_as_tags_var, 2, 1)
        self.create_checkbox("Tag Name", self.tag_input_var, 4, 0)
        self.tag_input_entry = ctk.CTkEntry(self, placeholder_text="Enter Tag Name")
        self.tag_input_entry.grid(row=4, column=1, pady=5, padx=5, sticky="ew")
        self.create_checkbox("Import captions", self.captions_var, 2, 0)
        self.create_checkbox("Captions as tags", self.captions_as_tags_var, 5, 0)
        self.caption_delimiter_entry = ctk.CTkEntry(self, placeholder_text="Enter delimiters, eg: ,.|")
        self.caption_delimiter_entry.grid(row=5, column=1, pady=5, padx=5, sticky="ew")

    def create_checkbox(self, text, variable, row, column):
        """Helper to create a checkbox."""
        checkbox = ctk.CTkCheckBox(self, text=text, variable=variable)
        checkbox.grid(row=row, column=column, pady=5, padx=5, sticky="w")  # Reduced padding for uniformity
        return checkbox

    def get_states(self):
        """Returns the states of all checkboxes and input fields as a dictionary."""
        return {
            "recursive": self.recursive_var.get(),
            "directory_names_as_albums": self.dirs_as_albums_var.get(),
            "album_input_enabled": self.album_input_var.get(),
            "album_input": self.album_input_entry.get(),
            "directory_names_as_tags": self.dirs_as_tags_var.get(),
            "tag_input_enabled": self.tag_input_var.get(),
            "tag_input": self.tag_input_entry.get(),
            "import_captions": self.captions_var.get(),
            "captions_as_tags": self.captions_as_tags_var.get(),
            "caption_delimiters": self.caption_delimiter_entry.get()
        }
