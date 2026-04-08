import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    CommandHandler,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Translations ────────────────────────────────────────────────────────────
STRINGS = {
    "en": {
        "welcome": (
            "👋 *Welcome to CleanBot!*\n\n"
            "I silently delete join & left notifications from your groups — instantly.\n\n"
            "➕ Add me to a group\n"
            "🔑 Make me *Admin* with *Delete Messages* permission\n"
            "✨ Done — no more clutter!"
        ),
        "help": (
            "🛠 *CleanBot — Help*\n\n"
            "• Add me to any Telegram group\n"
            "• Grant me *Admin* → *Delete Messages* permission\n"
            "• Join & left spam disappears instantly!\n\n"
            "Commands:\n"
            "`/start` — Introduction\n"
            "`/help`  — This message\n"
            "`/lang`  — Change language"
        ),
        "lang_changed": "✅ Language set to *English*.",
        "choose_lang": "🌐 Choose your language:",
    },
    "ru": {
        "welcome": (
            "👋 *Добро пожаловать в CleanBot!*\n\n"
            "Я мгновенно удаляю уведомления о входе и выходе участников из ваших групп.\n\n"
            "➕ Добавьте меня в группу\n"
            "🔑 Назначьте меня *Администратором* с правом *Удалять сообщения*\n"
            "✨ Готово — никакого спама!"
        ),
        "help": (
            "🛠 *CleanBot — Помощь*\n\n"
            "• Добавьте меня в любую группу Telegram\n"
            "• Дайте права *Администратора* → *Удалять сообщения*\n"
            "• Уведомления о входе/выходе исчезают мгновенно!\n\n"
            "Команды:\n"
            "`/start` — Приветствие\n"
            "`/help`  — Это сообщение\n"
            "`/lang`  — Сменить язык"
        ),
        "lang_changed": "✅ Язык изменён на *Русский*.",
        "choose_lang": "🌐 Выберите язык:",
    },
    "zh": {
        "welcome": (
            "👋 *欢迎使用 CleanBot！*\n\n"
            "我会立即删除群组中的加入和退出通知，保持群组整洁。\n\n"
            "➕ 将我添加到群组\n"
            "🔑 将我设为*管理员*并开启*删除消息*权限\n"
            "✨ 完成 — 再也没有杂乱通知！"
        ),
        "help": (
            "🛠 *CleanBot — 帮助*\n\n"
            "• 将我添加到任意 Telegram 群组\n"
            "• 授予*管理员* → *删除消息*权限\n"
            "• 加入和退出通知将立即消失！\n\n"
            "命令：\n"
            "`/start` — 欢迎介绍\n"
            "`/help`  — 此消息\n"
            "`/lang`  — 切换语言"
        ),
        "lang_changed": "✅ 语言已设置为*中文*。",
        "choose_lang": "🌐 请选择语言：",
    },
}

LANG_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇨🇳 中文",    callback_data="lang_zh"),
    ]
])


def get_lang(context):
    return context.user_data.get("lang", "en")

def t(key, context):
    return STRINGS[get_lang(context)][key]


# ─── Handlers ───────────────────────────────────────────────────────────────

async def delete_service_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
        logger.info("Deleted service message in chat '%s' (%s)",
                    update.effective_chat.title, update.effective_chat.id)
    except Exception as e:
        logger.warning("Could not delete message: %s", e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        STRINGS["en"]["choose_lang"],
        reply_markup=LANG_KEYBOARD,
    )


async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        t("choose_lang", context),
        reply_markup=LANG_KEYBOARD,
    )


async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    context.user_data["lang"] = lang
    await query.edit_message_text(STRINGS[lang]["lang_changed"], parse_mode="Markdown")
    await query.message.reply_text(STRINGS[lang]["welcome"], parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(t("help", context), parse_mode="Markdown")


# ─── Entry point ────────────────────────────────────────────────────────────

def main():
    token = os.environ.get("8672542432:AAGWKjblkdwp0ueW2LTTvAPR5DK6N1ueu_Y")
    if not token:
        raise RuntimeError("Set the BOT_TOKEN environment variable first.")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
        delete_service_message,
    ))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_command))
    app.add_handler(CommandHandler("lang",  lang_command))
    app.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))

    logger.info("CleanBot is running …")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
