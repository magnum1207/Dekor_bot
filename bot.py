import os 
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 6144650191  # <-- ЗАМЕНИ НА СВОЙ ЦИФРОВОЙ ID (узнать в @userinfobot)
MANAGER_PHONE = "+7 (928) 517-95-91"
MANAGER_USERNAME = "h44012"  # <-- Впиши свой юзернейм без @ (например, ivan_decor)

bot = telebot.TeleBot(TOKEN)

# Временное хранилище, чтобы бот помнил, какую фотозону выбрал клиент перед отправкой номера
user_orders = {}

# Список из 7 свадебных фотозон по 19 000 руб.
PHOTOZONES = [
    {"name": "Свадебная фотозона №1", "photo": "images/1.jpg", "price": "19 000 руб."},
    {"name": "Свадебная фотозона №2", "photo": "images/2.jpg", "price": "19 000 руб."},
    {"name": "Свадебная фотозона №3", "photo": "images/3.jpg", "price": "19 000 руб."},
    {"name": "Свадебная фотозона №4", "photo": "images/4.jpg", "price": "19 000 руб."},
    {"name": "Свадебная фотозона №5", "photo": "images/5.jpg", "price": "19 000 руб."},
    {"name": "Свадебная фотозона №6", "photo": "images/6.jpg", "price": "19 000 руб."},
    {"name": "Свадебная фотозона №7", "photo": "images/7.jpg", "price": "19 000 руб."},
]

# Главное меню (кнопки внизу экрана)
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("💍 Смотреть фотозоны (7 шт.)"))
    markup.add(types.KeyboardButton("📞 Связаться с менеджером"))
    return markup

# Клавиатура под фотографией (листалка + кнопка заказа)
def get_zone_keyboard(index):
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    prev_index = (index - 1) % len(PHOTOZONES)
    next_index = (index + 1) % len(PHOTOZONES)
    
    btn_prev = types.InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{prev_index}")
    btn_next = types.InlineKeyboardButton("Вперёд ➡️", callback_data=f"page_{next_index}")
    btn_order = types.InlineKeyboardButton("✅ Заказать эту фотозону", callback_data=f"order_{index}")
    
    markup.add(btn_prev, btn_next)
    markup.add(btn_order)
    return markup

# Текст под фото
def get_zone_caption(index):
    zone = PHOTOZONES[index]
    return (
        f"💍 **{zone['name']}** ({index + 1} из {len(PHOTOZONES)})\n\n"
        f"✨ Идеально для вашей свадьбы!\n"
        f"💰 **Цена:** {zone['price']}"
    )

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Нажми на кнопку ниже, чтобы посмотреть каталог свадебных фотозон и цены 👇",
        reply_markup=main_menu()
    )

# Обработка главного меню
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "💍 Смотреть фотозоны (7 шт.)":
        first_zone = PHOTOZONES[0]
        with open(first_zone["photo"], 'rb') as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=get_zone_caption(0),
                parse_mode="Markdown",
                reply_markup=get_zone_keyboard(0)
            )
            
    elif message.text == "📞 Связаться с менеджером":
        inline_markup = types.InlineKeyboardMarkup()
        btn_chat = types.InlineKeyboardButton("💬 Написать в Telegram", url=f"https://t.me{MANAGER_USERNAME}")
        inline_markup.add(btn_chat)
        
        bot.send_message(
            message.chat.id,
            f"📞 **Телефон для связи / WhatsApp:**\n`{MANAGER_PHONE}`\n\nИли напишите нам напрямую в Telegram по кнопке ниже 👇",
            parse_mode="Markdown",
            reply_markup=inline_markup
        )

    elif message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "Заказ отменён. Выбирайте другую фотозону 👇", reply_markup=main_menu())

# Перелистывание фотозон
@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def handle_pagination(call):
    parts = call.data.split("_")
    index = int(parts[1])
    zone = PHOTOZONES[index]
    
    with open(zone["photo"], 'rb') as photo:
        media = types.InputMediaPhoto(
            media=photo,
            caption=get_zone_caption(index),
            parse_mode="Markdown"
        )
        bot.edit_message_media(
            media=media,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_zone_keyboard(index)
        )
    bot.answer_callback_query(call.id)

# Шаг 1 при заказе: запоминаем фотозону и просим номер телефона
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def handle_order(call):
    parts = call.data.split("_")
    index = int(parts[1])
    zone = PHOTOZONES[index]
    
    # Запоминаем выбор клиента
    user_orders[call.from_user.id] = zone
    
    # Создаём кнопку отправки контакта
    phone_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_phone = types.KeyboardButton("📱 Отправить мой номер телефона", request_contact=True)
    btn_cancel = types.KeyboardButton("❌ Отмена")
    phone_markup.add(btn_phone)
    phone_markup.add(btn_cancel)
    
    bot.send_message(
        call.message.chat.id,
        f"Вы выбрали **{zone['name']}** ({zone['price']}).\n\n"
        f"Нажмите кнопку **«📱 Отправить мой номер телефона»** ниже, чтобы менеджер мог связаться с вами 👇",
        parse_mode="Markdown",
        reply_markup=phone_markup
    )
    bot.answer_callback_query(call.id)

# Шаг 2 при заказе: получаем номер клиента и шлём всё тебе в личку
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user = message.from_user
    phone = message.contact.phone_number
    zone = user_orders.get(user.id, {"name": "Не указана", "price": "19 000 руб."})
    
    username = f"@{user.username}" if user.username else "нет юзернейма"
    
    # Сообщение ТЕБЕ в личку
    admin_text = (
        f"🔥 **НОВЫЙ ЗАКАЗ СВАДЕБНОЙ ФОТОЗОНЫ!**\n\n"
        f"📍 **Фотозона:** {zone['name']}\n"
        f"💰 **Цена:** {zone['price']}\n"
        f"👤 **Имя:** {user.first_name} ({username})\n"
        f"📞 **Телефон:** `+{phone.lstrip('+')}`"
    )
    bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    
    # Ответ клиенту и возврат обычного меню
    bot.send_message(
        message.chat.id,
        f"✅ Спасибо! Ваша заявка на **{zone['name']}** принята.\n"
        f"Мы свяжемся с вами по номеру `+{phone.lstrip('+')}` в ближайшее время!",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

print("Свадебный бот (7 фотозон + приём телефонов) запущен...")
bot.infinity_polling()
