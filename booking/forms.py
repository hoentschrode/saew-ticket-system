from django.forms import ModelForm, ChoiceField
from django.core.exceptions import ObjectDoesNotExist
from .models import Booking, Performance


def get_performance_choices():
    performances = Performance.get_with_tickets_available()
    performance_choices = []
    for performance in performances:
        title = "{} (Noch {} tickets verfügbar)".format(
            performance.title,
            str(performance.tickets_available())
        )
        performance_choices.append((performance.id, title))
    return performance_choices


class BookingForm(ModelForm):
    performance = ChoiceField(choices=get_performance_choices(), label='Vorstellung')
    performance_model = None

    class Meta:
        model = Booking
        fields = ['first_name', 'last_name', 'number_of_tickets', 'email']
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'number_of_tickets': 'Anzahl:',
            'email': 'E-Mail-Adresse'
        }

    def is_valid(self):
        valid = super(BookingForm, self).is_valid()
        if not valid:
            return valid

        # Check valid performance
        try:
            self.performance_model = Performance.objects.get(pk=self.cleaned_data['performance'])
        except ObjectDoesNotExist:
            self.errors['performance'] = ["Ungültige Vorstellung!"]
            return False

        # Check if enough tickets are available
        tickets_available = self.performance_model.tickets_available()
        booked_tickets = self.cleaned_data['number_of_tickets']
        if tickets_available < booked_tickets:
            self.errors['performance'] = ['Vorstellung ist leider schon ausverkauft!']
            return False

        return valid
