from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
import db


def restricted(func):
    """Decorator: silently ignore messages from users not in the allowed list."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not db.is_allowed(user_id):
            return  # silent ignore
        return await func(update, context, *args, **kwargs)
    return wrapper


def admin_only(func):
    """Decorator: silently ignore if user is not admin."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not db.is_admin(user_id):
            return  # silent ignore
        return await func(update, context, *args, **kwargs)
    return wrapper
