import os
import random
import time

from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

START_TIME = time.time()

HELP_TEXT = """
*Available commands:*
/help - Show this help message
/echo <message> - Echoes back your message
/chat - Show info about this chat & you
/ping - Check if the bot is alive
/uptime - How long the bot has been running
/roll [NdN] - Roll dice (default: 1d6)
/flip - Flip a coin
"""


# ── /start & /help ────────────────────────────────────────────────────────────


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

    lines += [
        "",
        "*Your Information:*",
        f"• *User ID:* `{user.id}`",
        f"• *First name:* {user.first_name}",
    ]
    if user.last_name:
        lines.append(f"• *Last name:* {user.last_name}")
    if user.username:
        lines.append(f"• *Username:* @{user.username}")
    lines.append(f"• *Language code:* {user.language_code or 'N/A'}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"[/ping] user={user.username!r} (id={user.id})")
    sent = await update.message.reply_text("Pong! 🏓")
    delta_ms = (sent.date.timestamp() - update.message.date.timestamp()) * 1000
    await sent.edit_text(f"Pong! 🏓  `{delta_ms:.0f} ms`", parse_mode="Markdown")


async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"[/uptime] user={user.username!r} (id={user.id})")
    seconds = int(time.time() - START_TIME)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    await update.message.reply_text(f"⏱ Bot has been running for `{h}h {m}m {s}s`", parse_mode="Markdown")


async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    arg = context.args[0] if context.args else "1d6"
    logger.info(f"[/roll] user={user.username!r} (id={user.id}) arg={arg!r}")

    try:
        parts = arg.lower().split("d")
        num_dice = int(parts[0]) if parts[0] else 1
        sides = int(parts[1])
        if not (1 <= num_dice <= 20 and 2 <= sides <= 100):
            raise ValueError
    except (ValueError, IndexError):
        await update.message.reply_text(
            "Usage: /roll [NdN] — e.g. `/roll 2d6`, `/roll 1d20`\nMax 20 dice, max 100 sides.",
            parse_mode="Markdown",
        )
        return

    results = [random.randint(1, sides) for _ in range(num_dice)]
    total = sum(results)
    rolls_str = ", ".join(str(r) for r in results)
    msg = f"🎲 Rolling `{arg}`: [{rolls_str}]"
    if num_dice > 1:
        msg += f" = *{total}*"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def flip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"[/flip] user={user.username!r} (id={user.id})")
    result = random.choice(["Heads 🪙", "Tails 🪙"])
    await update.message.reply_text(f"*{result}*", parse_mode="Markdown")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    cmd = update.message.text
    logger.warning(f"[unknown command] user={user.username!r} (id={user.id}) sent={cmd!r}")
    await update.message.reply_text(f"Unknown command: `{cmd}`\n\n{HELP_TEXT}", parse_mode="Markdown")


async def ignore_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.debug(f"[ignored message] user={user.username!r} (id={user.id}) text={update.message.text!r}")


app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("echo", echo))
app.add_handler(CommandHandler("chat", chat_info))
app.add_handler(CommandHandler("ping", ping))
app.add_handler(CommandHandler("uptime", uptime))
app.add_handler(CommandHandler("roll", roll))
app.add_handler(CommandHandler("flip", flip))
app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ignore_message))

logger.info("Bot starting...")
app.run_polling()
