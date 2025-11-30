import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

DATA_FILE = "data.json"


def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_referrer(user_id, ref_id):
    data = load_data()
    if user_id not in data:
        data[user_id] = {"refs": []}

    if ref_id not in data[user_id]["refs"]:
        data[user_id]["refs"].append(ref_id)

    save_data(data)


def count_refs(user_id):
    data = load_data()
    if user_id in data:
        return len(data[user_id]["refs"])
    return 0


async def sen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.message.reply_to_message

    if not reply:
        await update.message.reply_text(
            "❗️ /sen şeýle yagdayda isleyar:\n"
            "1) Kim gerek bolsa şol adamyn ýazgan hatyna jogap berip /sen\n"
            "2) Ýa-da username bilen /sen @username"
        )
        return

    target = reply.from_user
    refs = count_refs(str(target.id))

    await update.message.reply_text(f"👤 {target.first_name} {refs} sany adam goşan.")


async def men(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    refs = count_refs(str(user.id))
    await update.message.reply_text(f"👤 Siz {refs} sany adam goşansyňyz.")


async def gosh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.message.reply_to_message

    if not reply:
        await update.message.reply_text("❗ Adamlaryňyzy birine geçirmek üçin, şol adamyň hatyna jogap berip /gosh diýip ýazyň.")
        return

    sender = update.message.from_user
    target = reply.from_user

    data = load_data()

    sender_id = str(sender.id)
    target_id = str(target.id)

    if sender_id not in data or len(data[sender_id]["refs"]) == 0:
        await update.message.reply_text("❗ Sizde geçiriljek adam ýok.")
        return

    refs_to_move = data[sender_id]["refs"]

    if target_id not in data:
        data[target_id] = {"refs": []}

    data[target_id]["refs"].extend(refs_to_move)
    data[sender_id]["refs"] = []

    save_data(data)

    await update.message.reply_text(f"✅ Siziň adamlaryňyz {target.first_name} adamyň üstüne geçdi.")


async def topadam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()

    ranking = [(uid, len(info["refs"])) for uid, info in data.items()]
    ranking.sort(key=lambda x: x[1], reverse=True)

    if not ranking:
        await update.message.reply_text("Häzirlikçe hiç kim adam goşmady.")
        return

    text = "🏆 *TOP adam goşanlar:*\n\n"

    place = 1
    for uid, count in ranking:
        try:
            user = await context.bot.get_chat(uid)
            text += f"{place}. {user.first_name} — {count} sany adam\n"
            place += 1
        except:
            pass

    await update.message.reply_text(text)


async def add_ref_on_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message

    if msg.new_chat_members:
        for member in msg.new_chat_members:
            referrer = msg.from_user
            if member.id != referrer.id:
                add_referrer(str(referrer.id), str(member.id))


def main():
    TOKEN = os.getenv("8365576118:AAHSRYraKNCS8DQLpsuC0pNgg6CWULk60HU")  # TOKEN railway variablesdan olinadi
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("sen", sen))
    app.add_handler(CommandHandler("men", men))
    app.add_handler(CommandHandler("gosh", gosh))
    app.add_handler(CommandHandler("topadam", topadam))

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, add_ref_on_join))

    print("Bot ishga tushdi...")
    app.run_polling()


if __name__ == "__main__":
    main()
