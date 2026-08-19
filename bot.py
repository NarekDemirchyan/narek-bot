import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

import os

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Բարև Ձեզ! Բոտն հաջողությամբ աշխատում է։")

async def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    # Աշխատեցնում ենք polling-ը ասինքրոն տարբերակով, որը խնդիր չի ունենա Python 3.14-ի հետ
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Թույլ ենք տալիս բոտին աշխատել անընդհատ
    stop_signal = asyncio.Event()
    await stop_signal.wait()

if __name__ == "__main__":
    asyncio.run(main())
