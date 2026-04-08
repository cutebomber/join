import logging
import asyncio
from typing import Dict, Optional

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    ChatMemberUpdated, 
    ChatMember
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    ChatMemberHandler, 
    ContextTypes,
    MessageHandler,
    filters
)

# ========== CONFIGURATION ==========
TOKEN = "8672542432:AAGWKjblkdwp0ueW2LTTvAPR5DK6N1ueu_Y"  # Replace with your bot token

# ========== LANGUAGE SUPPORT ==========
LANGUAGES = {
    "en": {
        "name": "English",
        "flag": "🇬🇧",
        "welcome": "🌟 *Welcome to the Group Cleaner Bot!* 🌟\n\nPlease choose your preferred language:",
        "lang_set": "✅ Language set to English! Now add me to a group and make me admin to start cleaning join/leave messages.",
        "start_private": "🚀 *Group Cleaner Bot* is ready!\n\nAdd me to any group and make me an administrator. I will automatically delete all 'joined' and 'left' messages instantly.",
        "clean_enabled": "✨ Clean mode activated! I will now delete all join/leave messages in this group.",
        "clean_disabled": "❌ Clean mode deactivated. I will no longer delete join/leave messages.",
        "already_cleaning": "ℹ️ Clean mode is already active.",
        "already_not_cleaning": "ℹ️ Clean mode is already inactive.",
        "not_admin": "⚠️ I need to be an administrator to delete messages. Please promote me!",
        "left_msg": "🚪 *{user}* left the group",
        "join_msg": "👋 *{user}* joined the group",
        "deleted": "🗑️ Deleted",
        "settings": "⚙️ *Settings*\n\nCurrent language: English 🇬🇧\n\nUse buttons below to change language or check status.",
        "status_on": "🟢 Clean mode: *ON*",
        "status_off": "🔴 Clean mode: *OFF*",
        "help_text": """
🤖 *Group Cleaner Bot Help*

• Add me to any group and make me admin
• I will instantly delete all join/left messages
• Use /settings to change language
• Use /status to check current mode
• Use /clean on/off to toggle cleaning

Made with ❤️ for clean groups
"""
    },
    "ru": {
        "name": "Русский",
        "flag": "🇷🇺",
        "welcome": "🌟 *Добро пожаловать в Group Cleaner Bot!* 🌟\n\nПожалуйста, выберите предпочитаемый язык:",
        "lang_set": "✅ Язык установлен: Русский! Добавьте меня в группу и сделайте админом, чтобы начать очистку сообщений о входе/выходе.",
        "start_private": "🚀 *Group Cleaner Bot* готов!\n\nДобавьте меня в любую группу и сделайте администратором. Я буду автоматически удалять все сообщения о входе и выходе участников.",
        "clean_enabled": "✨ Режим очистки активирован! Теперь я буду удалять все сообщения о входе/выходе в этой группе.",
        "clean_disabled": "❌ Режим очистки деактивирован. Сообщения о входе/выходе больше не будут удаляться.",
        "already_cleaning": "ℹ️ Режим очистки уже активен.",
        "already_not_cleaning": "ℹ️ Режим очистки уже неактивен.",
        "not_admin": "⚠️ Мне нужны права администратора для удаления сообщений. Пожалуйста, назначьте меня админом!",
        "left_msg": "🚪 *{user}* покинул группу",
        "join_msg": "👋 *{user}* присоединился к группе",
        "deleted": "🗑️ Удалено",
        "settings": "⚙️ *Настройки*\n\nТекущий язык: Русский 🇷🇺\n\nИспользуйте кнопки ниже, чтобы изменить язык или проверить статус.",
        "status_on": "🟢 Режим очистки: *ВКЛ*",
        "status_off": "🔴 Режим очистки: *ВЫКЛ*",
        "help_text": """
🤖 *Помощь Group Cleaner Bot*

• Добавьте меня в группу и сделайте админом
• Я мгновенно удаляю все сообщения о входе/выходе
• Используйте /settings для смены языка
• Используйте /status для проверки режима
• Используйте /clean on/off для включения/выключения очистки

Сделано с ❤️ для чистых групп
"""
    },
    "zh": {
        "name": "中文",
        "flag": "🇨🇳",
        "welcome": "🌟 *欢迎使用群聊清理机器人！* 🌟\n\n请选择您的首选语言：",
        "lang_set": "✅ 语言设置为中文！将我添加到群组并设为管理员，即可开始清理加入/离开消息。",
        "start_private": "🚀 *群聊清理机器人* 已就绪！\n\n将我添加到任何群组并设为管理员。我将自动删除所有成员加入和离开的消息。",
        "clean_enabled": "✨ 清理模式已激活！我将删除此群组中所有加入/离开消息。",
        "clean_disabled": "❌ 清理模式已停用。不再删除加入/离开消息。",
        "already_cleaning": "ℹ️ 清理模式已处于激活状态。",
        "already_not_cleaning": "ℹ️ 清理模式已处于停用状态。",
        "not_admin": "⚠️ 我需要管理员权限才能删除消息。请提升我的权限！",
        "left_msg": "🚪 *{user}* 离开了群组",
        "join_msg": "👋 *{user}* 加入了群组",
        "deleted": "🗑️ 已删除",
        "settings": "⚙️ *设置*\n\n当前语言：中文 🇨🇳\n\n使用下方按钮更改语言或查看状态。",
        "status_on": "🟢 清理模式：*开启*",
        "status_off": "🔴 清理模式：*关闭*",
        "help_text": """
🤖 *群聊清理机器人帮助*

• 将我添加到任何群组并设为管理员
• 我会立即删除所有加入/离开消息
• 使用 /settings 更改语言
• 使用 /status 查看当前模式
• 使用 /clean on/off 切换清理功能

用 ❤️ 打造干净群组
"""
    }
}

# Store group settings: {group_id: {"cleaning": bool, "lang": str}}
group_settings: Dict[int, Dict[str, any]] = {}

# Store user language preferences: {user_id: lang_code}
user_languages: Dict[int, str] = {}

# ========== HELPER FUNCTIONS ==========
def get_text(lang_code: str, key: str, **kwargs) -> str:
    """Get localized text for a given language code and key"""
    lang_data = LANGUAGES.get(lang_code, LANGUAGES["en"])
    text = lang_data.get(key, LANGUAGES["en"][key])
    if kwargs:
        text = text.format(**kwargs)
    return text

async def get_user_lang(user_id: int) -> str:
    """Get user's preferred language, fallback to English"""
    return user_languages.get(user_id, "en")

async def get_group_lang(chat_id: int) -> str:
    """Get group's language setting, fallback to English"""
    if chat_id in group_settings:
        return group_settings[chat_id].get("lang", "en")
    return "en"

async def is_cleaning_enabled(chat_id: int) -> bool:
    """Check if cleaning is enabled for a group"""
    if chat_id in group_settings:
        return group_settings[chat_id].get("cleaning", False)
    return False

async def set_cleaning(chat_id: int, enabled: bool):
    """Enable or disable cleaning for a group"""
    if chat_id not in group_settings:
        group_settings[chat_id] = {"cleaning": enabled, "lang": "en"}
    else:
        group_settings[chat_id]["cleaning"] = enabled

async def set_group_lang(chat_id: int, lang_code: str):
    """Set language for a group"""
    if chat_id not in group_settings:
        group_settings[chat_id] = {"cleaning": False, "lang": lang_code}
    else:
        group_settings[chat_id]["lang"] = lang_code

# ========== COMMAND HANDLERS ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - show language selection or main menu"""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    # If in private chat, show language selection
    if chat_type == "private":
        keyboard = []
        for code, data in LANGUAGES.items():
            keyboard.append([InlineKeyboardButton(
                f"{data['flag']} {data['name']}", 
                callback_data=f"lang_{code}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        welcome_text = get_text("en", "welcome")  # Default to English for initial message
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    else:
        # In group, just show status
        lang = await get_group_lang(update.effective_chat.id)
        cleaning = await is_cleaning_enabled(update.effective_chat.id)
        status_text = get_text(lang, "status_on") if cleaning else get_text(lang, "status_off")
        await update.message.reply_text(f"{status_text}\n\n{get_text(lang, 'help_text')}", parse_mode="Markdown")

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command - show settings menu"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    if chat_type == "private":
        lang = await get_user_lang(user_id)
    else:
        lang = await get_group_lang(chat_id)
    
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data=f"setlang_en_{chat_type}")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data=f"setlang_ru_{chat_type}")],
        [InlineKeyboardButton("🇨🇳 中文", callback_data=f"setlang_zh_{chat_type}")],
        [InlineKeyboardButton("📊 Status", callback_data=f"status_{chat_type}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(get_text(lang, "settings"), reply_markup=reply_markup, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command - show cleaning status"""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    if chat_type == "private":
        user_id = update.effective_user.id
        lang = await get_user_lang(user_id)
        await update.message.reply_text(get_text(lang, "help_text"), parse_mode="Markdown")
    else:
        lang = await get_group_lang(chat_id)
        cleaning = await is_cleaning_enabled(chat_id)
        status_text = get_text(lang, "status_on") if cleaning else get_text(lang, "status_off")
        await update.message.reply_text(status_text, parse_mode="Markdown")

async def clean_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clean on/off command"""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    if chat_type == "private":
        await update.message.reply_text("Please add me to a group first!")
        return
    
    args = context.args
    if not args or args[0].lower() not in ["on", "off"]:
        await update.message.reply_text("Usage: /clean on  or  /clean off")
        return
    
    lang = await get_group_lang(chat_id)
    action = args[0].lower()
    
    if action == "on":
        if await is_cleaning_enabled(chat_id):
            await update.message.reply_text(get_text(lang, "already_cleaning"))
        else:
            await set_cleaning(chat_id, True)
            await update.message.reply_text(get_text(lang, "clean_enabled"), parse_mode="Markdown")
    else:  # off
        if not await is_cleaning_enabled(chat_id):
            await update.message.reply_text(get_text(lang, "already_not_cleaning"))
        else:
            await set_cleaning(chat_id, False)
            await update.message.reply_text(get_text(lang, "clean_disabled"), parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    
    if chat_type == "private":
        user_id = update.effective_user.id
        lang = await get_user_lang(user_id)
    else:
        lang = await get_group_lang(chat_id)
    
    await update.message.reply_text(get_text(lang, "help_text"), parse_mode="Markdown")

# ========== CALLBACK QUERY HANDLER ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    chat_type = query.message.chat.type
    
    # Language selection from start menu (private chat only)
    if data.startswith("lang_"):
        lang_code = data.split("_")[1]
        user_languages[user_id] = lang_code
        
        # Show confirmation with main menu
        keyboard = [[InlineKeyboardButton("⚙️ Settings", callback_data="main_settings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            get_text(lang_code, "lang_set"), 
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        # Send main menu after a short delay
        await asyncio.sleep(1)
        await query.message.reply_text(
            get_text(lang_code, "start_private"),
            parse_mode="Markdown"
        )
    
    # Set language from settings
    elif data.startswith("setlang_"):
        parts = data.split("_")
        lang_code = parts[1]
        origin = parts[2]  # private or group
        
        if origin == "private":
            user_languages[user_id] = lang_code
            await query.edit_message_text(
                get_text(lang_code, "lang_set"),
                parse_mode="Markdown"
            )
        else:
            chat_id = query.message.chat.id
            await set_group_lang(chat_id, lang_code)
            await query.edit_message_text(
                get_text(lang_code, "lang_set"),
                parse_mode="Markdown"
            )
    
    # Status callback
    elif data.startswith("status_"):
        origin = data.split("_")[1]
        if origin == "private":
            lang = await get_user_lang(user_id)
            await query.edit_message_text(
                get_text(lang, "help_text"),
                parse_mode="Markdown"
            )
        else:
            chat_id = query.message.chat.id
            lang = await get_group_lang(chat_id)
            cleaning = await is_cleaning_enabled(chat_id)
            status_text = get_text(lang, "status_on") if cleaning else get_text(lang, "status_off")
            await query.edit_message_text(status_text, parse_mode="Markdown")
    
    # Main settings from start
    elif data == "main_settings":
        lang = await get_user_lang(user_id)
        keyboard = [
            [InlineKeyboardButton("🇬🇧 English", callback_data=f"setlang_en_private")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data=f"setlang_ru_private")],
            [InlineKeyboardButton("🇨🇳 中文", callback_data=f"setlang_zh_private")],
            [InlineKeyboardButton("📊 Status", callback_data="status_private")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            get_text(lang, "settings"),
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# ========== CHAT MEMBER HANDLER (CLEAN JOIN/LEAVE MESSAGES) ==========
async def track_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete join/leave messages instantly"""
    result: ChatMemberUpdated = update.chat_member
    chat_id = result.chat.id
    
    # Check if cleaning is enabled for this group
    if not await is_cleaning_enabled(chat_id):
        return
    
    # Check if bot is admin (can delete messages)
    bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
    if bot_member.status not in ["administrator", "creator"]:
        lang = await get_group_lang(chat_id)
        await context.bot.send_message(chat_id, get_text(lang, "not_admin"), parse_mode="Markdown")
        return
    
    # Detect if it's a join or leave event
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status
    
    user = result.new_chat_member.user
    user_name = user.full_name
    if user.username:
        user_name = f"@{user.username}"
    
    lang = await get_group_lang(chat_id)
    
    # Join event
    if old_status in ["left", "kicked"] and new_status in ["member", "administrator", "creator"]:
        # Find and delete the service message (join)
        # The service message is the one we're responding to
        if update.chat_member.invite_link:
            pass  # Handle invite link joins
        
        # Send a stylish notification that will be deleted after 2 seconds
        msg = await context.bot.send_message(
            chat_id, 
            get_text(lang, "join_msg", user=user_name),
            parse_mode="Markdown"
        )
        await asyncio.sleep(2)
        await msg.delete()
    
    # Leave event
    elif old_status in ["member", "administrator", "creator"] and new_status in ["left", "kicked"]:
        msg = await context.bot.send_message(
            chat_id,
            get_text(lang, "left_msg", user=user_name),
            parse_mode="Markdown"
        )
        await asyncio.sleep(2)
        await msg.delete()

# ========== MESSAGE HANDLER FOR SERVICE MESSAGES ==========
async def handle_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete Telegram's built-in service messages for joins/leaves"""
    chat_id = update.effective_chat.id
    message = update.message
    
    if not await is_cleaning_enabled(chat_id):
        return
    
    # Check if bot is admin
    bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
    if bot_member.status not in ["administrator", "creator"]:
        return
    
    # Delete service messages (new_chat_members, left_chat_member)
    if message.new_chat_members or message.left_chat_member:
        try:
            await message.delete()
        except Exception as e:
            logging.error(f"Failed to delete service message: {e}")

# ========== MAIN FUNCTION ==========
def main():
    """Start the bot"""
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("clean", clean_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add callback handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add chat member handler for tracking joins/leaves
    application.add_handler(ChatMemberHandler(track_chat_members, ChatMemberHandler.CHAT_MEMBER))
    
    # Add message handler for deleting service messages
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_service_messages))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, handle_service_messages))
    
    # Start the bot
    print("🤖 Bot is running... Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
