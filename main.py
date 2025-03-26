from bot import Scrapper, start_bot, Config
from bot.utils import dump_json
import asyncio

target = "testingKarazin"

folders = Config.get_folders(target)


async def main():
    test_bot = Scrapper(target)
    await test_bot.initialize()
    messages = await test_bot.fetch_messages()
    dump_json(messages, f"{folders['jsons_folder']}/messages")
    print(messages)

    await test_bot.close()

asyncio.run(main())

