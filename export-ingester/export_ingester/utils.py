from datetime import UTC, date, datetime, timedelta


def now() -> datetime:
    return datetime.now(tz=UTC)


def get_range(date_: date) -> tuple[datetime, datetime]:
    next_day = date_ + timedelta(days=1)
    start = datetime(date_.year, date_.month, date_.day, tzinfo=UTC)
    end = datetime(next_day.year, next_day.month, next_day.day, tzinfo=UTC)
    return start, end
