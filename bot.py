import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler

# Լոգերի կարգավորում
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Հայերեն 🇦🇲", callback_data="lang_am"),
            InlineKeyboardButton("Русский 🇷🇺", callback_data="lang_ru"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Խնդրում ենք ընտրել լեզուն / Пожалуйста, выберите язык:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "lang_am":
        await query.edit_message_text(text="Դուք ընտրեցիք հայերեն լեզուն։")
    elif query.data == "lang_ru":
        await query.edit_message_text(text="Вы выбрали русский язык.")

def main():
    if not TOKEN:
        print("Սխալ: TOKEN-ը գտնված չէ environment-ում!")
        return

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Բոտը հաջողությամբ սկսեց աշխատել...")
    application.run_polling()

if __name__ == "__main__":
    main()
