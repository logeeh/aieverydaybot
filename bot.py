import logging
import os
from dotenv import load_dotenv
import openai
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# === Загрузка переменных из .env ===
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

openai.api_key = OPENAI_API_KEY

# === Логгирование ===
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# === Генерация поста через GPT ===
async def generate_post() -> str:
    prompt = "Сделай короткий, живой пост для Telegram-канала про ИИ. Стиль — простой, разговорный, без шаблонов."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты Telegram-копирайтер"},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("Сделать пост", callback_data="make_post")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Нажми кнопку, чтобы сгенерировать пост:", reply_markup=reply_markup)

# === Обработка кнопок ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "make_post":
        await query.edit_message_text("Генерирую пост, подожди секунду...")
        post_text = await generate_post()

        keyboard = [[InlineKeyboardButton("Опубликовать сейчас", callback_data=f"post_now|{post_text}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.reply_text(post_text, reply_markup=reply_markup)

    elif query.data.startswith("post_now"):
        post_text = query.data.split("|", 1)[1]
        await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=post_text)
        await query.edit_message_text("Пост опубликован в канал!")

# === Основной запуск ===
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.run_polling()

if __name__ == "__main__":
    main()
