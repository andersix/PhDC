# src/utils/exceptions.py
class PiHoleDisplayError(Exception):
    """Base exception for PiHole Display application"""
    pass

class DisplayError(PiHoleDisplayError):
    """Display-related errors"""
    pass

class BacklightError(DisplayError):
    """Backlight control errors"""
    pass

class ButtonError(PiHoleDisplayError):
    """Button-related errors"""
    pass

class ServiceError(PiHoleDisplayError):
    """Service operation errors"""
    pass

class ConfigError(PiHoleDisplayError):
    """Configuration-related errors"""
    pass

