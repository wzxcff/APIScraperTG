import asyncio
from .scraper import Scrapper


async def main():
    target_username = input("Введите @username группы или канала: ")
    scrapper = Scrapper(target_username)
    await scrapper.run()


async def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()