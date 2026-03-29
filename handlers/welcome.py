import db
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from handlers.auth import restricted

REPLY_KEYBOARD = ReplyKeyboardMarkup(
    [["🔗 New link", "☰ Menu"]],
    resize_keyboard=True,
    is_persistent=True,
)


@restricted
async def show_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi! Use the buttons below to get started.",
        reply_markup=REPLY_KEYBOARD,
    )


def build_menu_keyboard(telegram_id: int) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("🔗 New link", callback_data="menu:newlink")],
        [InlineKeyboardButton("🎧 Podcasts", callback_data="menu:podcasts")],
        [InlineKeyboardButton("🌐 Domains", callback_data="menu:domains")],
    ]
    if db.is_admin(telegram_id):
        rows.append([InlineKeyboardButton("👥 Users", callback_data="menu:users")])
    return InlineKeyboardMarkup(rows)


@restricted
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = build_menu_keyboard(update.effective_user.id)
    await update.effective_message.reply_text("Select an option below:", reply_markup=keyboard)


async def cancel_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ConversationHandler fallback: cancel active conversation and show menu."""
    await show_menu(update, context)
    return ConversationHandler.END
