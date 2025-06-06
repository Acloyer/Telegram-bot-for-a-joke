import asyncio
import datetime
import random
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = "7619709838:AAGZrwZW-RID61ndOS8hcy5gkgFIalJVBg8"
CHAT_ID = -4907114041
ADMIN_ID = 1822862999

TRIP_TIME = datetime.datetime(2025, 6, 8, 8, 40)

PHRASES = [
    "Чемоданы собраны? Осталось всего {minutes} минут!",
    "Скоро вылет в Сумгаит! {minutes} минут до старта. 🚌",
    "Тик-так... осталось {minutes} минут! Время летит!",
    "Проверь носки и документы: {minutes} минут до Сумгаита!",
    "Ты уже пахнешь Сумгаитом... {minutes} минут осталось!",
    "Если ты не готов - это твои проблемы. {minutes} минут!",
    "Все уже сбрили себе письки? Потому что осталось всего {minutes} до того как все встретятся!",
    "Чувствуете этот вайб?... Это же тот самый вайб когда осталось {minutes} до Сумгаита!",
    "Каждая минута приближает тебя к великому приключению. Осталось {minutes}!",
]

is_muted = False
next_send_time: datetime.datetime = None
counters = {
    "messages_sent": 0,
    "broadcast_count": 0,
    "panic_count": 0,
    "time_requests": 0,
}

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def get_delta() -> datetime.timedelta:
    now = datetime.datetime.now()
    return max(TRIP_TIME - now, datetime.timedelta(0))

def get_minutes_left() -> int:
    return int(get_delta().total_seconds() // 60)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = "Привет! Доступные команды:\n"
    text += "/time — узнать остаток времени до поездки\n"
    text += "/next — когда будет следующее автосообщение\n"
    text += "/mute — выключить автосообщения\n"
    text += "/unmute — включить автосообщения\n"
    if is_admin(user.id):
        text += "\nАдмин-команды:\n"
        text += "/broadcast <chat_id> <msg> — отправить в группу любой текст\n"
        text += "/panic <chat_id> — отправить рофлофразу сейчас\n"
        text += "/stats — показать статистику\n"
    await update.message.reply_text(text)

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    counters["time_requests"] += 1
    minutes = get_minutes_left()
    # build inline buttons
    kb = [
        [InlineKeyboardButton("Минуты", callback_data="fmt_minutes"),
         InlineKeyboardButton("Часы", callback_data="fmt_hours")],
        [InlineKeyboardButton("Секунды", callback_data="fmt_seconds"),
         InlineKeyboardButton("Обновить", callback_data="fmt_refresh")],
        [InlineKeyboardButton("Next", callback_data="next")]
    ]
    markup = InlineKeyboardMarkup(kb)
    await update.message.reply_text(f"⏳ Осталось: {minutes} минут до поездки!", reply_markup=markup)

async def next_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if next_send_time:
        delta = next_send_time - datetime.datetime.now()
        mins = int(delta.total_seconds() // 60)
        secs = int(delta.total_seconds() % 60)
        await update.message.reply_text(f"📡 Следующее автосообщение через {mins} мин {secs} сек")
    else:
        await update.message.reply_text("🕑 Расписание автосообщений ещё не установлено.")

async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_muted
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ У тебя нет прав.")
    is_muted = True
    await update.message.reply_text("🔕 Автосообщения отключены.")

async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_muted
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ У тебя нет прав.")
    is_muted = False
    await update.message.reply_text("🔔 Автосообщения включены.")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ У тебя нет прав.")
    try:
        chat_id = int(context.args[0])
        text = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=chat_id, text=text)
        counters["broadcast_count"] += 1
        await update.message.reply_text("✅ Сообщение отправлено.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def panic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ У тебя нет прав.")
    try:
        chat_id = int(context.args[0])
        mins = get_minutes_left()
        phrase = random.choice(PHRASES).format(minutes=mins)
        await context.bot.send_message(chat_id=chat_id, text=phrase)
        counters["panic_count"] += 1
        await update.message.reply_text("✅ Паника отправлена.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ У тебя нет прав.")
    text = (
        f"📊 Статистика:\n"
        f"Сообщений отправлено (авто): {counters['messages_sent']}\n"
        f"Broadcast: {counters['broadcast_count']}\n"
        f"Panic: {counters['panic_count']}\n"
        f"Time-запросов: {counters['time_requests']}\n"
        f"Muted: {'Да' if is_muted else 'Нет'}"
    )
    await update.message.reply_text(text)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()
    if data.startswith("fmt_"):
        fmt = data.split("_")[1]
        delta = get_delta()
        if fmt == "minutes":
            out = f"⏳ Осталось: {int(delta.total_seconds()//60)} минут"
        elif fmt == "hours":
            hrs = int(delta.total_seconds()//3600)
            mins = int((delta.total_seconds()%3600)//60)
            out = f"⏲ Осталось: {hrs} ч {mins} мин"
        elif fmt == "seconds":
            secs = int(delta.total_seconds())
            out = f"⏱ Осталось: {secs} секунд"
        elif fmt == "refresh":
            out = f"🔄 Обновлено: {int(delta.total_seconds()//60)} мин"
        await query.edit_message_text(out, reply_markup=query.message.reply_markup)
    elif data == "next":
        # имитируем вызов /next
        await next_command(update, context)

async def countdown_loop(bot: Bot):
    global next_send_time, counters
    while True:
        delta = get_delta()
        mins = int(delta.total_seconds()//60)
        if mins <= 0:
            await bot.send_message(chat_id=CHAT_ID, text="Поездка уже началась! 🚌💨")
        else:
            if not is_muted:
                phrase = random.choice(PHRASES).format(minutes=mins)
                await bot.send_message(chat_id=CHAT_ID, text=phrase)
                counters["messages_sent"] += 1
        next_send_time = datetime.datetime.now() + datetime.timedelta(seconds=3600)
        await asyncio.sleep(3600)

async def post_init(app):
    asyncio.create_task(countdown_loop(app.bot))

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    # Команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("next", next_command))
    app.add_handler(CommandHandler("mute", mute_command))
    app.add_handler(CommandHandler("unmute", unmute_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("panic", panic_command))
    app.add_handler(CommandHandler("stats", stats_command))
    # Callback для кнопок
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("Бот запущен!")
    app.run_polling()