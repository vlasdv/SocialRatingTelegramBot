from telegram.ext import Application, MessageHandler, filters
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def echo(update, context):
    await update.message.reply_text("Привет, я на Fly.io!")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, echo))

app.run_polling()