import requests
import mimetypes
import uuid
import hashlib
import os
import json
import time
import random
from io import BytesIO
from datetime import datetime
import keyring


class ImmichClient:
    def __init__(self):
        self.device_id = self.get_device_id()
        self.base_url = "Unknown"
        self.token = None
        self.user = "Unknown"
        self.user_id = None
        self.asset_count = {'total': 0, 'images': 0, 'videos': 0}
        self.logged_in = False
        self._load_credentials()

    def _load_credentials(self):
        """Load credentials from the system's keyring."""
        saved_base_url = keyring.get_password("ImmichClient", "base_url")
        saved_token = keyring.get_password("ImmichClient", "token")
        if saved_base_url and saved_token:
            self.base_url = saved_base_url
            self.token = saved_token
            self.logged_in = True

    def _save_credentials(self):
        """Save credentials to the system's keyring."""
        keyring.set_password("ImmichClient", "base_url", self.base_url)
        keyring.set_password("ImmichClient", "token", self.token)

    def add_assets_to_album(self, album_id, asset_ids):
        """Takes an album id and a list of asset ids then adds them to the album"""
        url = f"{self.base_url}/api/albums/{album_id}/assets"
        payload = json.dumps({
            'ids': asset_ids
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("PUT", url, headers=headers, data=payload)
            if response.status_code != 200:
                print(f"Error adding assets to album {album_id}")
        except Exception as e:
            print(f"Error accessing addAssetsToAlbum API: {e}")

    def create_album(self, album_name):
        """Creates an album, returning the album id"""
        url = f"{self.base_url}/api/albums"
        payload = json.dumps({
            'albumName': album_name,
            'albumUsers': [{'role': 'viewer', 'userId': self.user_id}],
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 201:
                response_data = response.json()
                album_id = response_data.get('id')  # Extract the 'id' field
                return album_id
            else:
                print(f"Error creating album {album_name}")
        except Exception as e:
            print(f"Error accessing createAlbum API: {e}")

    def create_tag(self, tag_name):
        """Creates a tag, returning the tag id"""
        url = f"{self.base_url}/api/tags"
        payload = json.dumps({
            'name': tag_name
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 201:
                response_data = response.json()
                tag_id = response_data.get('id')  # Extract the 'id' field
                self.random_tag_color(tag_id)
                return tag_id
            else:
                print(f"Error creating tag {tag_name}")
        except Exception as e:
            print(f"Error accessing createTag API: {e}")

    @staticmethod
    def delete_credentials():
        """Delete the credentials from the system's keyring."""
        try:
            keyring.delete_password("ImmichClient", "base_url")
            keyring.delete_password("ImmichClient", "token")
            print("Credentials deleted.")
        except Exception as e:
            print(f"No credentials found to delete. {e}")

    def download_archive(self, asset_ids):
        """Takes a list of assetIds and returns a file like object containing an archive with the assets"""
        url = f"{self.base_url}/api/download/archive"
        payload = json.dumps({
            'assetIds': asset_ids
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/octet-stream',
            'x-api-key': self.token
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                archive_data = BytesIO(response.content)
                return archive_data
            else:
                print(f"Error downloading archive {asset_ids}")
        except Exception as e:
            print(f"Error accessing downloadArchive API: {e}")

    @staticmethod
    def generate_asset_id(file):
        """Returns a unique Asset ID"""
        file_stat = os.stat(file)
        metadata = f"{os.path.basename(file)}_{file_stat.st_size}_{file_stat.st_mtime}"
        return str(hashlib.md5(metadata.encode()).hexdigest())

    def get_album_info(self, album_id):
        """Returns a list of the assetIds in the album as well as the id of the thumbnail."""
        url = f"{self.base_url}/api/albums/{album_id}"
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            data = response.json()
            thumbnail_id = data.get('albumThumbnailAssetId', None)
            assets = data.get('assets', [])
            asset_ids = [asset.get('id') for asset in assets if 'id' in asset]
            return asset_ids, thumbnail_id
        except Exception as e:
            print(f"Error accessing getAlbumInfo API: {e}")

    def get_all_albums(self):
        """Returns a dict of all album names and associated ids"""
        url = f"{self.base_url}/api/albums"
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                albums = response.json()
                album_dict = {album['albumName']: album['id'] for album in albums}
                return album_dict
            else:
                print("Error getting album list")
        except Exception as e:
            print(f"Error accessing getAllAlbums API: {e}")

    def get_all_tags(self):
        """Returns a list of all tag names and associated ids"""
        url = f"{self.base_url}/api/tags"
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                tags = response.json()
                tag_dict = {tag['name']: tag['id'] for tag in tags}
                return tag_dict
            else:
                print("Error getting tag list")
        except Exception as e:
            print(f"Error accessing getAllTags API: {e}")

    def get_asset_statistics(self):
        """Gets total, image and video asset statistics"""
        url = f"{self.base_url}/api/assets/statistics"
        payload = {}
        headers = {
            'Content-Type': 'multipart/form-data',
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                self.asset_count['total'] = data.get('total', 0)
                self.asset_count['images'] = data.get('images', 0)
                self.asset_count['videos'] = data.get('videos', 0)
            else:
                self.asset_count['total'] = 0
                self.asset_count['images'] = 0
                self.asset_count['videos'] = 0
        except Exception as e:
            self.asset_count['total'] = 0
            self.asset_count['images'] = 0
            self.asset_count['videos'] = 0
            print(f"Error getAssetStatistics API. {e}")

    @staticmethod
    def get_device_id():
        """Returns a unique device ID"""
        return str(uuid.UUID(int=uuid.getnode()))

    @staticmethod
    def get_modified_date(file):
        """Returns the last modified date of a file."""
        file_stat = os.stat(file)
        modified_time = file_stat.st_mtime
        return datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")

    def get_my_user(self):
        """Gets the users login"""
        url = f"{self.base_url}/api/users/me"
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                self.user = data.get('email', "Unknown")
                self.user_id = data.get('id', "Unknown")
                self.logged_in = True
                self._save_credentials()
            else:
                self.user = "Unknown"
                self.logged_in = False
        except Exception as e:
            self.user = "Unknown"
            self.logged_in = False
            print(f"Error accessing getMyUser API. {e}")

    def get_tag_timebuckets(self, tag_id):
        """Returns a list of the timeBuckets with the tag."""
        url = f"{self.base_url}/api/timeline/buckets?size=MONTH&tagId={tag_id}&withStacked=false"
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.token
        }

        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                response_data = response.json()
                time_buckets = []
                for item in response_data:
                    if 'timeBucket' in item:
                        time_buckets.append(item['timeBucket'])
                if time_buckets:
                    return time_buckets
                else:
                    return None

            else:
                print("Error getting time buckets")
        except Exception as e:
            print(f"Error accessing getTimeBuckets API: {e}")

    def get_timebucket_assets_by_tag(self, time_bucket, tag_id):
        """Takes a timeBucket string and tag, then returns the objects within"""
        url = f"{self.base_url}/api/timeline/bucket?size=MONTH&tagId={tag_id}&timeBucket={time_bucket}"
        payload = {}
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                response_data = response.json()
                ids = [item['id'] for item in response_data if 'id' in item]
                return ids
        except Exception as e:
            print(f"Error accessing getTimeBucket API: {e}")

    def random_tag_color(self, tag_id):
        """Assigns the supplied tag a random color"""
        url = f"{self.base_url}/api/tags/{tag_id}"
        tag_color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        payload = json.dumps({
            'color': tag_color
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("PUT", url, headers=headers, data=payload)
            if response.status_code == 200:
                return
            else:
                print(f"Error assigning color:{tag_color} to tag {tag_id}")
        except Exception as e:
            print(f"Error accessing updateTag API: {e}")

    def tag_assets(self, tag_id, asset_ids):
        """Takes a tag id and a list of asset ids then adds them to the tag"""
        url = f"{self.base_url}/api/tags/{tag_id}/assets"
        payload = json.dumps({
            'ids': asset_ids
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("PUT", url, headers=headers, data=payload)
            if response.status_code != 200:
                print(f"Error tagging assets with tag: {tag_id}")
        except Exception as e:
            print(f"Error accessing tagAssets API: {e}")

    def update_asset_description(self, asset_id, asset_description):
        """Updates an asset with the supplied description"""
        url = f"{self.base_url}/api/assets/{asset_id}"
        payload = json.dumps({
            'description': asset_description
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("PUT", url, headers=headers, data=payload)
            if response.status_code != 200:
                print(f"Error adding caption as description. ID:{asset_id} Caption:{asset_description}")
        except Exception as e:
            print(f"Error accessing updateAsset API: {e}")

    def upload_asset(self, file):
        """Uploads a single asset, hashing an AssetId for it. Returning the immich id and upload status"""
        url = f"{self.base_url}/api/assets"
        mime_type, _ = mimetypes.guess_type(file)
        if mime_type is None:
            mime_type = 'application/octet-stream'  # Fallback if MIME type cannot be guessed
        asset_id = self.generate_asset_id(file)
        modified_date = self.get_modified_date(file)
        files = {
            'deviceAssetId': (None, asset_id),  # None ensures no file-type Content-Disposition
            'deviceId': (None, self.device_id),
            'fileCreatedAt': (None, modified_date),
            'fileModifiedAt': (None, modified_date),
            'assetData': (file, open(file, 'rb'), mime_type)
        }
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        attempt = 0
        while attempt < 3:
            try:
                response = requests.request("POST", url, headers=headers, files=files)
                if response.status_code in [200, 201]:

                    response_data = response.json()
                    asset_id = response_data.get('id')
                    status = response_data.get('status')
                    return asset_id, status
                else:
                    print(f'Error uploading {file}')
            except Exception as e:
                print(f'Error accessing uploadAsset API: {e}')
            # Retry logic: wait before the next attempt
            attempt += 1
            if attempt < 3:
                print(f"Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"Max retries reached for {file}")

    def view_asset(self, asset_id):
        """Returns a file-like object of an assets thumbnail."""
        url = f"{self.base_url}/api/assets/{asset_id}/thumbnail"
        payload = {}
        payload = {}
        headers = {
            'Accept': 'application/octet-stream',
            'x-api-key': self.token
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                return image_data
            else:
                print(f"Error getting thumb for {asset_id}")
        except Exception as e:
            print(f'Error accessing viewAsset API')

