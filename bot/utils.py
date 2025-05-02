import json
from .settings import Config
from telethon.errors import FloodWaitError


def dump_json(data, filename: str):
    """
    Dumps info in json file.\n
    Filename can be used for specifying path too.
    """
    with open(f'{filename}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


async def safe_call(coro, method_name="unknown"):
    """
    This method used to make safe calls, and stabilising them with try except expression.
    :param coro: coroutine,
    :param method_name: method name (optional), used to make debugging easier.
    """
    attempts = 0
    max_attempts = Config.max_attempts
    while True:
        try:
            return await coro
        except FloodWaitError as e:
            print(f"[FloodWait] - [{method_name}] Too many requests sent! Waiting for {e.seconds} seconds...")
        except Exception as e:
            if attempts > max_attempts:
                raise FloodWaitError(f"Error during calling method \"{method_name}\". Program used all of {max_attempts} available attempts.")
            print(f"[Exception] - [{method_name}] Unexpected exception occurred: {e}\nRetrying...")
            attempts += 1