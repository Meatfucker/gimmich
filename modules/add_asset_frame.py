import threading
from typing import List
import customtkinter as ctk
from PIL import Image, ImageDraw
from modules.download_frame import DownloadFrame
from modules.api_client import ImmichClient


class AddDownloadPackFrame(ctk.CTkFrame):
    """This frame displays an available download pack to be chosen and contains the relevant info needed to add it"""
    def __init__(self, parent: ctk.CTkScrollableFrame, download_frame: DownloadFrame, name: str, thumb: ctk.CTkImage,
                 asset_ids: List, color: str):
        super().__init__(parent, border_width=2, border_color="gray", fg_color=color)
        for row in range(1):
            self.rowconfigure(row, weight=1)
        self.columnconfigure(1, weight=1)
        self.parent = parent
        self.download_frame = download_frame
        self.color = color
        self.name = name
        self.thumb = thumb
        self.asset_ids = asset_ids
        self.thumbnail_label = ctk.CTkLabel(self, image=self.thumb, text="")
        self.thumbnail_label.grid(row=0, column=0, padx=2, pady=0)
        self.name_label = ctk.CTkLabel(self, text=self.name)
        self.name_label.grid(row=0, column=1, padx=2, pady=0, sticky="ew")
        self.add_pack_button = ctk.CTkButton(self, text="Add to download", command=self.add_asset_pack, corner_radius=0)
        self.add_pack_button.grid(row=0, column=2, padx=2, pady=0, sticky="ew")

    def add_asset_pack(self):
        """This adds the pack to the download frame."""
        self.download_frame.add_pack(self.name, self.thumb, self.asset_ids, self.color)


class AddAssetFrame(ctk.CTkFrame):
    """This frame displays the album/tag/person/all packs which can be added to the download queue"""
    def __init__(self, parent: ctk.CTkFrame, client: ImmichClient, download_frame: DownloadFrame):
        super().__init__(parent)
        self.client = client
        self.download_frame = download_frame
        self.albums = self.client.get_all_albums()

        for col in range(1):  # Adjust rows and columns for stretching to fit
            self.columnconfigure(col, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(5, weight=1)

        self.scrollable_album_frame = ctk.CTkScrollableFrame(self, label_text="Album List")  # Frame for album packs
        self.scrollable_album_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.scrollable_album_frame.columnconfigure(0, weight=1)

        self.scrollable_tag_frame = ctk.CTkScrollableFrame(self, label_text="Tag List")  # Frame for tag packs
        self.scrollable_tag_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        self.scrollable_tag_frame.columnconfigure(0, weight=1)

        self.scrollable_people_frame = ctk.CTkScrollableFrame(self, label_text="People List")  # Frame for person packs
        self.scrollable_people_frame.grid(row=5, column=0, padx=5, pady=5, sticky="nsew")
        self.scrollable_people_frame.columnconfigure(0, weight=1)

        self.add_all_assets_button = ctk.CTkButton(self, text="Add All Assets", command=self.add_all_assets)
        self.add_all_assets_button.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        self.refresh_albums_tags_button = ctk.CTkButton(self, text="Refresh Albums and Tags",
                                                        command=self.refresh_packs)
        self.refresh_albums_tags_button.grid(row=6, column=0, padx=5, pady=5, sticky="e")

        if self.client.logged_in:
            self.refresh_packs()

    def add_all_assets(self):
        """This function adds a download pack containing all assets on the server"""
        if self.client.logged_in:
            asset_ids = self.client.get_all_assets()
            print(asset_ids)
            thumb_data = self.client.view_asset(asset_ids[0])  # Get image and load thumbnail for pack
            thumb = ctk.CTkImage(light_image=Image.open(thumb_data), size=(32, 32))
            people_pack = AddDownloadPackFrame(self.scrollable_people_frame, self.download_frame,
                                               "ALL ASSETS", thumb, asset_ids, "#212121")
            people_pack.add_asset_pack()

    def refresh_packs(self):
        """This refreshes the available download packs in case you just logged in or things have changed serverside"""
        if self.client.logged_in:  # Run jobs in threads so as to not lock up UI
            threading.Thread(target=self.get_album_info, daemon=True).start()
            threading.Thread(target=self.get_tag_info, daemon=True).start()
            threading.Thread(target=self.get_people_info, daemon=True).start()

    def get_people_info(self):
        """Populates the available people download packs"""
        people_ids = self.client.get_all_people()
        row = 0
        for people_id in people_ids:
            asset_ids = self.client.get_person(people_id)
            thumb_data = self.client.view_asset(asset_ids[0])  # Get image and load thumbnail for pack
            thumb = ctk.CTkImage(light_image=Image.open(thumb_data), size=(32, 32))
            people_pack = AddDownloadPackFrame(self.scrollable_people_frame, self.download_frame,
                                               f"{people_id}", thumb, asset_ids, "#3E2121")
            people_pack.grid(row=row, column=0, padx=5, pady=1, sticky="ew")
            row += 1

    def get_tag_info(self):
        """Populates the available tag download packs"""
        tag_ids = self.client.get_all_tags()
        row = 0
        for tag_name, tag_id in tag_ids.items():  # Iterate over tag timebuckets to collect all tag packs and assets
            tag_time_buckets = self.client.get_tag_time_buckets(tag_id)
            if tag_time_buckets:
                asset_ids = []
                for time_bucket in tag_time_buckets:
                    ids = self.client.get_time_bucket_assets_by_tag(time_bucket, tag_id)
                    asset_ids = asset_ids + ids
                thumb_data = self.client.view_asset(asset_ids[0])  # Get image and load thumbnail for pack
                thumb = ctk.CTkImage(light_image=Image.open(thumb_data), size=(32, 32))
                tag_pack = AddDownloadPackFrame(self.scrollable_tag_frame, self.download_frame, f"{tag_name}",
                                                thumb, asset_ids, "#213421")
                tag_pack.grid(row=row, column=0, padx=5, pady=1, sticky="ew")
                row += 1

    def get_album_info(self):
        """Populates the available album download packs"""
        album_ids = self.client.get_all_albums()
        row = 0
        for album_name, album_id in album_ids.items():
            asset_ids, thumb_id = self.client.get_album_info(album_id)
            thumb_data = self.client.view_asset(thumb_id)  # Get thumbnail for album pack or blank image if no thumb
            try:
                thumb = ctk.CTkImage(light_image=Image.open(thumb_data), size=(32, 32))
            except Exception as e:
                print(f"No thumb found: {album_name} : {e}")
                blank_image = Image.new("RGBA", (32, 32), (255, 255, 255, 0))
                draw = ImageDraw.Draw(blank_image)
                draw.rectangle((0, 0, 31, 31), outline="gray")  # Optional: Add a border
                thumb = ctk.CTkImage(light_image=blank_image, size=(32, 32))
            album_pack = AddDownloadPackFrame(self.scrollable_album_frame, self.download_frame,
                                              f"{album_name}", thumb, asset_ids, "#212150")
            album_pack.grid(row=row, column=0, padx=5, pady=1, sticky="ew")
            row += 1
