import os
import logging
from telegram import Update, Sticker
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import sqlite3

# Telegram
BOT_ID = 8402154631
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Google Sheets
SHEET_ID = '1Jub3HZ4p2EVshVfw2L3WM_sabb5juyq_j_Aj7KmrK5o'
SHEET_NAME = 'Лист1'

# Stickers
STICKERS = {
    "SMALL_POS": 'CAACAgIAAxkBAAE6GtlorDG_sXk0gJzvDjKSP7C7G1AVqwACGw8AAtGBEUtvRkAii2YBiDYE',
    "LARGE_POS": 'CAACAgIAAxkBAAE6Gy9orDcTMz4zDUhDKBQ8OZD1xT15GQACtAwAAlp7EEs4EXBGHIGMbjYE',
    "NEUTRAL_UP": 'CAACAgIAAxkBAAE6GzlorDe0NflUYLkksi8J8Kb5Hg4S9QACSREAAtEOgUg5dzdn9iFN-TYE',
    "NEUTRAL_DOWN": 'CAACAgIAAxkBAAE6HIVorExvaEXKfZ02JrDDoq4x07YbawACiQsAAoeWEEsdmpQkx6Dk3TYE',
    "SMALL_NEG": 'CAACAgIAAxkBAAE6G1VorDh4mM1Ko2beV4j8i4cTxc-tDAACNSAAAmevwEhX-iyeQLyPZjYE',
    "LARGE_NEG": 'CAACAgIAAxkBAAE6G1lorDiONBJ-6Z8CFNc1zUQFXw-88wACdiMAAlLlwEhjQeCEPHoELjYE',
    "UP": 'CAACAgIAAxkBAAE6G29orDl3zX4OWaHEg113YiMDWz4nsAACThwAAiRNwUibQduLU5osdDYE',
    "DOWN": 'CAACAgIAAxkBAAE6G0RorDfiTL91fIY5ayf_wAJ6ZigenwAClA4AAjFS2EoIn54JXM7RkTYE',
    "SELF": 'CAACAgIAAxkBAAE6HCZorEloaAG2l82Q5mqDOGRDz-kmrwAC1AkAAvCvCEv5DzmZH6j0uTYE'
}

# Setup logging
logging.basicConfig(level=logging.INFO)


# Setup SQLite access
def get_db_connection():
    conn = sqlite3.connect("ratings.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    """)
    return conn

def update_rating(user_id: str, name: str, delta: int) -> int:
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT score FROM ratings WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

    if row:
        new_rating = row[0] + delta
        cur.execute("UPDATE ratings SET score = ?, name = ? WHERE user_id = ?", (new_rating, name, user_id))
    else:
        new_rating = delta
        cur.execute("INSERT INTO ratings (user_id, name, score) VALUES (?, ?, ?)", (user_id, name, new_rating))

    conn.commit()
    conn.close()
    return new_rating

def build_response_text(name: str, rating: int, direction: str) -> str:
    if direction == 'up':
        return f"✨ Плюс социальный рейтинг {name}!\n🌈 Текущий рейтинг: {rating}"
    else:
        return f"💩 Минус социальный рейтинг для {name}!\n🌈 Текущий рейтинг: {rating}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.reply_to_message or not msg.text:
        return

    text = msg.text.strip().lower()
    sender = msg.from_user
    target = msg.reply_to_message.from_user

    if sender.id == target.id:
        await msg.reply_text("Ай-яй!")
        await msg.reply_sticker(STICKERS["SELF"])
        return

    if target.id == BOT_ID:
        await msg.reply_text("Да восстанут машины из ядерного пепла! 🤖")
        return

    if text in ['плюс вайб', '👍', '❤️', '🔥']:
        rating = update_rating(target.id, target.first_name, 1)
        await msg.reply_text(build_response_text(target.first_name, rating, 'up'))

        if rating == 5:
            await msg.reply_sticker(STICKERS["SMALL_POS"])
        elif rating == 10:
            await msg.reply_sticker(STICKERS["LARGE_POS"])
        elif rating == 0:
            await msg.reply_sticker(STICKERS["NEUTRAL_UP"])
        else:
            await msg.reply_sticker(STICKERS["UP"])

    elif text in ['минус вайб', '👎', '💩', '🤡']:
        rating = update_rating(target.id, target.first_name, -1)
        await msg.reply_text(build_response_text(target.first_name, rating, 'down'))

        if rating == -5:
            await msg.reply_sticker(STICKERS["SMALL_NEG"])
        elif rating == -10:
            await msg.reply_sticker(STICKERS["LARGE_NEG"])
        elif rating == 0:
            await msg.reply_sticker(STICKERS["NEUTRAL_DOWN"])
        else:
            await msg.reply_sticker(STICKERS["DOWN"])

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, handle_message))
    app.run_polling()