import telebot
import psycopg2
import requests
import os
import requests
from io import BytesIO
from telebot import types
import select
import threading
import uuid
from telebot.types import InlineQueryResultArticle, InputTextMessageContent, InputFile
from dotenv import load_dotenv
import os

load_dotenv()



token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)

def get_conn():
    return psycopg2.connect(
        host=os.getenv("HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        port=os.getenv("PORT"),
        password=os.getenv("PASSWORD"),
    )

@bot.message_handler(commands=['start'])
def send_welcome(message):

    welcome_text = (
        "Привіт! Я — бот проєкту <b>AbitHelp</b> 🎓\n\n"
        "Я допоможу тобі відстежувати всі важливі новини з університетів, факультетів та інших ресурсів 📢\n\n"
      "Тримай усе під контролем — жодна подія не пройде повз тебе! 🔍✨\n\n"
       "👉 Напиши <b>/help</b>,або обери опцію з меню нижче щоб переглянути список доступних команд 📋\n"
    )
    main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_menu.row("Підписатися", "Відписатися")
    main_menu.row("Мої підписки", "Допомога")
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu, parse_mode="HTML")


@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "<b> Список команд:</b>\n"
        "/start — перезапуск\n"
        "/help — довідка\n"
        "/follow — підписка на ресурс\n"
        "/unfollow — відписка від ресурсу\n"
        "/myfollows — твої підписки"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="HTML")


@bot.message_handler(commands=['follow'])
def follow(message):
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM events_resource")
            resources = cursor.fetchall()

    if not resources:
        bot.send_message(message.chat.id, "Список ресурсів порожній.")
        return

    res_id, name = resources[0]
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("◀️", callback_data=f"prev_0"),
        types.InlineKeyboardButton("Підписатись", callback_data=f"follow_{res_id}"),
        types.InlineKeyboardButton("▶️", callback_data=f"next_0")
    )
    markup.add(types.InlineKeyboardButton("🔍 Пошук", switch_inline_query_current_chat=""))

    bot.send_message(message.chat.id, f"🔽 Подія: {name}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('next_', 'prev_')))
def navigate_resources(call):
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM events_resource")
            resources = cursor.fetchall()

    total = len(resources)
    current = int(call.data.split('_')[1])
    new_index = (current + 1) % total if call.data.startswith('next_') else (current - 1) % total
    res_id, name = resources[new_index]
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("◀️", callback_data=f"prev_{new_index}"),
        types.InlineKeyboardButton("Підписатись", callback_data=f"follow_{res_id}"),
        types.InlineKeyboardButton("▶️", callback_data=f"next_{new_index}")
    )
    markup.add(types.InlineKeyboardButton("🔍 Пошук", switch_inline_query_current_chat=""))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🔽 Подія: {name}",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('follow_'))
def handle_follow(call):
    resource_id = int(call.data.split('_')[1])
    user_id = call.from_user.id
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM telegram_subscribe WHERE user_id = %s AND resource_id = %s",
                           (user_id, resource_id))
            already_followed = cursor.fetchone()

            if already_followed:
                bot.answer_callback_query(call.id, "Ти вже підписаний на цей ресурс.")
                return

            cursor.execute("INSERT INTO telegram_subscribe (user_id, resource_id) VALUES (%s, %s)",
                           (user_id, resource_id))

            cursor.execute("SELECT name FROM events_resource WHERE id = %s", (resource_id,))
            resource_name_row = cursor.fetchone()
            resource_name = resource_name_row[0] if resource_name_row else "Невідомий ресурс"

    bot.answer_callback_query(call.id, "Підписка оформлена!")
    bot.send_message(call.message.chat.id, "<b>Ти успішно підписався на ресурс!</b>", parse_mode="HTML")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛠 Створити фільтр", callback_data=f"setfilter_{resource_id}"))

    bot.send_message(
        call.message.chat.id,
        f"✅ Ви підписалися на ресурс <b>{resource_name}</b>.\n\n"
        "📌 Тепер ви можете створити фільтр для новин цього ресурсу:\n"
        "— виключити новини, які містять хоча б одне із зазначених слів;\n"
        "— залишити лише новини, що містять кожне слово зі списку.\n\n"
        f"✍️ Натисніть кнопку нижче для налаштування фільтра.",
        parse_mode="HTML",
        reply_markup=markup
    )
@bot.message_handler(commands=['unfollow'])
def unfollow(message):
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT r.id, r.name FROM events_resource r
                JOIN telegram_subscribe ts ON ts.resource_id = r.id
                WHERE ts.user_id = %s
            """, (message.from_user.id,))
            resources = cursor.fetchall()

    if not resources:
        bot.send_message(message.chat.id, "Ти ще не підписаний на жоден ресурс.")
        return

    markup = types.InlineKeyboardMarkup()
    for res_id, name in resources:
        markup.add(types.InlineKeyboardButton(name, callback_data=f"unfollow_{res_id}"))
    bot.send_message(message.chat.id, "Обери ресурс для відписки:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('unfollow_'))
def handle_unfollow(call):
    res_id = int(call.data.split('_')[1])
    user_id = call.from_user.id
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM telegram_subscribe WHERE user_id = %s AND resource_id = %s", (user_id, res_id))
            bot.answer_callback_query(call.id, " Відписка виконана.")
            bot.send_message(call.message.chat.id, "<b>Ти успішно відписався від ресурс!</b>", parse_mode="HTML")

@bot.message_handler(commands=['myfollows'])
def myfollows(message):
    with get_conn() as conn:
        with conn.cursor() as cursor:
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


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def inline_search(query):
    text = query.query.strip().lower()
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, name FROM events_resource
                WHERE LOWER(name) LIKE %s
                LIMIT 10
            """, (f"%{text}%",))
            results = cursor.fetchall()

    articles = []
    for res_id, name in results:
        articles.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=name,
                description="Натисни, щоб підписатися",
                input_message_content=InputTextMessageContent(
                    message_text=f"/subscribe_{res_id}"
                )
            )
        )

    if not articles:
        articles.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="Нічого не знайдено",
                input_message_content=InputTextMessageContent(
                    message_text="Нічого не знайдено за вашим запитом."
                )
            )
        )

    bot.answer_inline_query(query.id, articles, cache_time=1)


@bot.message_handler(regexp=r'^/subscribe_\d+$')
def subscribe_from_inline(message):
    resource_id = int(message.text.split("_")[1])
    user_id = message.from_user.id
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO telegram_subscribe (user_id, resource_id)
                VALUES (%s, %s) ON CONFLICT DO NOTHING
            """, (user_id, resource_id))
    bot.send_message(message.chat.id, "✅ Ви підписалися на ресурс!")




user_filter_states = {}

@bot.callback_query_handler(func=lambda c: c.data.startswith("setfilter_"))
def start_filter_setup(call):
    resource_id = int(call.data.split("_")[1])
    user_id = call.from_user.id
    user_filter_states[user_id] = {
        "resource_id": resource_id,
        "filter_include": None,
        "filter_except": None,
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Пропустити", callback_data="skip_include"))

    bot.send_message(user_id, "Введи слова для ВКЛЮЧЕННЯ у фільтр через пробіл.\nАбо натисни кнопку 'Пропустити'.", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda c: c.data == "skip_include")
def skip_include_handler(call):
    user_id = call.from_user.id
    if user_id in user_filter_states:
        user_filter_states[user_id]["filter_include"] = []
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Пропустити", callback_data="skip_except"))
        bot.send_message(user_id, "Введи слова для ВИКЛЮЧЕННЯ у фільтр через пробіл.\nАбо натисни кнопку 'Пропустити'.", reply_markup=markup)
        bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.from_user.id in user_filter_states and user_filter_states[m.from_user.id]["filter_include"] is None)
def receive_include_words(message):
    user_id = message.from_user.id
    words = message.text.strip()
    if words.lower() == "пропустити":
        user_filter_states[user_id]["filter_include"] = []
    else:
        user_filter_states[user_id]["filter_include"] = words.split()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Пропустити", callback_data="skip_except"))
    bot.send_message(user_id, "Введи слова для ВИКЛЮЧЕННЯ у фільтр через пробіл.\nАбо натисни кнопку 'Пропустити'.", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: c.data == "skip_except")
def skip_except_handler(call):
    user_id = call.from_user.id
    if user_id in user_filter_states:
        user_filter_states[user_id]["filter_except"] = []
        save_filters(user_id)
        bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.from_user.id in user_filter_states and user_filter_states[m.from_user.id]["filter_include"] is not None and user_filter_states[m.from_user.id]["filter_except"] is None)
def receive_except_words(message):
    user_id = message.from_user.id
    words = message.text.strip()
    if words.lower() == "пропустити":
        user_filter_states[user_id]["filter_except"] = []
    else:
        user_filter_states[user_id]["filter_except"] = words.split()

    save_filters(user_id)

def save_filters(user_id):
    state = user_filter_states[user_id]
    resource_id = state["resource_id"]
    filter_include = state["filter_include"]
    filter_except = state["filter_except"]

    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE telegram_subscribe
                SET filter_include = %s, filter_except = %s
                WHERE user_id = %s AND resource_id = %s
            """, (filter_include, filter_except, user_id, resource_id))
        conn.commit()

    bot.send_message(
        user_id,
        f"Фільтр збережено\n\nВключені слова: {', '.join(filter_include) if filter_include else 'немає'}\n"
        f"Виключені слова: {', '.join(filter_except) if filter_except else 'немає'}"
    )

    user_filter_states.pop(user_id)
@bot.message_handler(func=lambda message: message.text == "Підписатися")
def handle_follow_text(message):
    follow(message)

@bot.message_handler(func=lambda message: message.text == "Відписатися")
def handle_unfollow_text(message):
    unfollow(message)

@bot.message_handler(func=lambda message: message.text == "Мої підписки")
def handle_myfollows_text(message):
    myfollows(message)

@bot.message_handler(func=lambda message: message.text == "Допомога")
def handle_help_text(message):
    send_help(message)


def send_event_to_subscribers(event_id):
    with get_conn() as conn:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT title, content, source_id, date, post_link FROM events_event WHERE id = %s
            """, (event_id,))
            event = cursor.fetchone()

            if not event:
                print(f"Подія з ID {event_id} не знайдена.")
                return

            title, content, source_id, date, post_link = event

            cursor.execute("""
                SELECT image FROM events_eventimage WHERE event_id = %s
            """, (event_id,))
            images = cursor.fetchall()

            images_data = []
            for img in images:
                url = f'http://localhost:8000/media/{img[0].lstrip("/")}'
                response = requests.get(url)
                if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('image/'):
                    images_data.append(response)
                else:
                    print(f"❌ Не вдалося завантажити зображення за URL: {url}")

            cursor.execute("""
                SELECT user_id FROM telegram_subscribe WHERE resource_id = %s
            """, (source_id,))
            subscribers = cursor.fetchall()

    if not subscribers:
        print(f"ℹ️ Немає підписників для ресурсу {source_id}.")
        return

    event_text = (
        f"<b>{title}</b>\n\n"
        f"Опис:\n{content}\n\n"
        f"Дата: <i>{date.strftime('%d.%m.%Y %H:%M')}</i>"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Переглянути ресурси", url=post_link))

    for (user_id,) in subscribers:
        try:
            bot.send_message(
                user_id,
                event_text,
                parse_mode="HTML",
                reply_markup=markup
            )

            for img_response in images_data:
                photo_bytes = BytesIO(img_response.content)
                photo_bytes.name = "photo.jpg"
                photo_bytes.seek(0)
                photo = InputFile(photo_bytes, file_name="photo.jpg")
                bot.send_photo(user_id, photo)

        except Exception as e:
            print(f"❌ Не вдалося надіслати повідомлення користувачу {user_id}: {e}")

def listen():
    def inner():
        conn = get_conn()
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        try:
            cursor.execute("LISTEN events_channel;")
            print("Слухаємо events_channel...")

            while True:
                if select.select([conn], [], [], 5) == ([], [], []):
                    continue
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    print(f"Отримано NOTIFY з payload: {notify.payload}")
                    try:
                        event_id = int(notify.payload)
                        send_event_to_subscribers(event_id)
                    except ValueError:
                        print("Невірний payload.")
        except Exception as e:
            print(f"Помилка у слухачі: {e}")
        finally:
            cursor.close()
            conn.close()
    thread = threading.Thread(target=inner, daemon=True)
    thread.start()

listen()

bot.infinity_polling()