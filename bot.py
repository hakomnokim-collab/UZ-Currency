import os
import httpx

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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
CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇺🇿 Assalomu alaykum!\n\n"
        "💱 UZ Currency botiga xush kelibsiz!\n\n"
        "📊 Valyuta kurslarini ko‘rish uchun /kurs buyrug‘ini yuboring.\n"
        "ℹ️ Yordam uchun /help buyrug‘ini yuboring."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Bot imkoniyatlari:\n\n"
        "💱 /kurs — bugungi valyuta kurslari\n"
        "💵 /kurs USD — dollar kursi\n"
        "💶 /kurs EUR — yevro kursi\n"
        "₽ /kurs RUB — rubl kursi\n"
        "💷 /kurs GBP — funt kursi"
    )


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

        # /kurs USD kabi so‘rov
        if context.args:
            code = context.args[0].upper()

            found = next(
                (item for item in data if item.get("Ccy") == code),
                None
            )

            if not found:
                await update.message.reply_text(
                    "❌ Bu valyuta topilmadi.\n\n"
                    "Masalan: /kurs USD"
                )
                return

            await update.message.reply_text(
                f"💱 {found['CcyNm_UZ']} ({code})\n\n"
                f"🇺🇿 1 {code} = {found['Rate']} so‘m\n\n"
                f"📅 Sana: {found['Date']}"
            )
            return

        # Barcha asosiy kurslar
        text = "🇺🇿 <b>O‘zbekiston Markaziy banki kurslari</b>\n\n"

        for code, name in currencies.items():
            found = next(
                (item for item in data if item.get("Ccy") == code),
                None
            )

            if found:
                text += f"{name}: <b>{found['Rate']} so‘m</b>\n"

        if data:
            text += f"\n📅 Sana: {data[0]['Date']}"

        await update.message.reply_text(
            text,
            parse_mode="HTML"
        )

    except Exception:
        await update.message.reply_text(
            "⚠️ Kurslarni olishda xatolik yuz berdi.\n"
            "Birozdan keyin qayta urinib ko‘ring."
        )


def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError("BOT_TOKEN topilmadi")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("kurs", kurs))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
