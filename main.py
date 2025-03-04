import os
import json
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat


def dump_json(data, filename):
    with open(f'{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


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
        dump_json(messages, "messages")
        participants = await self.get_members()
        dump_json(participants, "participants")
        await self.close()

    async def get_messages(self):
        messages = []
        avatar_folder = f"avatars/{self.target}"
        os.makedirs(avatar_folder, exist_ok=True)

        async for message in self.client.iter_messages(self.target, limit=10):
            sender_id = message.from_id.user_id if message.from_id else None
            msg_data = {
                'id': message.id,
                'text': message.text,
                'date': message.date.isoformat(),
            }

            sender_dict = {}
            if sender_id:
                try:
                    sender = await self.client.get_entity(sender_id)
                    sender_dict['user_id'] = sender_id
                    sender_dict['first_name'] = sender.first_name if sender.first_name else None
                    sender_dict['last_name'] = sender.last_name if sender.last_name else None
                    sender_dict['username'] = sender.username if sender.username else None

                    avatar_path = os.path.join(avatar_folder, f"{sender_id}_{sender.first_name}.jpg")
                    if sender.photo and not os.path.exists(avatar_path):
                        await self.client.download_profile_photo(sender, file=avatar_path)

                    sender_dict['avatar'] = avatar_path if os.path.exists(avatar_path) else None
                except Exception as e:
                    sender_dict['name'] = "Cannot fetch info"
                    msg_data['error'] = str(e)
            else:
                sender_dict['first_name'] = "Unknown sender"
                sender_dict['last_name'] = "Unknown sender"
                sender_dict['username'] = None
                sender_dict['avatar'] = None
            msg_data['sender'] = sender_dict

            if message.media:
                file_path = await message.download_media(file=f"media/{self.target}/{message.date}_{message.id}.jpg")
                msg_data['media'] = file_path if file_path else None

            messages.append(msg_data)
        return {"target": self.target, "messages": messages}

    async def get_members(self):
        entity = await self.client.get_entity(self.target)
        users = []
        users_dict = {"target": self.target}
        users_list = []

        if isinstance(entity, Channel):
            if entity.megagroup:
                users = await self.client.get_participants(self.target)
            else:
                user = await self.client.get_me()
                permissions = await self.client.get_permissions(self.target, user.id)
                if permissions.is_admin or permissions.is_creator:
                    users = await self.client.get_participants(self.target)
                else:
                    print("Cannot fetch members. You're not an admin.")
        elif isinstance(entity, Chat):
            users = await self.client.get_participants(self.target)
        else:
            print("Unknown entity type")

        if users:
            for user in users:
                user_entity = await self.client.get_entity(user)

                os.makedirs(f"participants_avatars/{self.target}", exist_ok=True)
                participant_path = f"participants_avatars/{self.target}/{user.id}_{user.first_name}.jpg"

                user_data = {
                    'user_id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }

                if user.photo and not os.path.exists(participant_path):
                    await self.client.download_profile_photo(user_entity, file=participant_path)

                user_data['avatar'] = participant_path if os.path.exists(participant_path) else None
                users_list.append(user_data)

        users_dict["participants"] = users_list

        return users_dict


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
