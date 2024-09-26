import os
from dotenv import load_dotenv
from telegram import ForceReply, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters

REGION, CITY, DISTRICT = range(3)

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send a message when the command /start is issued."""
#     user = update.effective_user
#     await update.message.reply_text(
#         rf"Привет {user.full_name}! Этот бот создан для отслеживания донорского светофора. Давай выберем больницу"
#     )
#     await update.message.reply_text(
#         "Введи нужный регион"
#     )

# Функция для старта разговора
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Привет! Пожалуйста, введите ваш регион:")
    return REGION

# Функция для получения региона
async def receive_region(update: Update, context: CallbackContext) -> int:
    region = update.message.text
    context.user_data['region'] = region  # Сохраняем введенный регион
    await update.message.reply_text(f"Регион '{region}' принят. Теперь введите ваш город:")
    return CITY

# Функция для получения города
async def receive_city(update: Update, context: CallbackContext) -> int:
    city = update.message.text
    context.user_data['city'] = city  # Сохраняем введенный город
    await update.message.reply_text(f"Город '{city}' принят. Теперь введите ваш район:")
    return DISTRICT

# Функция для получения района
async def receive_district(update: Update, context: CallbackContext) -> int:
    district = update.message.text
    context.user_data['district'] = district  # Сохраняем введенный район
    await update.message.reply_text(f"Район '{district}' принят. Спасибо за ввод данных!")
    
    # Формируем словарь и выводим его в консоль
    user_data = {
        'region': context.user_data['region'],
        'city': context.user_data['city'],
        'district': district
    }
    print(user_data)
    return ConversationHandler.END  # Завершаем разговор

# Функция для отмены
async def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END

def main():
    load_dotenv()
    app = ApplicationBuilder().token(os.getenv('TELEGRAM_API')).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REGION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_region)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_city)],
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_district)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    #app.add_handler(CommandHandler("start", start))
    app.add_handler(conversation_handler)
    app.run_polling()