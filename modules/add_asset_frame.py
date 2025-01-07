import threading
import customtkinter as ctk
from PIL import Image


class AddDownloadPackFrame(ctk.CTkFrame):
    def __init__(self, parent, download_frame, name, thumb, asset_ids):
        super().__init__(parent, border_width=2, border_color="gray")
        for row in range(1):
            self.rowconfigure(row, weight=1)
        self.columnconfigure(1, weight=1)
        self.parent = parent
        self.download_frame = download_frame
        self.name = name
        self.thumb = thumb
        self.asset_ids = asset_ids
        self.thumbnail_label = ctk.CTkLabel(self, image=self.thumb, text="")
        self.thumbnail_label.grid(row=0, column=0, padx=5, pady=1)
        self.name_label = ctk.CTkLabel(self, text=self.name)
        self.name_label.grid(row=0, column=1, padx=5, pady=1, sticky="ew")
        self.add_pack_button = ctk.CTkButton(self, text="Add to download", command=self.add_album_pack)
        self.add_pack_button.grid(row=0, column=2, padx=5, pady=1, sticky="ew")

    def add_album_pack(self):
        self.download_frame.add_album_pack(self.name, self.thumb, self.asset_ids)


class AddAssetFrame(ctk.CTkFrame):
    def __init__(self, parent, client, download_frame):
        super().__init__(parent)
        self.client = client
        self.download_frame = download_frame
        self.albums = self.client.get_all_albums()

        # Configure layout
        for col in range(1):
            self.columnconfigure(col, weight=1)
        self.rowconfigure(1, weight=1)  # Make the scrollable frame fill the top space
        self.rowconfigure(1, weight=1)  # Allow space for the button

        # Add a scrollable frame
        self.album_list_label = ctk.CTkLabel(self, text="Album List")
        self.album_list_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.scrollable_album_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_album_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.scrollable_album_frame.columnconfigure(0, weight=1)

        self.tag_list_label = ctk.CTkLabel(self, text="Tag List")
        self.tag_list_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.scrollable_tag_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_tag_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        self.scrollable_tag_frame.columnconfigure(0, weight=1)
        self.refresh_albums_tags_button = ctk.CTkButton(self, text="Refresh Albums and Tags",
                                                        command=self.refresh_albums_tags)
        self.refresh_albums_tags_button.grid(row=4, column=0, padx=5, pady=5, sticky="e")

        if self.client.logged_in:
            self.refresh_albums_tags()


    def refresh_albums_tags(self):
        if self.client.logged_in:
            threading.Thread(target=self.get_album_info, daemon=True).start()
            threading.Thread(target=self.get_tag_info, daemon=True).start()


    def get_tag_info(self):
        tag_ids = self.client.get_all_tags()
        row = 0
        for tag_name, tag_id in tag_ids.items():
            tag_timebuckets = self.client.get_tag_timebuckets(tag_id)
            if tag_timebuckets:
                asset_ids = []
                for time_bucket in tag_timebuckets:
                    ids = self.client.get_timebucket_assets_by_tag(time_bucket, tag_id)
                    asset_ids = asset_ids + ids
                thumb_data = self.client.view_asset(asset_ids[0])
                thumb = ctk.CTkImage(light_image=Image.open(thumb_data), size=(50, 50))
                tag_pack = AddDownloadPackFrame(self.scrollable_tag_frame, self.download_frame, f"{tag_name}-tag",
                                                thumb, asset_ids)
                tag_pack.grid(row=row, column=0, padx=5, pady=1, sticky="ew")
                row += 1


    def get_album_info(self):
        album_ids = self.client.get_all_albums()
        row = 0
        for album_name, album_id in album_ids.items():
            asset_ids, thumb_id = self.client.get_album_info(album_id)
            thumb_data = self.client.view_asset(thumb_id)
            thumb = ctk.CTkImage(light_image=Image.open(thumb_data), size=(50, 50))
            album_pack = AddDownloadPackFrame(self.scrollable_album_frame, self.download_frame,
                                              f"{album_name}-album", thumb, asset_ids)
            album_pack.grid(row=row, column=0, padx=5, pady=1, sticky="ew")
            row += 1



