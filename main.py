import os
import json
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.types import Channel, Chat


def dump_json(messages):
    with open('messages.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)


class Scrapper:
    def __init__(self, target_channel):
        load_dotenv()
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.target = target_channel
        self.client = TelegramClient("session_name", self.api_id, self.api_hash)

    async def connect(self):
        await self.client.start()
        if not self.client.is_connected():
            print("Client cannot connect!")

    async def close(self):
        await self.client.disconnect()
        print("Client disconnected!")

    async def run(self):
        await self.connect()
        print(await self.get_messages())
        print(await self.get_members())
        await self.close()

    async def get_messages(self):
        messages = []
        async for message in self.client.iter_messages(self.target, limit=10):
            msg_data = {
                'id': message.id,
                'sender': message.sender_id,
                'text': message.text,
                'date': message.date.isoformat(),
            }
            if message.media:
                file_path = await message.download_media(file=f"media/{self.target}/{message.date}.jpg")
                msg_data['media'] = file_path if file_path else "Failed to download"

            messages.append(msg_data)

        return messages

    async def get_members(self):
        entity = await self.client.get_entity(self.target)

        if isinstance(entity, Channel):
            if entity.megagroup:
                return await self.client.get_participants(self.target)
            else:
                user = await self.client.get_me()
                permissions = await self.client.get_permissions(self.target, user.id)
                if permissions.is_admin or permissions.is_creator:
                    return await self.client.get_participants(self.target)
                else:
                    print("Cannot fetch members in a private channel. You're not an admin.")
                    return []
        elif isinstance(entity, Chat):
            return await self.client.get_participants(self.target)


if __name__ == "__main__":
    target_username = input("Enter target channel or group username (e.g., @channel_name): ")
    scrapper = Scrapper(target_username)

    import asyncio

    asyncio.run(scrapper.run())
