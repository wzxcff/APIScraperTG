import os
import json
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient


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

    async def close(self):
        await self.client.disconnect()

    async def run(self):
        await self.connect()
        messages = await self.get_messages()
        dump_json(messages)
        await self.close()

    async def get_messages(self):
        messages = []
        avatar_folder = f"avatars/{self.target}"
        os.makedirs(avatar_folder, exist_ok=True)

        async for message in self.client.iter_messages(self.target, limit=10):
            sender_id = message.from_id.user_id if message.from_id else None
            msg_data = {
                'id': message.id,
                'sender_id': sender_id,
                'text': message.text,
                'date': message.date.isoformat(),
            }

            if sender_id:
                try:
                    sender = await self.client.get_entity(sender_id)
                    msg_data['sender_name'] = sender.first_name if sender.first_name else "No name"
                    msg_data['sender_username'] = sender.username if sender.username else None

                    avatar_path = os.path.join(avatar_folder, f"{sender_id}_{sender.first_name}.jpg")
                    if sender.photo and not os.path.exists(avatar_path):
                        await self.client.download_profile_photo(sender, file=avatar_path)

                    msg_data['sender_avatar'] = avatar_path if os.path.exists(avatar_path) else None
                except Exception as e:
                    msg_data['sender_name'] = "Cannot fetch info"
                    msg_data['error'] = str(e)
            else:
                msg_data['sender_name'] = "Unknown sender"
                msg_data['sender_username'] = None
                msg_data['sender_avatar'] = None

            if message.media:
                file_path = await message.download_media(file=f"media/{self.target}/{message.date}.jpg")
                msg_data['media'] = file_path if file_path else None

            messages.append(msg_data)
        return messages


async def main():
    target_username = input("Введите @username группы или канала: ")
    scrapper = Scrapper(target_username)
    await scrapper.run()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()