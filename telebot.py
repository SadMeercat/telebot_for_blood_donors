import os
from dotenv import load_dotenv
from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters, CallbackQueryHandler

from models.city_model import get_city_id
from models.district_model import get_district_id
from models.hospital_model import get_hospital_id
from models.region_model import get_region_id
from models.user_model import User, add_user_to_db

EMPTY, REGION, CITY, DISTRICT, HOSPITAL = range(5)

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
    found_reg, result = get_region_id(region)
    if not found_reg:
        if result:
            await update.message.reply_text(f"Некорректный ввод. Возможно Вы имели ввиду:\r\n {'\r\n'.join(result)}")
        else:
            await update.message.reply_text(f"Некорректный ввод. Ничего похожего не найдено")
        return CITY
    context.user_data['region'] = result
    await update.message.reply_text(f"Ваш регион: {region}. Введите ваш город:")
    return DISTRICT

# Получаем город
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    city = update.message.text
    found_city, result = get_city_id(city)
    if not found_city:
        if result:
            await update.message.reply_text(f"Некорректный ввод. Возможно Вы имели ввиду:\r\n {'\r\n'.join(result)}")
        else:
            await update.message.reply_text(f"Некорректный ввод. Ничего похожего не найдено")
        return CITY
    context.user_data['city'] = result
    await update.message.reply_text(f"Ваш город: {city}. Введите ваш район:")
    return EMPTY  # После района можно завершить или продолжить работу

# Получаем район
async def get_district(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    district = update.message.text
    found_dist, result = get_district_id(district)
    if not found_dist:
        if result:
            await update.message.reply_text(f"Некорректный ввод. Возможно Вы имели ввиду:\r\n{'\r\n'.join(result)}")
        else:
            await update.message.reply_text(f"Некорректный ввод. Ничего похожего не найдено")
        return CITY
    context.user_data['district'] = result

    # Выводим данные в консоль
    region = context.user_data.get('region')
    city = context.user_data.get('city')

    reply_markup = ReplyKeyboardMarkup(
        [[hospital_name[1]] for hospital_name in get_hospital_id(region_id=region, city_id=city, district_id=result)]
    )

    await update.message.reply_text(f"Выбери нужную больницу", reply_markup=reply_markup)
    print(f"Region: {region}, City: {city}, District: {district}")

      # Завершаем диалог
    return HOSPITAL

async def get_hospital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    region = context.user_data.get('region')
    city = context.user_data.get('city')
    district = context.user_data.get('district')

    hospital_id = get_hospital_id(region_id=region, city_id=city, district_id=district, name=update.message.text).id
    telegram_id = update.effective_user.id
    new_user = User(
        telegram_id=telegram_id,
        hospital_id=hospital_id
    )
    add_user_to_db(new_user)
    return ConversationHandler.END

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
            EMPTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_district)],
            HOSPITAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_hospital)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conversation_handler)
    app.run_polling()