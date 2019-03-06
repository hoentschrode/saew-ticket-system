from django.forms import ModelForm, ChoiceField, CharField, TextInput
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
    email_confirmation = CharField(max_length=254, required=True, label='E-Mail (zur Bestätigung)',
                                   widget=TextInput(attrs={'placeholder': 'Geben Sie Ihre E-Mail-Adresse erneut ein.'}))
    performance_model = None

    class Meta:
        model = Booking
        fields = ['first_name', 'last_name', 'number_of_tickets', 'email', 'email_confirmation']
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'number_of_tickets': 'Anzahl:',
            'email': 'E-Mail-Adresse'
        }
        help_texts = {
            'first_name': 'Informationen über den Schutz Ihrer Daten, finden Sie in der Datenschutzerklärung.',
            'last_name': '',
            'number_of_tickets': '',
            'email': ''
        }
        widgets = {
            'first_name': TextInput(attrs={'placeholder': 'Vorname'}),
            'last_name': TextInput(attrs={'placeholder': 'Nachname'}),
            'email': TextInput(attrs={'placeholder': 'Geben Sie Ihre E-Mail-Adresse ein.'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['performance'].choices = get_performance_choices()

    def is_valid(self):
        valid = super(BookingForm, self).is_valid()
        if not valid:
            return valid

        # Check mail confirmation
        if self.cleaned_data['email'] != self.cleaned_data['email_confirmation']:
            self.add_error('email', 'Bitte überprüfen Sie die E-Mail-Adresse')
            return False

        # Check valid performance
        try:
            self.performance_model = Performance.objects.get(pk=self.cleaned_data['performance'])
        except ObjectDoesNotExist:
            self.add_error('performance', "Ungültige Vorstellung!")
            return False

        # Check if enough tickets are available
        tickets_available = self.performance_model.tickets_available()
        booked_tickets = self.cleaned_data['number_of_tickets']
        if tickets_available < booked_tickets:
            self.add_error('performance', 'Vorstellung ist leider schon ausverkauft!')
            return False

        return valid
