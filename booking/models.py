from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator, BaseValidator
from django.utils import formats


class Base(models.Model):

    class Meta:
        abstract = True


class Performance(Base):
    title = models.CharField(max_length=200, help_text="Performance title")
    start = models.DateTimeField(help_text="Date and time of performance")
    capacity = models.IntegerField(default=0, help_text='Maximum number of tickes')

    def __str__(self):
        return self.title

    @classmethod
    def get_with_tickets_available(cls, pk=None):
        if pk is None:
            performances = cls.objects.all().annotate(
                tickets_booked=Sum('booking__number_of_tickets')
            )
        else:
            performances = cls.objects.get(pk=pk).annotate(
                tickets_booked=Sum('booking__number_of_tickets')
            )
        return performances

    def tickets_available(self):
        tickets_booked = Performance.objects.filter(id=self.id).annotate(
            tickets_booked=Sum('booking__number_of_tickets')
        )[0].tickets_booked

        return self.capacity - int(tickets_booked or 0)

    @property
    def start_date(self):
        return formats.date_format(self.start, format='DATE_FORMAT', use_l10n=True)

    @property
    def start_time(self):
        return formats.date_format(self.start, format='TIME_FORMAT', use_l10n=True)


class Booking(Base):
    first_name = models.CharField(max_length=200, help_text="First name")
    last_name = models.CharField(max_length=200, help_text='Last name')
    email = models.EmailField()
    booking_date = models.DateTimeField(auto_now_add=True)
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE)
    number_of_tickets = models.IntegerField(
        blank=True,
        default=0,
        validators=[
            MinValueValidator(1, 'Mindestens ein Ticket'),
            MaxValueValidator(5, 'Maximal 5 Tickets pro Buchung erlaubt')
        ]
    )
    code = models.CharField(max_length=10, unique=True, blank=True)

    def __str__(self):
        return self.email


class Ticket(Base):
    code = models.CharField(max_length=10, unique=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)

