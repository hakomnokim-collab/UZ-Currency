import os
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇺🇿 UZ Currency botiga xush kelibsiz!\n\n"
        "💱 Kurslarni ko‘rish uchun /kurs buyrug‘ini bosing."
    )


async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(CBU_URL)
            response.raise_for_status()
            data = response.json()

        kerakli = ["USD", "EUR", "RUB", "GBP"]

        text = "💱 O‘zbekiston valyuta kurslari:\n\n"

        for item in data:
            if item["Ccy"] in kerakli:
                text += (
                    f"💵 {item['Ccy']}: "
                    f"{item['Rate']} so‘m\n"
                )

        await update.message.reply_text(text)

    except Exception:
        await update.message.reply_text(
            "❌ Kurslarni olishda xatolik yuz berdi."
        )


def main():
    token = os.environ["TELEGRAM_BOT_TOKEN"]

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kurs", kurs))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()