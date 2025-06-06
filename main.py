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
