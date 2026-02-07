import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()


class TelegramAlertEngine:

    def __init__(self):
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if not self.token or not self.chat_id:
            print("[TELEGRAM] ❌ Missing token or chat id")
            self.bot = None
        else:
            self.bot = Bot(token=self.token)

    # ----------------------------------------
    # INTERNAL ASYNC SENDER
    # ----------------------------------------
    async def _send_async(self, message: str):

        if not self.bot:
            return

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message
            )

        except Exception as e:
            print(f"[TELEGRAM ERROR] {e}")

    # ----------------------------------------
    # PUBLIC SEND METHOD
    # ----------------------------------------
    def send(self, message: str):
        """
        Non-blocking Telegram sender
        Safe for trading loop
        """

        try:
            asyncio.run(self._send_async(message))
        except RuntimeError:
            # If event loop already running
            loop = asyncio.get_event_loop()
            loop.create_task(self._send_async(message))

        except Exception as e:
            print("Telegram error: ", e)


# ⭐ GLOBAL INSTANCE
telegram_alert = TelegramAlertEngine()

