from datetime import date


def format_date(value: date | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%Y-%m-%d")
