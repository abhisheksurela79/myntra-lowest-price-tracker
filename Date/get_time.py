import datetime
import pytz


def date_now():
    ist = pytz.timezone('Asia/Kolkata')
    date_time = datetime.datetime.now(tz=ist)
    date = date_time.date().strftime("%B %d %Y")
    time = date_time.time().replace(microsecond=0).strftime("%I:%M %p")

    return {'date': str(date), 'time': str(time)}
