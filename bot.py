import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Կարգավորում ենք լոգավորումը, որպեսզի տեսնենք հնարավոր սխալները
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Բոտի տոկենը, որը վերցվում է Render-ի միջավայրի փոփոխականներից
TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Այս ֆունկցիան աշխատում է, երբ օգտատերը գրում է /start"""
    await update.message.reply_text("Բարև Ձեզ! Բոտն հաջողությամբ աշխատում է։")

def main():
    # Ստեղծում ենք բոտի հավելվածը
    application = ApplicationBuilder().token(TOKEN).build()

    # Ավելացնում ենք /start հրամանի հանդիպման կառավարիչը
    application.add_handler(CommandHandler("start", start))

    # Գործարկում ենք բոտը
    application.run_polling()

if __name__ == "__main__":
    main()
