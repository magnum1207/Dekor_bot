import telebot
from telebot import types

TOKEN = '9069100903:AAFj7v5NXjihEzyeDihG4iuphsEwg2bVUVg'
ADMIN_ID = 6144650191  # <-- ЗАМЕНИ НА СВОЙ ЦИФРОВОЙ ID (узнать в @userinfobot)
MANAGER_PHONE = "+7 (928) 517-95-91"
MANAGER_USERNAME = "h44012"  # <-- Впиши свой юзернейм без @

bot = telebot.TeleBot(TOKEN)
user_orders = {}

# База всех 5 категорий с актуальными ценами и точным количеством фоток
CATALOG = {
    "wedding": {
        "btn_name": "💍 Свадьба — Сватовство",
        "title": "Свадьба — Сватовство",
        "items": [
            {"photo": "images/wedding/1.JPG", "price": "19 000 руб."},
            {"photo": "images/wedding/2.JPG", "price": "19 000 руб."},
            {"photo": "images/wedding/3.JPG", "price": "19 000 руб."},
            {"photo": "images/wedding/4.JPG", "price": "19 000 руб."},
            {"photo": "images/wedding/5.JPG", "price": "19 000 руб."},
            {"photo": "images/wedding/6.JPG", "price": "19 000 руб."},
            {"photo": "images/wedding/7.JPG", "price": "19 000 руб."},
        ]
    },
    "birthday": {
        "btn_name": "🎂 День рождения",
        "title": "Фотозона на День рождения",
        "items": [
            {"photo": "images/birthday/1.JPG", "price": "5 000 руб."},
            {"photo": "images/birthday/2.JPG", "price": "5 000 руб."},
            {"photo": "images/birthday/3.JPG", "price": "5 000 руб."},
            {"photo": "images/birthday/4.JPG", "price": "5 000 руб."},
        ]
    },
    "grad_kindergarten": {
        "btn_name": "🧸 Выпускной (дет. сад)",
        "title": "Выпускной (детский сад)",
        "items": [
            {"photo": "images/grad_kindergarten/1.JPG", "price": "10 000 – 15 000 руб."},
            {"photo": "images/grad_kindergarten/2.JPG", "price": "10 000 – 15 000 руб."},
            {"photo": "images/grad_kindergarten/3.JPG", "price": "10 000 – 15 000 руб."},
        ]
    },
    "grad_school": {
        "btn_name": "🎓 Выпускной (школа)",
        "title": "Выпускной (школа)",
        "items": [
            {"photo": "images/grad_school/1.JPG", "price": "10 000 – 15 000 руб."},
            {"photo": "images/grad_school/2.JPG", "price": "10 000 – 15 000 руб."},
            {"photo": "images/grad_school/3.JPG", "price": "10 000 – 15 000 руб."},
        ]
    },
    "baby": {
        "btn_name": "👶 Рождение ребёнка",
        "title": "Фотозона на Рождение ребёнка",
        "items": [
            {"photo": "images/baby/1.JPG", "price": "5 500 руб."},
            {"photo": "images/baby/2.JPG", "price": "5 500 руб."},
        ]
    }
}

# Главное меню с 5 вкладками + кнопка связи
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("💍 Свадьба — Сватовство"),
        types.KeyboardButton("🎂 День рождения"),
        types.KeyboardButton("🧸 Выпускной (дет. сад)"),
        types.KeyboardButton("🎓 Выпускной (школа)"),
        types.KeyboardButton("👶 Рождение ребёнка"),
        types.KeyboardButton("📞 Связаться с менеджером")
    )
    return markup

# Кнопки под фото (листалка внутри выбранной категории + заказ)
def get_zone_keyboard(cat_key, index):
    items = CATALOG[cat_key]["items"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    prev_index = (index - 1) % len(items)
    next_index = (index + 1) % len(items)
    
    btn_prev = types.InlineKeyboardButton("⬅️ Назад", callback_data=f"page|{cat_key}|{prev_index}")
    btn_next = types.InlineKeyboardButton("Вперёд ➡️", callback_data=f"page|{cat_key}|{next_index}")
    btn_order = types.InlineKeyboardButton("✅ Заказать эту фотозону", callback_data=f"order|{cat_key}|{index}")
    
    markup.add(btn_prev, btn_next)
    markup.add(btn_order)
    return markup

# Подпись под фото
def get_zone_caption(cat_key, index):
    category = CATALOG[cat_key]
    items = category["items"]
    item = items[index]
    return (
        f"✨ **{category['title']} №{index + 1}** ({index + 1} из {len(items)})\n\n"
        f"💰 **Цена:** {item['price']}"
    )

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Выбери повод в меню ниже, чтобы посмотреть варианты фотозон и цены 👇",
        reply_markup=main_menu()
    )

# Обработка нажатий на вкладки и кнопку менеджера
@bot.message_handler(content_types=['text'])
def handle_text(message):
    for cat_key, cat_data in CATALOG.items():
        if message.text == cat_data["btn_name"]:
            first_item = next(iter(cat_data["items"]))
            with open(first_item["photo"], 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=get_zone_caption(cat_key, 0),
                    parse_mode="Markdown",
                    reply_markup=get_zone_keyboard(cat_key, 0)
                )
            return

    if message.text == "📞 Связаться с менеджером":
        inline_markup = types.InlineKeyboardMarkup()
        btn_chat = types.InlineKeyboardButton("💬 Написать в Telegram", url=f"https://t.me/{MANAGER_USERNAME}")
        inline_markup.add(btn_chat)
        
        bot.send_message(
            message.chat.id,
            f"📞 **Телефон для связи / WhatsApp:**\n`{MANAGER_PHONE}`\n\nИли напишите нам напрямую в Telegram по кнопке ниже 👇",
            parse_mode="Markdown",
            reply_markup=inline_markup
        )

    elif message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "Заказ отменён. Выбирайте другую фотозону 👇", reply_markup=main_menu())

# Перелистывание внутри выбранной категории
@bot.callback_query_handler(func=lambda call: call.data.startswith("page|"))
def handle_pagination(call):
    _, cat_key, index_str = call.data.split("|")
    index = int(index_str)
    item = CATALOG[cat_key]["items"][index]
    
    with open(item["photo"], 'rb') as photo:
        media = types.InputMediaPhoto(
            media=photo,
            caption=get_zone_caption(cat_key, index),
            parse_mode="Markdown"
        )
        bot.edit_message_media(
            media=media,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=get_zone_keyboard(cat_key, index)
        )
    bot.answer_callback_query(call.id)

# Запрос номера телефона при заказе
@bot.callback_query_handler(func=lambda call: call.data.startswith("order|"))
def handle_order(call):
    _, cat_key, index_str = call.data.split("|")
    index = int(index_str)
    category = CATALOG[cat_key]
    item = category["items"][index]
    
    user_orders[call.from_user.id] = {
        "name": f"{category['title']} №{index + 1}",
        "price": item["price"]
    }
    
    phone_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    phone_markup.add(types.KeyboardButton("📱 Отправить мой номер телефона", request_contact=True))
    phone_markup.add(types.KeyboardButton("❌ Отмена"))
    
    bot.send_message(
        call.message.chat.id,
        f"Вы выбрали: **{category['title']} №{index + 1}** ({item['price']}).\n\n"
        f"Нажмите кнопку **«📱 Отправить мой номер телефона»** ниже, чтобы менеджер связался с вами 👇",
        parse_mode="Markdown",
        reply_markup=phone_markup
    )
    bot.answer_callback_query(call.id)

# Отправка готовой заявки в личку админу
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user = message.from_user
    phone = message.contact.phone_number
    order = user_orders.get(user.id, {"name": "Не указана", "price": "—"})
    username = f"@{user.username}" if user.username else "нет юзернейма"
    
    admin_text = (
        f"🔥 **НОВЫЙ ЗАКАЗ ФОТОЗОНЫ!**\n\n"
        f"📍 **Вариант:** {order['name']}\n"
        f"💰 **Цена:** {order['price']}\n"
        f"👤 **Клиент:** {user.first_name} ({username})\n"
        f"📞 **Телефон:** `+{phone.lstrip('+')}`"
    )
    bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    
    bot.send_message(
        message.chat.id,
        f"✅ Спасибо! Заявка на **{order['name']}** принята.\n"
        f"Мы свяжемся с вами по номеру `+{phone.lstrip('+')}` в ближайшее время!",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

print("Бот на 5 категорий запущен...")
bot.infinity_polling()
