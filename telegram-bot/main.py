import telebot
import psycopg2
from telebot import types
import time
import threading
from dotenv import load_dotenv
import os

load_dotenv()



token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)

conn = psycopg2.connect(
    host=os.getenv("HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    port=os.getenv("PORT"),
    password=os.getenv("PASSWORD"),
)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
         "<b>🎓 Вітаємо тебе в офіційному боті університетських подій!</b>\n\n"
        "Тут ти зможеш:\n"
        "📢 Отримувати важливі сповіщення\n"
        "🎉 Дізнаватися про заходи та активності\n"
        "📚 Слідкувати за новинами факультетів\n\n"
        "Обери дію з меню нижче або введи команду:"
    )
    main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu.row(" Підписатися", " Відписатися")
    main_menu.row(" Мої підписки", "ℹ️ Допомога")
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu, parse_mode="HTML")


@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "<b>ℹ️ Доступні команди:</b>\n\n"
        "🔄 /start — Перезапустити бота\n"
        "❓ /help — Отримати довідку\n"
        "➕ /follow — Підписатися на ресурс\n"
        "➖ /unfollow — Відписатися від ресурсу\n"
        "📋 /myfollows — Переглянути свої підписки"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="HTML")


@bot.message_handler(commands=['follow'])
def follow(message):
    cursor.execute("SELECT id, name FROM events_resource")
    resources = cursor.fetchall()
    if not resources:
        bot.send_message(message.chat.id, "😔 Наразі немає доступних ресурсів для підписки.")
        return

    res_id, name = resources[0]
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("◀️", callback_data=f"prev_0"),
        types.InlineKeyboardButton("✅ Підписатися", callback_data=f"follow_{res_id}"),
        types.InlineKeyboardButton("▶️", callback_data=f"next_0")
    )
    bot.send_message(message.chat.id, f"🎓 <b>Ресурс:</b> {name}", reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith(('next_', 'prev_')))
def navigate_resources(call):
    cursor.execute("SELECT id, name FROM events_resource")
    resources = cursor.fetchall()
    total = len(resources)
    current = int(call.data.split('_')[1])
    new_index = (current + 1) % total if call.data.startswith('next_') else (current - 1) % total
    res_id, name = resources[new_index]
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("◀️", callback_data=f"prev_{new_index}"),
        types.InlineKeyboardButton("✅ Підписатися", callback_data=f"follow_{res_id}"),
        types.InlineKeyboardButton("▶️", callback_data=f"next_{new_index}")
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🎓Ресурс: {name}",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('follow_'))
def handle_follow(call):
    resource_id = int(call.data.split('_')[1])
    user_id = call.from_user.id

    cursor.execute("SELECT 1 FROM telegram_subscribe WHERE user_id = %s AND resource_id = %s", (user_id, resource_id))
    already_followed = cursor.fetchone()

    if already_followed:
        bot.answer_callback_query(call.id, " Ти вже підписаний на цей ресурс")
        return

    cursor.execute("INSERT INTO telegram_subscribe (user_id, resource_id) VALUES (%s, %s)", (user_id, resource_id))
    conn.commit()

    bot.answer_callback_query(call.id, " Підписка оформлена")
    bot.send_message(call.message.chat.id, "<b> Ти успішно підписався на ресурс</b>", parse_mode="HTML")


@bot.message_handler(commands=['unfollow'])
def unfollow(message):
    cursor.execute("""
        SELECT r.id, r.name FROM events_resource r
        JOIN telegram_subscribe ts ON ts.resource_id = r.id
        WHERE ts.user_id = %s
    """, (message.from_user.id,))
    resources = cursor.fetchall()

    if not resources:
        bot.send_message(message.chat.id, "Ти ще не підписаний на жоден ресурс")
        return

    markup = types.InlineKeyboardMarkup()
    for res_id, name in resources:
        markup.add(types.InlineKeyboardButton(name, callback_data=f"unfollow_{res_id}"))
    bot.send_message(message.chat.id, "Обери ресурс для відписки:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('unfollow_'))
def handle_unfollow(call):
    res_id = int(call.data.split('_')[1])
    user_id = call.from_user.id
    cursor.execute("DELETE FROM telegram_subscribe WHERE user_id = %s AND resource_id = %s", (user_id, res_id))
    conn.commit()

    bot.answer_callback_query(call.id, " Відписка виконана.")
    bot.send_message(call.message.chat.id, "<b>Ти успішно відписався від ресурсу</b>", parse_mode="HTML")

@bot.message_handler(commands=['myfollows'])
def myfollows(message):
    cursor.execute("""
        SELECT r.name FROM events_resource r
        JOIN telegram_subscribe ts ON ts.resource_id = r.id
        WHERE ts.user_id = %s
    """, (message.from_user.id,))
    resources = cursor.fetchall()

    if resources:
        text = "<b> Твої підписки:</b>\n" + "\n".join(f"🔹 {r[0]}" for r in resources)
    else:
        text = "<b>️ Ти ще не підписаний на жоден ресурс.</b>"
    bot.send_message(message.chat.id, text, parse_mode="HTML")


def send_event(event_id):
    cursor.execute("SELECT title, content, source_id, date, post_link FROM events_event WHERE id = %s", (event_id,))
    event = cursor.fetchone()

    if not event:
        print(f" Подія з ID {event_id} не знайдена.")
        return

    title, content, source_id, date, post_link = event

    event_text = (
        f"🎓 <b>{title}</b>\n\n"
        f"📝 <b>Опис:</b>\n{content}\n\n"
        f"📅 <b>Дата:</b> <i>{date.strftime('%d.%m.%Y %H:%M')}</i>"
    )

    cursor.execute("SELECT user_id FROM telegram_subscribe WHERE resource_id = %s", (source_id,))
    subscribers = cursor.fetchall()

    if not subscribers:
        print(f"ℹ Немає підписників для ресурсу {source_id}.")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(" Переглянути детальніше", url=post_link))

    for subscriber in subscribers:
        user_id = subscriber[0]
        try:
            bot.send_message(user_id, event_text, parse_mode="HTML", reply_markup=markup)
        except Exception as e:
            print(f" Не вдалося надіслати повідомлення користувачу {user_id}: {e}")


def listen():
    cursor.execute("LISTEN events_channel;")
    print("слухає канал 'events_channel'...")
    while True:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            print(f"Прийшло повідомлення: {notify.payload}")
            try:
                event_id = int(notify.payload)
                send_event(event_id)
            except ValueError:
                print(" Помилка: невірний payload в NOTIFY.")
        time.sleep(5)

listener_thread = threading.Thread(target=listen, daemon=True)
listener_thread.start()

@bot.message_handler(func=lambda message: message.text == "Підписатися")
def handle_follow_text(message):
    follow(message)

@bot.message_handler(func=lambda message: message.text == "Відписатися")
def handle_unfollow_text(message):
    unfollow(message)

@bot.message_handler(func=lambda message: message.text == "Мої підписки")
def handle_myfollows_text(message):
    myfollows(message)

@bot.message_handler(func=lambda message: message.text == "ℹ️ Допомога")
def handle_help_text(message):
    send_help(message)

bot.infinity_polling()