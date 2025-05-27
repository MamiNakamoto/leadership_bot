from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes,
    CallbackQueryHandler
)
from database import (
    init_db, is_admin, get_siralama, reset_siralama,
    puan_ekle, puan_sil, add_admin
)

BOT_TOKEN = "7754336424:AAEg18duiISQYkDmL5eA0KOZMq8gQXKfCxE"
DB_PATH = "leaderboard.db"
YED_KANAL_ID = -1002503990729  # Yedekleme kanalının ID'sini buraya girin
MEXC_GROUP_ID = -1001463977309  # MEXC kanalının ID'sini buraya girin

def only_in_mexc_group(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != MEXC_GROUP_ID:
            return  # Komut çalıştırılmaz
        return await func(update, context)
    return wrapper

# /siralama
@only_in_mexc_group
async def siralama(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = get_siralama()
    if not data:
        await update.message.reply_text("📉 Bu hafta için henüz puanlama yok.")
        return

    msg = "🏆 Haftalık Liderlik Tablosu:\n\n"
    for i, (username, at_etiket, puan) in enumerate(data, start=1):
        msg += f"{i}. {username} ({at_etiket}): {puan} puan\n"
    await update.message.reply_text(msg)

# /sifirla → butonlu onay
@only_in_mexc_group
async def sifirla(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bu komutu sadece adminler kullanabilir.")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Evet", callback_data="sifirla_evet"),
         InlineKeyboardButton("❌ Hayır", callback_data="sifirla_hayir")]
    ])
    await update.message.reply_text("⚠️ Liderlik tablosunu sıfırlamak istediğinize emin misiniz?", reply_markup=keyboard)

# Callback handler
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.edit_message_text("❌ Bu işlemi sadece adminler yapabilir.")
        return

    if query.data == "sifirla_evet":
        reset_siralama()
        await query.edit_message_text("✅ Liderlik tablosu sıfırlandı.")
    elif query.data == "sifirla_hayir":
        await query.edit_message_text("🚫 Liderlik tablosu sıfırlama işlemi iptal edildi.")

# /puanekle
@only_in_mexc_group
async def puan_ekle_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bu komutu sadece adminler kullanabilir.")
        return

    if not context.args or not context.args[0].startswith("@"):
        await update.message.reply_text("❗ Doğru kullanım: /puanekle @kullaniciadi")
        return

    at_etiket = context.args[0]
    username = at_etiket[1:]
    puan_ekle(username, at_etiket)
    await update.message.reply_text(f"✅ {at_etiket} kullanıcısına 1 puan eklendi.")

    # 📤 Veritabanını yedek kanalına gönder
    try:
        with open(DB_PATH, "rb") as db_file:
            await context.bot.send_document(
                chat_id=YED_KANAL_ID,
                document=InputFile(db_file, filename="leaderboard.db"),
                caption=f"📦 Otomatik Yedekleme - {at_etiket}"
            )
    except Exception as e:
        await update.message.reply_text("⚠️ Yedekleme başarısız: " + str(e))

# /puansil
@only_in_mexc_group
async def puan_sil_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ Bu komutu sadece adminler kullanabilir.")
        return

    if not context.args or not context.args[0].startswith("@"):
        await update.message.reply_text("❗ Doğru kullanım: /puansil @kullaniciadi")
        return

    at_etiket = context.args[0]
    username = at_etiket[1:]
    puan_sil(username)
    await update.message.reply_text(f"⚠️ {at_etiket} kullanıcısından 1 puan silindi.")

# /adminekle
@only_in_mexc_group
async def admin_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    sender_id = update.effective_user.id
    if not is_admin(sender_id):
        return  # Komut diğer kullanıcılar için sessizce yok sayılır

    if not context.args or not context.args[0].startswith("@"):
        await update.message.reply_text("❗ Doğru kullanım: /adminekle @kullaniciadi")
        return

    at_etiket = context.args[0]
    username = at_etiket[1:]
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    else:
        await update.message.reply_text("ℹ️ Bu komutu kullanırken kullanıcı mesajına yanıt verin.")
        return

    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    add_admin(user.id, at_etiket, full_name)
    await update.message.reply_text(f"✅ {at_etiket} admin olarak eklendi.")

# Bot başlangıç
def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("siralama", siralama))
    app.add_handler(CommandHandler("sifirla", sifirla))
    app.add_handler(CommandHandler("puanekle", puan_ekle_cmd))
    app.add_handler(CommandHandler("puansil", puan_sil_cmd))
    app.add_handler(CommandHandler("adminekle", admin_ekle))
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("Bot çalışıyor...")
    app.run_polling()

if __name__ == "__main__":
    main()
