from datetime import datetime, timedelta


def get_current_time_interval() -> tuple[datetime, datetime]:
    now = datetime.now()
    if now.hour >= 5:
        try:
            end = datetime(now.year, now.month, now.day + 1, 5, 0)
        except ValueError as e:
            end = datetime(now.year, now.month + 1, 1, 5, 0)
    else:
        end = datetime(now.year, now.month, now.day, 5, 0)
    start = end - timedelta(hours=24)
    return start, end
