import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"


# Render uchun kichik web-server
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


port = int(os.environ.get("PORT", 10000))
server = HTTPServer(("0.0.0.0", port), HealthHandler)
threading.Thread(target=server.serve_forever, daemon=True).start()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇺🇿 Assalomu alaykum!\n\n"
        "💱 UZ Currency botiga xush kelibsiz!"
    )

    keyboard = [
        ["🇺🇿 O‘zbekcha", "🇬🇧 English"],
        ["🇷🇺 Русский", "🇺🇿 Ўзбекча"],
    ]

    await update.message.reply_text(
        "🌐 Tilni tanlang / Choose language / Выберите язык:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )


async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🇺🇿 O‘zbekcha":
        context.user_data["language"] = "uz"
        await update.message.reply_text(
            "🇺🇿 O‘zbek tili tanlandi!\n\n"
            "💱 /kurs — valyuta kurslari\n"
            "ℹ️ /help — yordam"
        )

    elif text == "🇬🇧 English":
        context.user_data["language"] = "en"
        await update.message.reply_text(
            "🇬🇧 English selected!\n\n"
            "💱 /kurs — currency rates\n"
            "ℹ️ /help — help"
        )

    elif text == "🇷🇺 Русский":
        context.user_data["language"] = "ru"
        await update.message.reply_text(
            "🇷🇺 Русский язык выбран!\n\n"
            "💱 /kurs — курсы валют\n"
            "ℹ️ /help — помощь"
        )

    elif text == "🇺🇿 Ўзбекча":
        context.user_data["language"] = "uz_cyr"
        await update.message.reply_text(
            "🇺🇿 Ўзбек тили танланди!\n\n"
            "💱 /kurs — валюта курслари\n"
            "ℹ️ /help — ёрдам"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    language = context.user_data.get("language", "uz")

    if language == "en":
        text = (
            "📚 Bot features:\n\n"
            "💱 /kurs — currency rates\n"
            "💵 /kurs USD — US Dollar\n"
            "💶 /kurs EUR — Euro\n"
            "🇷🇺 /kurs RUB — Russian Ruble\n"
            "🇬🇧 /kurs GBP — British Pound"
        )

    elif language == "ru":
        text = (
            "📚 Возможности бота:\n\n"
            "💱 /kurs — курсы валют\n"
            "💵 /kurs USD — доллар США\n"
            "💶 /kurs EUR — евро\n"
            "🇷🇺 /kurs RUB — российский рубль\n"
            "🇬🇧 /kurs GBP — британский фунт"
        )

    elif language == "uz_cyr":
        text = (
            "📚 Бот имкониятлари:\n\n"
            "💱 /kurs — валюта курслари\n"
            "💵 /kurs USD — АҚШ доллари\n"
            "💶 /kurs EUR — евро\n"
            "🇷🇺 /kurs RUB — Россия рубли\n"
            "🇬🇧 /kurs GBP — Англия фунти"
        )

    else:
        text = (
            "📚 Bot imkoniyatlari:\n\n"
            "💱 /kurs — valyuta kurslari\n"
            "💵 /kurs USD — AQSH dollari\n"
            "💶 /kurs EUR — Yevro\n"
            "🇷🇺 /kurs RUB — Rossiya rubli\n"
            "🇬🇧 /kurs GBP — Angliya funti"
        )

    await update.message.reply_text(text)


async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(CBU_URL)
            response.raise_for_status()
            data = response.json()

        currencies = {
            "USD": "🇺🇸 Dollar",
            "EUR": "🇪🇺 Yevro",
            "RUB": "🇷🇺 Rubl",
            "GBP": "🇬🇧 Funt",
        }

        language = context.user_data.get("language", "uz")

        if context.args:
            code = context.args[0].upper()

            found = next(
                (item for item in data if item.get("Ccy") == code),
                None
            )

            if not found:
                await update.message.reply_text(
                    "❌ Valyuta topilmadi."
                )
                return

            if language == "en":
                text = (
                    f"💱 {found['CcyNm_EN']} ({code})\n\n"
                    f"🇺🇿 1 {code} = {found['Rate']} UZS\n\n"
                    f"📅 Date: {found['Date']}"
                )

            elif language == "ru":
                text = (
                    f"💱 {found['CcyNm_RU']} ({code})\n\n"
                    f"🇺🇿 1 {code} = {found['Rate']} сум\n\n"
                    f"📅 Дата: {found['Date']}"
                )

            elif language == "uz_cyr":
                text = (
                    f"💱 {found['CcyNm_UZ']} ({code})\n\n"
                    f"🇺🇿 1 {code} = {found['Rate']} сўм\n\n"
                    f"📅 Сана: {found['Date']}"
                )

            else:
                text = (
                    f"💱 {found['CcyNm_UZ']} ({code})\n\n"
                    f"🇺🇿 1 {code} = {found['Rate']} so‘m\n\n"
                    f"📅 Sana: {found['Date']}"
                )

            await update.message.reply_text(text)
            return

        if language == "en":
            text = "🇺🇿 <b>Central Bank of Uzbekistan exchange rates</b>\n\n"
        elif language == "ru":
            text = "🇺🇿 <b>Курсы валют Центрального банка Узбекистана</b>\n\n"
        elif language == "uz_cyr":
            text = "🇺🇿 <b>Ўзбекистон Марказий банки валюта курслари</b>\n\n"
        else:
            text = "🇺🇿 <b>O‘zbekiston Markaziy banki kurslari</b>\n\n"

        for code, name in currencies.items():
            found = next(
                (item for item in data if item.get("Ccy") == code),
                None
            )

            if found:
                text += f"{name}: <b>{found['Rate']} so‘m</b>\n"

        if data:
            if language == "en":
                text += f"\n📅 Date: {data[0]['Date']}"
            elif language == "ru":
                text += f"\n📅 Дата: {data[0]['Date']}"
            elif language == "uz_cyr":
                text += f"\n📅 Сана: {data[0]['Date']}"
            else:
                text += f"\n📅 Sana: {data[0]['Date']}"

        await update.message.reply_text(
            text,
            parse_mode="HTML"
        )

    except Exception:
        await update.message.reply_text(
            "⚠️ Kurslarni olishda xatolik yuz berdi."
        )


def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError("BOT_TOKEN topilmadi")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kurs", kurs))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            language_handler
        )
    )

    print("🤖 Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
