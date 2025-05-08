import asyncio
import os
import threading
from bot import Scraper, Config, dump_json
from bot.utils import get_last_message_id
from bot import Config
from bot.settings import logging


target_channel = ""
start_from_last_msg = False
specify_limit_offset = False
user_limit, user_offset = None, None

def ask_for_limit_n_offset():
    global user_limit, user_offset
    user_limit = int(input("Enter the number of messages you would like to fetch (limit): "))
    user_offset = int(input("Enter the number of message_id from where program needs to start (offset): "))


def menu():
    global target_channel, start_from_last_msg, specify_limit_offset
    target_channel = input("Enter channel username: ")
    start_from_last_msg = True if input("Do you want to start from last scraped message? y/n: ") == "y" else False
    specify_limit_offset = True if input("Do you want to specify limit and offset manually? y/n: ") == "y" else False
    if specify_limit_offset:
        ask_for_limit_n_offset()


def input_listener():
    while True:
        cmd = input("Type \"exit\" to safe exit program: ")
        if cmd.strip().lower() == "exit":
            Config.stop_event.set()
            print("Program stopped by user\nwaiting for everything to save...")
            break




async def main():
    global user_limit, user_offset
    folders = Config.get_folders(target_channel)
    bot = Scraper(target_channel)
    await bot.initialize()
    offset = 0
    limit = 100

    threading.Thread(target=input_listener, daemon=True).start()

    if Config.stop_event.is_set():
        return

    if start_from_last_msg:
        offset = get_last_message_id(os.path.join(folders["jsons_folder"], "messages.json"))
        print(f"Set offset of fetch_message to last message_id: {offset}")

    if specify_limit_offset:
        if user_limit is not None:
            limit = user_limit
            logging.debug("Found user specified limit, overriding default value")
        if user_offset is not None:
            offset = user_offset
            logging.debug(f"Found user specified offset, overriding last message_id offset")

    logging.debug(f"Passed limit: {limit}, offset: {offset}")
    data_dict = {
        "messages": await bot.fetch_messages(limit=limit, offset=offset),
        "participants": await bot.get_members(),
        "pinned_messages": await bot.get_pinned_messages(),
        "target_info": await bot.fetch_target_info(),
        "admin_logs": await bot.get_admin_log(),
    }

    for name, data in data_dict.items():
        dump_json(data, f"{folders['jsons_folder']}/{name}")

if __name__ == "__main__":
    menu()
    asyncio.run(main())
