import os

from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

HELP_TEXT = """
*Available commands:*
/help - Show this help message
/echo <message> - Echoes back your message
/chat - Show information about this chat
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"[/start] user={user.username!r} (id={user.id}) in chat={update.effective_chat.id}")
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"[/help] user={user.username!r} (id={user.id}) in chat={update.effective_chat.id}")
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = " ".join(context.args)
    logger.info(f"[/echo] user={user.username!r} (id={user.id}) args={text!r}")
    if not text:
        await update.message.reply_text("Usage: /echo <your message>")
        return
    await update.message.reply_text(text)


async def chat_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f"[/chat] user={user.username!r} (id={user.id}) in chat={chat.id}")

    lines = [
        "*Chat Information:*",
        f"• *Chat ID:* `{chat.id}`",
        f"• *Chat type:* {chat.type}",
    ]

    if chat.title:
        lines.append(f"• *Chat title:* {chat.title}")
    if chat.username:
        lines.append(f"• *Chat username:* @{chat.username}")

    lines.append("")
    lines.append("*Your Information:*")
    lines.append(f"• *User ID:* `{user.id}`")
    lines.append(f"• *First name:* {user.first_name}")

    if user.last_name:
        lines.append(f"• *Last name:* {user.last_name}")
    if user.username:
        lines.append(f"• *Username:* @{user.username}")

    lines.append(f"• *Is bot:* {user.is_bot}")
    lines.append(f"• *Language code:* {user.language_code or 'N/A'}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cmd = update.message.text
    logger.warning(f"[unknown command] user={user.username!r} (id={user.id}) sent={cmd!r}")
    await update.message.reply_text(f"Unknown command: `{cmd}`\n\n{HELP_TEXT}", parse_mode="Markdown")


async def ignore_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.debug(f"[ignored message] user={user.username!r} (id={user.id}) text={update.message.text!r}")
    # silently ignore — no reply


app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("echo", echo))
app.add_handler(CommandHandler("chat", chat_info))
app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ignore_message))

logger.info("Bot starting...")
app.run_polling()
