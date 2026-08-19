import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Կարգավորում ենք լոգավորումը
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Վերցնում ենք թոկենը Render-ի միջավայրից
TOKEN = os.environ.get("TOKEN")

# /start հրամանի ֆունկցիան, որը բերում է լեզվի ընտրության կոճակները
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Հայերեն 🇦🇲", callback_data="lang_am"),
            InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Խնդրում ենք ընտրել լեզուն / Пожалуйста, выберите язык:", reply_markup=reply_markup)

# Կոճակների սեղմման մշակումը
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "lang_am":
        await query.edit_message_text(text="Դուք ընտրեցիք հայերեն լեզուն։")
    elif query.data == "lang_ru":
        await query.edit_message_text(text="Вы выбрали русский язык.")

async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Ավելացնում ենք հրամաններն ու կոճակների լսողները
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Ապահով գործարկում ենք բոտը Python-ի նոր տարբերակների համար
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    print("Բոտը հաջողությամբ աշխատում է...")
    
    # Թույլ ենք տալիս բոտին աշխատել անընդհատ
    stop_signal = asyncio.Event()
    await stop_signal.wait()

if __name__ == "__main__":
    asyncio.run(main())
