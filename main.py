import asyncio
import datetime
import random
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7619709838:AAGZrwZW-RID61ndOS8hcy5gkgFIalJVBg8"
CHAT_ID = -4907114041

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

ADMIN_ID = 1822862999

def is_admin(user_id):
    return user_id == ADMIN_ID

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ У тебя нет прав.")
        return
    
    try:
        chat_id = int(context.args[0])
        message_text = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=chat_id, text=message_text)
        await update.message.reply_text("✅ Сообщение отправлено.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

app.add_handler(CommandHandler("broadcast", broadcast_command))

async def panic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ У тебя нет прав.")
        return
    
    try:
        chat_id = int(context.args[0])
        minutes = get_minutes_left()
        phrase = random.choice(PHRASES).format(minutes=minutes)
        await context.bot.send_message(chat_id=chat_id, text=phrase)
        await update.message.reply_text("✅ Паника отправлена.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

app.add_handler(CommandHandler("panic", panic_command))


def get_minutes_left():
    now = datetime.datetime.now()
    delta = TRIP_TIME - now
    return max(0, int(delta.total_seconds() // 60))

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    minutes = get_minutes_left()
    await update.message.reply_text(f"⏳ Осталось: {minutes} минут до поездки!")

async def countdown_loop(bot: Bot):
    already_announced = False
    while True:
        minutes = get_minutes_left()
        if minutes <= 0:
            if not already_announced:
                await bot.send_message(chat_id=CHAT_ID, text="Поездка уже началась! 🚌💨")
                already_announced = True
        else:
            phrase = random.choice(PHRASES).format(minutes=minutes)
            await bot.send_message(chat_id=CHAT_ID, text=phrase)
        await asyncio.sleep(3600)

async def post_init(app):
    asyncio.create_task(countdown_loop(app.bot))

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("time", time_command))
    print("Бот запущен!")
    app.run_polling()
