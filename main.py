"""
╔══════════════════════════════════════════════╗
║         CleanBot — Telegram Group Cleaner    ║
║         Removes join/left messages instantly ║
╚══════════════════════════════════════════════╝

Requirements:
    pip install python-telegram-bot==20.7

Setup:
    1. Open config.py and fill in BOT_TOKEN and BOT_USERNAME
    2. Add bot to your group as Admin
    3. Enable "Delete Messages" permission for the bot
    4. Run: python cleanbot.py
    5. Send /start to your bot in private chat to pick language
"""

import logging
from config import BOT_TOKEN, BOT_USERNAME
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
#  TRANSLATIONS
# ──────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "en": {
        "flag": "🇬🇧",
        "name": "English",
        "welcome_title": "🤖 Welcome to CleanBot!",
        "welcome_body": (
            "I silently remove *join* and *left* messages from your Telegram groups.\n\n"
            "✦ Add me to a group\n"
            "✦ Make me an *Admin*\n"
            "✦ Give me *Delete Messages* permission\n\n"
            "That's it — I'll handle the rest automatically. 🚀"
        ),
        "lang_set": "✅ Language set to *English*.",
        "add_btn":  "➕ Add me to a group",
    },
    "ru": {
        "flag": "🇷🇺",
        "name": "Русский",
        "welcome_title": "🤖 Добро пожаловать в CleanBot!",
        "welcome_body": (
            "Я автоматически удаляю сообщения о *входе* и *выходе* участников из ваших групп.\n\n"
            "✦ Добавьте меня в группу\n"
            "✦ Назначьте меня *Администратором*\n"
            "✦ Дайте право *Удалять сообщения*\n\n"
            "Всё — дальше я всё сделаю сам. 🚀"
        ),
        "lang_set": "✅ Язык установлен: *Русский*.",
        "add_btn":  "➕ Добавить меня в группу",
    },
    "zh": {
        "flag": "🇨🇳",
        "name": "中文",
        "welcome_title": "🤖 欢迎使用 CleanBot！",
        "welcome_body": (
            "我会自动删除群组中的*入群*和*退群*消息。\n\n"
            "✦ 将我添加到群组\n"
            "✦ 设置我为*管理员*\n"
            "✦ 授予*删除消息*权限\n\n"
            "完成！我将自动处理剩下的一切。🚀"
        ),
        "lang_set": "✅ 语言已设置为*中文*。",
        "add_btn":  "➕ 将我添加到群组",
    },
}

user_languages: dict = {}


# ──────────────────────────────────────────────────────────────
#  KEYBOARDS
# ──────────────────────────────────────────────────────────────
def build_language_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            f"{TRANSLATIONS[code]['flag']}  {TRANSLATIONS[code]['name']}",
            callback_data=f"lang_{code}",
        )]
        for code in TRANSLATIONS
    ]
    return InlineKeyboardMarkup(rows)


def build_add_to_group_keyboard(lang_code: str) -> InlineKeyboardMarkup:
    lang = TRANSLATIONS[lang_code]
    add_url = f"https://t.me/{BOT_USERNAME}?startgroup=true"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(lang["add_btn"], url=add_url)],
    ])


# ──────────────────────────────────────────────────────────────
#  HANDLERS
# ──────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌐  *Choose your language*\n_Выберите язык · 选择语言_",
        parse_mode="Markdown",
        reply_markup=build_language_keyboard(),
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    code = query.data.replace("lang_", "")
    if code not in TRANSLATIONS:
        return

    user_id = query.from_user.id
    user_languages[user_id] = code
    lang = TRANSLATIONS[code]
    logger.info(f"Language [{code}] set for user {user_id}")

    text = (
        f"{lang['welcome_title']}\n\n"
        f"{lang['welcome_body']}\n\n"
        f"{lang['lang_set']}"
    )
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=build_add_to_group_keyboard(code),
    )


async def delete_service_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message is None:
        return

    should_delete = False

    if message.new_chat_members:
        names = [u.full_name for u in message.new_chat_members]
        logger.info(f"[JOIN] Deleting join message for: {', '.join(names)}")
        should_delete = True

    if message.left_chat_member:
        logger.info(f"[LEFT] Deleting left message for: {message.left_chat_member.full_name}")
        should_delete = True

    if should_delete:
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Could not delete message: {e}")


# ──────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_callback, pattern=r"^lang_"))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, delete_service_message))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER,  delete_service_message))

    logger.info("🤖  CleanBot is running — Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
