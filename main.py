import json
from telethon.sync import TelegramClient
import os
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
channel_username = "testingKarazin"

client = TelegramClient("session_name", api_id, api_hash)


async def main():
    await client.start()

    messages = []
    async for message in client.iter_messages(channel_username, limit=10):
        msg_data = {
            'id': message.id,
            'sender': message.sender_id,
            'text': message.text,
            'date': message.date.isoformat(),
        }

        if message.media:
            msg_data['media'] = str(message.media)  # Сохраняем описание медиа

        messages.append(msg_data)

    with open('messages.json', 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)
    
    list_of_users = await client.get_participants(channel_username)
    for user in list_of_users:
        print(user)


with client:
    client.loop.run_until_complete(main())