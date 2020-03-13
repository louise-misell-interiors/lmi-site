from django.utils import timezone
import datetime
from django.core.management.base import BaseCommand
from bookings import models


INTERVALS = [
    (datetime.timedelta(days=1), "tomorrow"),
    (datetime.timedelta(days=7), "7 days"),
]


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n/10 % 10 != 1)*(n % 10 < 4)*n % 10::4])


class Command(BaseCommand):
    help = "Sends notifications to booking customers"

    def handle(self, *args, **options):
        now = timezone.now()
        bookings = models.Booking.objects.filter(time__gte=now)

        for booking in bookings:
            last_notif = booking.last_notification_sent if booking.last_notification_sent else \
                datetime.datetime.fromtimestamp(0, booking.time.tzinfo)
            last_notif_delta = booking.time - last_notif
            time_in_future = booking.time - now
            ordinal_date = ordinal(booking.time.day)
            formatted_time = booking.time.strftime(f"%A the {ordinal_date} of %B at %-I:%M%p")

            for interval in INTERVALS:
                if time_in_future <= interval[0]:
                    if last_notif_delta >= interval[0]:
                        print(
                            f"Your {booking.type.name.lower()} with Louise Misell Interiors is coming up in "
                            f"{interval[1]} on {formatted_time}. Please contact Louise to make any amendments or to "
                            f"cancel."
                        )
                        booking.last_notification_sent = now
                        booking.save()
                    break

