import customtkinter as ctk
from modules.api_client import ImmichClient


class LoginFrame(ctk.CTkFrame):
    """This frame holds the login info fields and displays the asset information."""
    def __init__(self, parent: ctk.CTkFrame, client: ImmichClient):
        super().__init__(parent)
        self.client = client

        for col in range(1):
            self.columnconfigure(col, weight=1)  # Even column widths
        for row in range(6):
            self.rowconfigure(row, weight=0)  # Uniform row heights, no extra stretching

        self.login_url = ctk.CTkEntry(self, placeholder_text="Enter base Immich URL")  # Login URL Entry
        self.login_url.grid(row=0, column=0, pady=5, padx=5, sticky="ew")

        self.login_key = ctk.CTkEntry(self, placeholder_text="Enter API key")  # Login API Key Entry
        self.login_key.grid(row=1, column=0, pady=5, padx=5, sticky="ew")

        self.login_button = ctk.CTkButton(self, text="Login", command=self.login_action)  # Login Button
        self.login_button.grid(row=2, column=0, pady=5, padx=5, sticky="ew")

        self.logout_button = ctk.CTkButton(self, text="Logout", command=self.logout_action)  # Logout Button
        self.logout_button.grid(row=3, column=0, pady=5, padx=5, sticky="ew")

        self.logged_in_status = ctk.StringVar(value="Logged in: False")  # Logged-in status label
        self.logged_in_label = ctk.CTkLabel(self, textvariable=self.logged_in_status)
        self.logged_in_label.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        self.immich_user_status = ctk.StringVar(value="User: Unknown")  # Username status label
        self.immich_user_label = ctk.CTkLabel(self, textvariable=self.immich_user_status)
        self.immich_user_label.grid(row=5, column=0, padx=5, pady=5, sticky="ew")

        self.immich_url_status = ctk.StringVar(value="URL: Unknown")  # URL status label
        self.immich_url_label = ctk.CTkLabel(self, textvariable=self.immich_url_status)
        self.immich_url_label.grid(row=6, column=0, padx=5, pady=5, sticky="ew")

        self.immich_total_asset_status = ctk.StringVar(value="Image:0 Video:0 Total:0")  # Asset status label
        self.immich_total_asset_label = ctk.CTkLabel(self, textvariable=self.immich_total_asset_status)
        self.immich_total_asset_label.grid(row=7, column=0, padx=5, pady=5, sticky="ew")

        self.update_login_info()  # Update the displayed information.

    def login_action(self):
        """Gets the entered url and token and validates them by grabbing API info"""
        try:
            self.client.base_url = self.login_url.get()
            self.client.token = self.login_key.get()
            self.update_login_info()
        except Exception as e:
            print(f"Unexpected error logging in: {e}")

    def logout_action(self):
        """Clears the entered url and token, deletes the securely stored credentials, then validates against the
         API to ensure they have been cleared"""
        self.client.base_url = "Unknown"
        self.client.token = "Enter API key"
        self.client.delete_credentials()
        self.update_login_info()

    def update_login_info(self):
        """Attempts to get the users immich statistics and username"""
        self.client.get_asset_statistics()
        self.client.get_my_user()
        if self.client.logged_in:
            self.login_button.configure(state="disabled")
            print(f"Logged in as {self.client.user}")
            print(f"Asset Counts: {self.client.asset_count}")

        else:
            self.login_button.configure(state="normal")
            print("Not Logged In")
        self.logged_in_status.set(f"Logged in: {self.client.logged_in}")
        self.immich_user_status.set(f"User: {self.client.user}")
        self.immich_url_status.set(f"URL: {self.client.base_url}")
        self.immich_total_asset_status.set(f"Image:{self.client.asset_count['images']} "
                                           f"Video:{self.client.asset_count['videos']} "
                                           f"Total:{self.client.asset_count['total']}")
