import os

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

HELP_TEXT = """
*Available commands:*

/help - Show this help message
/echo <message> - Echoes back your message

Send any message to see your *Chat ID*.
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /echo <your message>")
        return
    await update.message.reply_text(text)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Unknown command: `{update.message.text}`\n\n{HELP_TEXT}", parse_mode="Markdown")


async def print_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"Chat ID: {chat_id}")
    await update.message.reply_text(f"Your chat ID is: `{chat_id}`", parse_mode="Markdown")


app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("echo", echo))
app.add_handler(MessageHandler(filters.COMMAND, unknown_command))  # catches unknown commands
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, print_chat_id))

app.run_polling()
