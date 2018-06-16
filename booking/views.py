import string
import random
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views import generic, View
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from .forms import BookingForm
from .models import Performance, Booking, Ticket

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm


def confirmation(request, booking_code):
    try:
        booking = Booking.objects.get(code=booking_code)
        tickets = booking.ticket_set.all()
    except ObjectDoesNotExist:
        return render(request, 'booking/invalid_ticket_code.html')

    return render(
        request,
        'booking/confirmation.html',
        context={
            'current_view': 'booking',
            'booking': booking,
            'tickets': tickets
        }
    )


def create_code():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))


class BookingView(View):
    form_class = BookingForm
    template_name = "booking/booking_form.html"

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            context={
                'current_view': 'booking',
                'form': BookingForm()
            }
        )

    def post(self, request, *args, **kwargs):
        form = BookingForm(request.POST)
        if form.is_valid():
            # Prepare new booking
            booking = Booking(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                number_of_tickets=form.cleaned_data['number_of_tickets'],
                performance=form.performance_model,
                code=create_code()
            )
            booking.save()

            # Create the tickets
            tickets = []
            for i in range(booking.number_of_tickets):
                ticket = Ticket(
                    booking=booking,
                    code=create_code()
                )
                ticket.save()
                tickets.append(ticket)

            # Send confirmation mail
            subject = 'Ihre Bestellung'

            html_content = render_to_string('booking/mail.html', context={
                'request': request,
                'booking': booking,
                'tickets': tickets
            })
            text_content = strip_tags(html_content)

            message = EmailMultiAlternatives(
                'Ihre Bestellung',
                text_content,
                'tickets@localhost',
                [booking.email],
                headers={
                    'Message-ID': 'foo'
                }
            )
            message.attach_alternative(html_content, 'text/html')
            message.send()          # @todo Catch ConnectionRefusedError if mail server isn't answering!

            return HttpResponseRedirect(reverse('booking:confirmation', args=(booking.code,), ))
        else:
            return render(request, self.template_name, context={'form': form})


def pdf_view(request, ticket_code):
    try:
        ticket = Ticket.objects.get(code=ticket_code)
        booking = ticket.booking
    except ObjectDoesNotExist:
        return render(request, 'booking/invalid_ticket_code.html')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ticket.pdf"'

    p = Canvas(response, pagesize=(260*mm, 150*mm), pageCompression=1)
    image_path = 'booking/static/booking/ticket.png'
    image = ImageReader(image_path)
    p.drawImage(image, 0, 0, 260*mm, 150*mm, mask='auto')

    p.setFont('Times-Bold', 20)

    p.drawString(70*mm, 90*mm, '{},'.format(booking.last_name))
    p.drawString(70*mm, 80*mm, booking.first_name)

    p.drawString(165*mm, 90*mm, '{}'.format(booking.performance.title))
    p.drawString(165*mm, 80*mm, booking.performance.start_date)
    p.drawString(165*mm, 70*mm, booking.performance.start_time)

    p.setFont('Times-Bold', 24)
    p.drawString(192*mm, 18*mm, ticket.code)

    p.showPage()
    p.save()

    return response


class ServiceView(View):
    template_name = "booking/services.html"

    def get(self, request):
        performances = Performance.get_with_tickets_available()

        return render(
            request,
            self.template_name,
            context={
                'current_view': 'services',
                'performances': performances
            }
        )


class PolicyView(generic.TemplateView):
    template_name = "booking/policies.html"
    extra_context = {
        'current_view': '',
    }
