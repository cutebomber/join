import asyncio
import logging
from telegram import Update, ChatMember
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token from @BotFather
BOT_TOKEN = '8601450793:AAEW6wlf2xkoGwrbJr7V0H3tjSDGlLE4UoY'

async def delete_join_leave_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Delete messages that are join or leave notifications
    """
    try:
        message = update.effective_message
        
        # Check if message is a service message (join/leave)
        if message:
            # Check for new chat members (join messages)
            if message.new_chat_members:
                # Delete the join message
                await message.delete()
                logger.info(f"Deleted join message from chat {message.chat_id}")
                
                # Optional: Send a private welcome message to new member
                # for member in message.new_chat_members:
                #     if not member.is_bot:
                #         await message.chat.send_message(
                #             f"👋 Welcome {member.first_name}! Please read the group rules."
                #         )
            
            # Check for left chat member (leave messages)
            elif message.left_chat_member:
                # Delete the leave message
                await message.delete()
                logger.info(f"Deleted leave message from chat {message.chat_id}")
                
            # Check for chat title changes (optional, can be removed)
            elif message.new_chat_title:
                await message.delete()
                logger.info(f"Deleted chat title change message from chat {message.chat_id}")
                
            # Check for chat photo changes (optional, can be removed)
            elif message.new_chat_photo or message.delete_chat_photo:
                await message.delete()
                logger.info(f"Deleted chat photo change message from chat {message.chat_id}")
                
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command
    """
    welcome_text = (
        "🤖 *Bot Started Successfully!*\n\n"
        "I will automatically delete all join and leave messages from this group.\n\n"
        "📌 *Requirements:*\n"
        "• Add me as an admin in the group\n"
        "• Give me 'Delete Messages' permission\n\n"
        "✅ The group will stay clean from join/leave notifications!"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /help command
    """
    help_text = (
        "🔧 *How to use this bot:*\n\n"
        "1️⃣ Add this bot to your group\n"
        "2️⃣ Make the bot an admin with 'Delete Messages' permission\n"
        "3️⃣ The bot will automatically delete:\n"
        "   • Join messages\n"
        "   • Leave messages\n"
        "   • Group title changes (optional)\n"
        "   • Group photo changes (optional)\n\n"
        "📝 *Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/status - Check bot status in this chat"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check bot's admin status in the chat
    """
    chat_id = update.effective_chat.id
    
    try:
        # Get bot's chat member status
        bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
        
        if bot_member.status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            status_text = (
                "✅ *Bot Status:* Active\n\n"
                f"• Chat: {update.effective_chat.title}\n"
                f"• Admin: Yes\n"
                f"• Permission: Can delete messages\n\n"
                "The bot is working properly!"
            )
        else:
            status_text = (
                "⚠️ *Bot Status:* Limited\n\n"
                f"• Chat: {update.effective_chat.title}\n"
                f"• Admin: No\n\n"
                "Please make me an admin with 'Delete Messages' permission to work properly!"
            )
    except Exception as e:
        status_text = f"❌ Error checking status: {str(e)}"
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle errors
    """
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """
    Main function to run the bot
    """
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS | 
        filters.StatusUpdate.LEFT_CHAT_MEMBER |
        filters.StatusUpdate.NEW_CHAT_TITLE |
        filters.StatusUpdate.CHAT_PHOTO,
        delete_join_leave_messages
    ))
    
    application.add_handler(MessageHandler(filters.COMMAND & filters.Regex('^/start$'), start_command))
    application.add_handler(MessageHandler(filters.COMMAND & filters.Regex('^/help$'), help_command))
    application.add_handler(MessageHandler(filters.COMMAND & filters.Regex('^/status$'), status_command))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("Bot is starting...")
    print("Make sure you've set the correct BOT_TOKEN!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
