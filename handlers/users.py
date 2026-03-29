from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

import db
from handlers.auth import admin_only

_MENU_TEXTS = filters.Text(["🔗 New link", "☰ Menu"])

# ── States ─────────────────────────────────────────────────────────────────
(
    USERS_MENU,
    ADD_USER_ID,
    REMOVE_PICK,
) = range(3)


def _menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add user", callback_data="usr_add")],
        [InlineKeyboardButton("🗑 Remove user", callback_data="usr_remove")],
        [InlineKeyboardButton("❌ Close", callback_data="usr_close")],
    ])


@admin_only
async def users_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if cq := update.callback_query:
        await cq.answer()
    users = db.list_users()
    if users:
        lines = []
        for u in users:
            tag = " 👑" if u["is_admin"] else ""
            name = u["nickname"] or "—"
            lines.append(f"• `{u['telegram_id']}` {name}{tag}")
        text = "Allowed users:\n\n" + "\n".join(lines)
    else:
        text = "No users yet."
    await update.effective_message.reply_text(text, reply_markup=_menu_keyboard(), parse_mode="Markdown")
    return USERS_MENU


async def users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "usr_close":
        await query.edit_message_text("Done.")
        return ConversationHandler.END

    if query.data == "usr_add":
        await query.edit_message_text(
            "Send the Telegram user ID to allow:\n_(They can get their ID from @userinfobot)_",
            parse_mode="Markdown",
        )
        return ADD_USER_ID

    if query.data == "usr_remove":
        users = [u for u in db.list_users() if not u["is_admin"]]
        if not users:
            await query.edit_message_text("No non-admin users to remove.", reply_markup=_menu_keyboard())
            return USERS_MENU
        rows = [
            [InlineKeyboardButton(
                f"{u['nickname'] or u['telegram_id']} ({u['telegram_id']})",
                callback_data=f"rmusr:{u['telegram_id']}"
            )]
            for u in users
        ]
        rows.append([InlineKeyboardButton("↩ Back", callback_data="rmusr:back")])
        await query.edit_message_text("Which user to remove?", reply_markup=InlineKeyboardMarkup(rows))
        return REMOVE_PICK

    return USERS_MENU


async def add_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if not text.lstrip("-").isdigit():
        await update.message.reply_text("That doesn't look like a valid Telegram ID. Try again:")
        return ADD_USER_ID

    telegram_id = int(text)
    db.add_user(telegram_id)
    await update.message.reply_text(f"✅ User `{telegram_id}` added.", parse_mode="Markdown")
    return ConversationHandler.END


async def remove_pick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "rmusr:back":
        users = db.list_users()
        lines = [f"• `{u['telegram_id']}` {u['nickname'] or '—'}" for u in users]
        text = "Allowed users:\n\n" + "\n".join(lines) if lines else "No users yet."
        await query.edit_message_text(text, reply_markup=_menu_keyboard(), parse_mode="Markdown")
        return USERS_MENU

    telegram_id = int(query.data.split(":")[1])
    db.remove_user(telegram_id)
    await query.edit_message_text(f"✅ User `{telegram_id}` removed.", parse_mode="Markdown")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


def users_handler() -> ConversationHandler:
    from handlers.welcome import cancel_to_menu
    return ConversationHandler(
        entry_points=[
            CommandHandler("users", users_entry),
            CallbackQueryHandler(users_entry, pattern="^menu:users$"),
        ],
        states={
            USERS_MENU: [CallbackQueryHandler(users_menu, pattern="^usr_")],
            ADD_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~_MENU_TEXTS, add_user_id)],
            REMOVE_PICK: [CallbackQueryHandler(remove_pick, pattern="^rmusr:")],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.Text(["☰ Menu"]), cancel_to_menu),
        ],
        per_message=False,
    )
