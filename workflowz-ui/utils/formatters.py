from datetime import date, datetime


def format_date(value: date | datetime | str | None) -> str:
    """Format a date value to YYYY-MM-DD string.
    
    Handles:
    - None: returns "-"
    - date/datetime objects: formats using strftime
    - strings: returns as-is if already formatted, or parses and formats
    """
    if value is None:
        return "-"
    
    # If it's already a string, check if it's in a valid format
    if isinstance(value, str):
        # If it's already in YYYY-MM-DD format, return as-is
        if len(value) == 10 and value.count("-") == 2:
            return value
        # Try to parse it
        try:
            # Try parsing as ISO format
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except (ValueError, AttributeError):
            # If parsing fails, return as-is
            return value
    
    # If it's a date or datetime object, format it
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    
    # Fallback: convert to string
    return str(value)
