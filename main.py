import asyncio
from bot import Scrapper, Config, dump_json


target_channel = input("Enter channel username: ")

folders = Config.get_folders(target_channel)


async def main():
    bot = Scrapper(target_channel)
    await bot.initialize()

    data_dict = {
        "messages": await bot.fetch_messages(),
        "participants": await bot.get_members(),
        "pinned_messages": await bot.get_pinned_messages(),
        "target_info": await bot.fetch_target_info(),
        "admin_logs": await bot.get_admin_log(),
    }

    for name, data in data_dict.items():
        dump_json(data, f"{folders['jsons_folder']}/{name}")


asyncio.run(main())
