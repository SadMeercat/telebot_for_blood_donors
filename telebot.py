import os
from dotenv import load_dotenv
from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters, CallbackQueryHandler

EMPTY, REGION, CITY, DISTRICT = range(4)

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
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton('Выбрать больницу для сдачи крови', callback_data='choose_hospital')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Привет {user.full_name}! Этот бот создан для отслеживания донорского светофора. Давай выберем больницу", reply_markup=reply_markup)
    return REGION
    

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Просим ввести регион
    await query.message.reply_text("Введите ваш регион:")
    return CITY
    
# Получаем регион
async def get_region(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    region = update.message.text
    context.user_data['region'] = region
    await update.message.reply_text(f"Ваш регион: {region}. Введите ваш город:")
    return DISTRICT

# Получаем город
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    city = update.message.text
    context.user_data['city'] = city
    await update.message.reply_text(f"Ваш город: {city}. Введите ваш район:")
    return EMPTY  # После района можно завершить или продолжить работу

# Получаем район
async def get_district(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    district = update.message.text
    context.user_data['district'] = district

    # Выводим данные в консоль
    region = context.user_data.get('region')
    city = context.user_data.get('city')
    await update.message.reply_text(f"Регион: {region}, Город: {city}, Район: {district}. Регистрация завершена.")
    print(f"Region: {region}, City: {city}, District: {district}")

    return ConversationHandler.END  # Завершаем диалог

# Отмена действия
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Регистрация отменена.")
    return ConversationHandler.END

def main():
    load_dotenv()
    app = ApplicationBuilder().token(os.getenv('TELEGRAM_API')).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            REGION: [CallbackQueryHandler(button_callback, pattern='choose_hospital')],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_region)],
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            EMPTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_district)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conversation_handler)
    app.run_polling()