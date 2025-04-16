import asyncio
from .scraper import Scraper


async def main():
    target_username = input("Введите @username группы или канала: ")
    scrapper = Scraper(target_username)
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