import os
from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        rf"Привет {user.full_name}! Этот бот создан для отслеживания донорского светофора. Давай выберем больницу"
    )
    await update.message.reply_text(
        "Введи нужный регион"
    )


load_dotenv()
app = ApplicationBuilder().token(os.getenv('TELEGRAM_API')).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()