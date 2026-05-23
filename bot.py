# -*- coding: utf-8 -*-
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import google.generativeai as genai

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

logging.basicConfig(level=logging.INFO)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = (
    "You are Narek AI assistant. Reply to people who message Narek. "
    "Rules: "
    "1. Reply in SAME LANGUAGE as user (Armenian, Russian, English, etc.). "
    "2. If user wrote Armenian words using Latin letters (like vonts es, inch ka, barev, ayo, che), ALWAYS reply in Armenian script. "
    "3. Be natural, warm and concise. "
    "4. You are already introduced as AI, just answer naturally."
)

GREETING = 'Բարև! Ես Նարեկի AI օգնական եմ։\nԵս կպատասխանեմ, մինչև ինքը անձամբ կգա ու կպատասխանի։'

user_greeted = set()

@dp.message()
async def handle(message: Message):
    uid = message.from_user.id
    text = message.text or message.caption or ""
    if not text:
        return
    try:
        prompt = f"{SYSTEM_PROMPT}\nUser message: {text}\nYour reply:"
        resp = model.generate_content(prompt)
        reply = resp.text.strip()
        if uid not in user_greeted:
            user_greeted.add(uid)
            reply = GREETING + "\n\n" + reply
        await message.reply(reply)
    except Exception as e:
        logging.error(e)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
