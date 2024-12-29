import customtkinter as ctk
import sys
from modules.gui import LoginFrame, PathFrame, CheckboxFrame, InfoFrame, ConsoleOutput


# Redirect console output to a Text widget


# Create the customtkinter app
class GimmichApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("gimmich")
        self.main_frame = ctk.CTkFrame(self)  # Main container frame
        self.main_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.top_frame = ctk.CTkFrame(self.main_frame)  # Frame for buttons and info
        self.top_frame.grid(row=0, column=0, padx=5, pady=5, sticky="new")

        self.console_text = ctk.CTkTextbox(self.main_frame, wrap="word")  # Console log
        self.console_text.grid(row=2, column=0, padx=5, pady=5, sticky="sew")
        sys.stdout = ConsoleOutput(self.console_text)  # Redirect console output to the Text widget

        self.path_list = []  # Initialize the list to store paths
        self.path_frame = PathFrame(parent=self.top_frame, path_list=self.path_list)  # Path frame
        self.path_frame.grid(row=1, column=2, padx=5, pady=5, sticky="ns")

        self.checkbox_frame = CheckboxFrame(self.top_frame)  # Checkbox frame
        self.checkbox_frame.grid(row=1, column=3, padx=5, pady=5, sticky="ns")
        self.checkbox_states = self.checkbox_frame.get_states()

        self.info_frame = InfoFrame(self.top_frame, self.path_list, self.checkbox_states)  # Info frame
        self.info_frame.grid(row=1, column=4, padx=5, pady=5, sticky="nse")

        self.login_frame = LoginFrame(self.top_frame, self.info_frame)  # Login frame
        self.login_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsw")

    def on_closing(self):
        # Restore sys.stdout before closing
        sys.stdout = sys.__stdout__
        self.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("dark-blue")
    gimmich = GimmichApp()
    gimmich.protocol("WM_DELETE_WINDOW", gimmich.on_closing)
    gimmich.mainloop()
