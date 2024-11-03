import os
from dotenv import load_dotenv
from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters, CallbackQueryHandler

from models.city_model import get_city_id
from models.district_model import get_district_id
from models.hospital_model import get_hospital_id
from models.user_model import User, add_user_to_db, get_hospital_link, get_hospital_data

from db.parser import get_lights

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
    await query.message.reply_text("Введите ваш город:")
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
    city = context.user_data.get('city')

    reply_markup = ReplyKeyboardMarkup(
        [[hospital_name[1]] for hospital_name in get_hospital_id(city_id=city, district_id=result)]
    )

    await update.message.reply_text(f"Выбери нужную больницу", reply_markup=reply_markup)
    print(f"City: {city}, District: {district}")

      # Завершаем диалог
    return HOSPITAL

async def get_hospital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    region = context.user_data.get('region')
    city = context.user_data.get('city')
    district = context.user_data.get('district')

    hospital_id = get_hospital_id(city_id=city, district_id=district, name=update.message.text).id
    telegram_id = update.effective_user.id
    new_user = User(
        telegram_id=telegram_id,
        hospital_id=hospital_id
    )
    add_user_to_db(new_user)
    await update.message.reply_text(generate_reply(telegram_id), reply_markup=None)
    return ConversationHandler.END

def generate_reply(tg_id):
    url = get_hospital_link(tg_id)
    lights = get_lights(url)
    hospital_data = get_hospital_data(tg_id)

    lights_text = ""
    lights_text += f"❗️0 (I):\n\t❕Rh+: {lights['0 (I)']['Rh+']} - {about_text(lights['0 (I)']['Rh+'])}"
    lights_text += f"\n\t❕Rh-: {lights['0 (I)']['Rh-']} - {about_text(lights['0 (I)']['Rh-'])}\n"
    lights_text += f"❗️A (II):\n\t❕Rh+: {lights['A (II)']['Rh+']} - {about_text(lights['A (II)']['Rh+'])}"
    lights_text += f"\n\t❕Rh-: {lights['A (II)']['Rh-']} - {about_text(lights['A (II)']['Rh-'])}\n"
    lights_text += f"❗️B (III):\n\t❕Rh+: {lights['B (III)']['Rh+']} - {about_text(lights['B (III)']['Rh+'])}"
    lights_text += f"\n\t❕Rh-: {lights['B (III)']['Rh-']} - {about_text(lights['B (III)']['Rh-'])}\n"
    lights_text += f"❗️AB (IV):\n\t❕Rh+: {lights['AB (IV)']['Rh+']} - {about_text(lights['AB (IV)']['Rh+'])}"
    lights_text += f"\n\t❕Rh-: {lights['AB (IV)']['Rh-']} - {about_text(lights['AB (IV)']['Rh-'])}\n"

    reply_text = f"""🏥 Ваша больница:
{hospital_data['name']}
📍 Находится по адресу: {hospital_data['address']}
🚦Ваш светофор:
{lights_text}
"""
    return reply_text

def about_text(data):
    if '🟢' in data:
        return 'достаточный запас крови. С визитом в Службу крови можно повременить.'
    elif '🟡' in data:
        return 'присутствует потребность, рекомендуем запланировать визит для плановой донации.'
    elif '🔴' in data:
        return 'повышенная потребность, рекомендуем запланировать визит для плановой донации.'
    elif '⚪️' in data:
        return 'не имеет экстренных потребностей ввиду заготовки исключительно донорской плазмы'
    else:
        return 'донорский светофор не обновлялся более 3-х недель.'

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
            DISTRICT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            EMPTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_district)],
            HOSPITAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_hospital)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conversation_handler)
    app.run_polling()