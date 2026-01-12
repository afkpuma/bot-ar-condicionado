class BotError(Exception):
    """Base generic error for the bot"""
    pass

class CalendarError(BotError):
    """Errors related to Google Calendar"""
    pass

class DatabaseError(BotError):
    """Errors related to Supabase"""
    pass

class ValidationError(BotError):
    """Input validation errors"""
    pass
