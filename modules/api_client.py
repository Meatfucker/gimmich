import requests
import mimetypes
import uuid
import hashlib
import os
import json
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

    @staticmethod
    def delete_credentials():
        """Delete the credentials from the system's keyring."""
        try:
            keyring.delete_password("ImmichClient", "base_url")
            keyring.delete_password("ImmichClient", "token")
            print("Credentials deleted.")
        except Exception as e:
            print(f"No credentials found to delete. {e}")

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
            print(f"Error getting asset statistics. {e}")

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
            print(f"Error getting user. {e}")

    def create_album(self, album_name, ids):
        """Creates an album"""
        url = f"{self.base_url}/api/albums"
        payload = json.dumps({
            'albumName': album_name,
            'albumUsers': [{'role': 'viewer', 'userId': self.user_id}],
            'assetIds': ids
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'x-api-key': self.token
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code in [200, 201]:
                print(f"Album created: {album_name}")
            else:
                print("Error creating album")
        except Exception as e:
            print(f"Error accessing album API: {e}")

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
        try:
            response = requests.request("POST", url, headers=headers, files=files)
            if response.status_code in [200, 201]:

                response_data = response.json()
                print(f'Uploaded {file}')
                asset_id = response_data.get('id')
                status = response_data.get('status')
                return asset_id, status
            else:
                print(f'Error uploading {file}')
        except Exception as e:
            print(f'Error accessing upload API: {e}')

    @staticmethod
    def get_device_id():
        """Returns a unique device ID"""
        return str(uuid.UUID(int=uuid.getnode()))

    @staticmethod
    def generate_asset_id(file):
        """Returns a unique Asset ID"""
        file_stat = os.stat(file)
        metadata = f"{os.path.basename(file)}_{file_stat.st_size}_{file_stat.st_mtime}"
        return str(hashlib.md5(metadata.encode()).hexdigest())

    @staticmethod
    def get_modified_date(file):
        """Returns the last modified date of a file."""
        file_stat = os.stat(file)
        modified_time = file_stat.st_mtime
        return datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
