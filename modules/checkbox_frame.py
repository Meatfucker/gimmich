import customtkinter as ctk


class CheckboxFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Variables for checkboxes
        self.recursive = ctk.BooleanVar(value=False)
        self.names_as_albums = ctk.BooleanVar(value=False)
        self.album_input_enabled = ctk.BooleanVar(value=False)

        # Checkboxes
        self.recursive = ctk.CTkCheckBox(self, text="Recursive", variable=self.recursive)
        self.recursive.grid(row=0, column=0, pady=5, padx=5, sticky="w")
        self.names_as_albums = ctk.CTkCheckBox(self, text="Directory names as albums", variable=self.names_as_albums)
        self.names_as_albums.grid(row=1, column=0, pady=5, padx=5, sticky="w")
        self.album_input = ctk.CTkCheckBox(self, text="Album Name", variable=self.album_input_enabled)
        self.album_input.grid(row=2, column=0, pady=5, padx=5, sticky="w")
        self.album_input_entry = ctk.CTkEntry(self, placeholder_text="Enter Album Name")
        self.album_input_entry.grid(row=3, column=0, pady=5, padx=5)


    def get_states(self):
        """Returns the states of all checkboxes as a dictionary."""
        return {
            "recursive": self.recursive.get(),
            "directory_names_as_albums": self.names_as_albums.get(),
            "album_input_enabled": self.album_input_enabled.get(),
            "album_input": self.album_input_entry.get(),
        }
