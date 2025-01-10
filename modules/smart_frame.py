import threading
from typing import List
import customtkinter as ctk
from PIL import Image
from modules.download_frame import DownloadFrame
from modules.api_client import ImmichClient


class SmartAssetFrame(ctk.CTkFrame):
    """This frame displays the smart search results which can be added to the download queue"""
    def __init__(self, parent: ctk.CTkFrame, client: ImmichClient, download_frame: DownloadFrame):
        super().__init__(parent)
        self.parent = parent
        self.client = client
        self.download_frame = download_frame

        for col in range(1):  # Adjust rows and columns for stretching to fit
            self.columnconfigure(col, weight=1)
        self.rowconfigure(2, weight=1)
        self.search_entry = ctk.CTkEntry(self, placeholder_text="Enter smart search term here")
        self.search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.search_button = ctk.CTkButton(self, text="Smart Search", command=self.start_search_thread)
        self.search_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        self.num_results_label = ctk.CTkLabel(self, text="Number of results")
        self.num_results_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.num_results_entry = ctk.CTkEntry(self, placeholder_text="20")
        self.num_results_entry.grid(row=1, column=1, padx=5, pady=5, sticky="e")

        self.smart_results_frame = ctk.CTkScrollableFrame(self, label_text="Search results")  # Frame for search
        self.smart_results_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew", columnspan=2)

        self.add_smart_pack_button = ctk.CTkButton(self, text="Add to download", command=self.add_smart_pack)
        self.add_smart_pack_button.grid(row=3, column=0, padx=5, pady=5, sticky="ew", columnspan=2)
        # self.scrollable_album_frame.columnconfigure(0, weight=1)

    def add_smart_pack(self):
        asset_ids = []  # List to store asset IDs

        # Iterate over all children in the smart_results_frame
        for child in self.smart_results_frame.winfo_children():
            if isinstance(child, SmartResultFrame):  # Ensure the child is a SmartResultFrame
                asset_ids.append(child.asset_id)  # Collect the asset_id

        name = self.search_entry.get()
        thumb_data = self.client.view_asset(asset_ids[0])  # Get thumbnail data
        thumb = ctk.CTkImage(light_image=Image.open(thumb_data), size=(32, 32))
        self.download_frame.add_pack(name, thumb, asset_ids, "#565116")

    def start_search_thread(self):
        threading.Thread(target=self.smart_search, daemon=True).start()

    def smart_search(self):
        query = self.search_entry.get()
        num_results = self.num_results_entry.get()
        if num_results:
            asset_ids = self.client.search_smart(query, int(num_results))
        else:
            asset_ids = self.client.search_smart(query, 20)

        # Clear previous results
        for child in self.smart_results_frame.winfo_children():
            child.destroy()

        # Dynamically calculate the number of columns
        tile_width = 120
        available_width = self.smart_results_frame.winfo_width()
        num_columns = max(1, available_width // tile_width)  # Ensure at least 1 column

        for index, asset_id in enumerate(asset_ids):
            thumb_data = self.client.view_asset(asset_id)  # Get thumbnail data
            thumb = ctk.CTkImage(light_image=Image.open(thumb_data), size=(64, 64))  # Adjust thumbnail size as needed

            # Create SmartResultFrame
            result = SmartResultFrame(self.smart_results_frame, asset_id, thumb)

            # Grid the result frame
            row = index // num_columns
            col = index % num_columns
            result.grid(row=row, column=col, padx=5, pady=5)

        # Adjust column configurations
        for col in range(num_columns):
            self.smart_results_frame.columnconfigure(col, weight=1)


class SmartResultFrame(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkScrollableFrame, asset_id: List, thumb: ctk.CTkImage):
        super().__init__(parent, border_color="gray", border_width=2, fg_color="#565116")
        self.parent = parent
        self.asset_id = asset_id
        self.thumb = thumb

        self.thumbnail_label = ctk.CTkLabel(self, image=self.thumb, text="", width=0, height=0)
        self.thumbnail_label.grid(row=0, column=0, padx=5, pady=5)
        self.remove_button = ctk.CTkButton(self, text="Remove", command=self.remove_pack, width=0, corner_radius=0)
        self.remove_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    def remove_pack(self):
        self.destroy()  # Remove the current frame from the UI

        # Re-grid remaining children
        children = self.parent.winfo_children()
        tile_width = 100
        available_width = self.parent.winfo_width()
        num_columns = max(1, available_width // tile_width)  # Ensure at least 1 column

        for index, child in enumerate(children):
            row = index // num_columns
            col = index % num_columns
            child.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        # Adjust column configurations
        for col in range(num_columns):
            self.parent.columnconfigure(col, weight=1)
