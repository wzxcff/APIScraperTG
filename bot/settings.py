import os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv(dotenv_path='.env')


class Config:
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    client = TelegramClient("session_name", api_id=API_ID, api_hash=API_HASH)

    @staticmethod
    def get_folders(target_channel):
        return {
            "avatar_folder": f"{target_channel}/avatars",
            "target_folder": f"{target_channel}",
            "participants_avatars_folder": f"{target_channel}/participants_avatars",
            "media_folder": f"{target_channel}/media",
            "jsons_folder": f"{target_channel}/jsons",
        }
