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
from django.apps import apps
import qrcode as qr
from .forms import BookingForm
from .models import Performance, Booking, Ticket

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import mm
from io import BytesIO


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
            'booking': booking,
            'tickets': tickets
        }
    )


def create_code():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))


def send_confirmation_mail(request, booking):
    # Send confirmation mail
    subject = 'Ihre Bestellung'

    html_content = render_to_string('booking/mail.html', context={
        'request': request,
        'booking': booking,
        'tickets': booking.ticket_set.all()
    })
    text_content = strip_tags(html_content)

    message = EmailMultiAlternatives(
        subject='Ihre Bestellung',
        body=text_content,
        to=[booking.email],
        headers={
            'Message-ID': 'foo'
        }
    )
    message.attach_alternative(html_content, 'text/html')

    # @todo Implement proper error handling
    try:
        message.send()
    except Exception:
        pass


class BookingView(View):
    form_class = BookingForm
    template_name = "booking/base.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        number_of_tickets_available_per_performance = []
        number_of_tickets_booked_total = 0
        number_of_tickets_available_total = 0
        for performance in Performance.objects.all():
            number_of_tickets_available_per_performance.append(performance.tickets_available())
            number_of_tickets_booked_total += performance.capacity - performance.tickets_available()
            number_of_tickets_available_total += performance.tickets_available()

        return render(
            request,
            self.template_name,
            context={
                'number_of_tickets_available_per_performance': number_of_tickets_available_per_performance,
                'number_of_tickets_booked_total': number_of_tickets_booked_total,
                'number_of_tickets_available_total': number_of_tickets_available_total,
                'form': form
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

            send_confirmation_mail(request, booking)

            return HttpResponseRedirect(reverse('booking:confirmation', args=(booking.code,)))
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

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont('ComicBd', 'booking/templates/booking/comicbd.ttf'))

    p = Canvas(response, pagesize=(260*mm, 150*mm), pageCompression=1)

    image_path = 'booking/templates/booking/ticket.png'

    image = ImageReader(image_path)
    p.drawImage(image, 0, 0, 260*mm, 150*mm, mask='auto')

    p.setFont('ComicBd', 20)

    p.drawString(70*mm, 90*mm, '{},'.format(booking.last_name))
    p.drawString(70*mm, 80*mm, booking.first_name)

    p.drawString(165*mm, 90*mm, '{}'.format(booking.performance.title))
    p.drawString(165*mm, 80*mm, booking.performance.start_date)
    p.drawString(165*mm, 70*mm, booking.performance.start_time)

    p.setFont('Times-Bold', 24)
    p.drawString(192*mm, 18*mm, ticket.code)

    if apps.get_app_config('booking').use_qr_codes:

        # Create QRcode
        qr_code = qr.QRCode(
            version=1,
            error_correction=qr.ERROR_CORRECT_L,
            box_size=3,
            border=4
        )

        verification_url = 'http://{}{}'.format(
            request.get_host(),
            reverse('booking:verify', args=(ticket_code,))
        )
        qr_code.add_data(verification_url)
        img = qr_code.make_image(fill_color="black", back_color="white")
        raw_img = BytesIO()
        img.save(raw_img, format='PNG')
        p.drawImage(ImageReader(raw_img), 210*mm, 35*mm, mask='auto')

    p.showPage()
    p.save()

    return response


class VerificationView(View):
    template_name = 'booking/verify.html'

    def get(self, request, ticket_code=None):
        if ticket_code is None:
            return render(request, self.template_name, context={'ticket': None, 'checkin_ok': False})
        try:
            ticket = Ticket.objects.get(code=ticket_code)
        except ObjectDoesNotExist:
            return render(request, self.template_name, context={'ticket': None, 'checkin_ok': False})

        ticket.check_in_flag = True
        ticket.save()

        return render(request, self.template_name, context={'ticket': ticket, 'checkin_ok': True})


class ResendConfirmationMail(View):

    def get(self, request, booking_code):
        try:
            booking = Booking.objects.get(code=booking_code)
            send_confirmation_mail(request, booking)
            return HttpResponseRedirect(reverse('booking:confirmation', args=(booking.code,), ) + '#order_confirmation')
        except ObjectDoesNotExist:
            return render(request, 'booking/invalid_ticket_code.html')
